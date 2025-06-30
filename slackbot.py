#!/usr/bin/env python3
import logging
import json
import httpx
import requests

logger = logging.getLogger(__name__)

import os
import re
import time
from typing import List

# from langchain import OpenAI
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp
from slack_sdk.errors import SlackApiError

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get('SLACK_APP_TOKEN')
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
LANGFLOW_FLOW_ID = os.environ.get("LANGFLOW_FLOW_ID")


class SlackBot:
    def __init__(self, slack_app: AsyncApp):
        self.threads_bot_is_participating_in = {}
        self.app = slack_app
        self.client = self.app.client
        self.id_to_name_cache = {}
        self.user_id_to_info_cache = {}

    async def start(self):
        logger.info("Looking up bot user_id. (If this fails, something is wrong with the auth)")
        response = await self.app.client.auth_test()
        self.bot_user_id = response["user_id"]
        self.bot_user_name = await self.get_username_for_user_id(self.bot_user_id)
        logger.info("Bot user id: "+ self.bot_user_id)
        logger.info("Bot user name: "+ self.bot_user_name)

        await AsyncSocketModeHandler(app, SLACK_APP_TOKEN).start_async()

    async def get_user_info_for_user_id(self, user_id):
        user_info = self.user_id_to_info_cache.get(user_id, None)
        if user_info is not None:
            return user_info

        user_info_response = await self.app.client.users_info(user=user_id)
        user_info = user_info_response['user']
        logger.debug(user_info)
        self.user_id_to_info_cache[user_id] = user_info
        return user_info

    async def get_username_for_user_id(self, user_id):
        user_info = await self.get_user_info_for_user_id(user_id)
        profile = user_info['profile']
        ret_val = profile['real_name']
        return ret_val

    async def translate_mentions_to_names(self, text):
        # Replace every @mention of a user id with their actual name:
        # First, use a regex to find @mentions that look like <@U123456789>:
        matches = re.findall(r"<@(U[A-Z0-9]+)>", text)
        for match in matches:
            mention_string = f"<@{match}>"
            mention_name = await self.get_username_for_user_id(match)
            if mention_name is not None:
                text = text.replace(mention_string, "@"+mention_name)

        return text

    async def confirm_message_received(self, channel, thread_ts, message_ts, user_id_of_sender):
        # React to the message with a thinking face emoji:
        try:
            print('Adding thinking face to message')
            await self.client.reactions_add(channel=channel, name="thinking_face", timestamp=message_ts)
        except Exception as e:
            logger.exception(e)

    async def respond_to_message(self, channel_id, thread_ts, message_ts, user_id, message_text, thread_history=None, message_files=None):
        try:
            print('Responding to message')
            message_text = await self.translate_mentions_to_names(message_text)
            processed_thread_history = None if thread_history is None else await self.process_thread_history(thread_history, as_text=True)
            langflow_payload = {
                "user_message": message_text,
                "thread_history": "" if processed_thread_history is None else processed_thread_history,
                "files": "" if message_files is None else json.dumps(message_files),
                "slack_bot_token": SLACK_BOT_TOKEN,
                "channel_id": channel_id,
                "thread_ts": thread_ts
            }
            print(langflow_payload)
            url = "http://127.0.0.1:7860/api/v1/run/{}?stream=false".format(LANGFLOW_FLOW_ID)

            payload = json.dumps({
              "input_value": json.dumps(langflow_payload),
              "input_type": "any",
              "output_type": "any"
            })
            headers = {
              'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)
        except Exception as e:
            response = f":exclamation::exclamation::exclamation: Error: {e}"
            logger.exception(response)
            await self.client.chat_postMessage(channel=channel_id, text=response, thread_ts=thread_ts, mrkdwn=True)

    async def get_thread_history_and_bot_response(self, channel_id, message_ts, thread_ts):
        thread_history, has_bot_responded_in_thread = None, False
        if not message_ts == thread_ts: #This is not the first message in the thread
            thread_history = await self.client.conversations_replies(channel=channel_id, ts=thread_ts)
            message_history = thread_history.data['messages']
            message_history = message_history[:-1]
            for message in message_history:
                if message['user'] == self.bot_user_id:
                    has_bot_responded_in_thread = True
                    break
        return thread_history, has_bot_responded_in_thread

    async def process_thread_history(self, thread_history, as_text=False):
        processed_history = []
        message_history = thread_history.data['messages']
        message_history = message_history[:-1] # Get rid of the last message from the histroy since it's the message we're responding to:
        for message in message_history:
            text = message['text']
            text = await self.translate_mentions_to_names(text)
            user_id = message['user']
            user_name = await self.get_username_for_user_id(user_id)
            if (user_id == self.bot_user_id):
                processed_history.append(["bot", text])
            else:
                processed_history.append([f"{user_name}",  text])
        if as_text:
          processed_history = '\n'.join(["{}: {}".format(v[0], v[1]) for v in processed_history]) if processed_history else 'No thread history found'
        return processed_history

    async def on_message(self, event, say):
        print(event)
        message_ts = event['ts']
        thread_ts = event.get('thread_ts', message_ts)
        channel_type = event.get('channel_type', None)
        channel_id = event.get('channel', None)
        message_text = event.get('text', None)
        message_files = event.get('files', None)
        user_id = event.get('user', None)
        subtype = event.get('subtype', None)
        is_bot_mentioned = f"<@{self.bot_user_id}>" in message_text
        thread_history, has_bot_responded_in_thread = await self.get_thread_history_and_bot_response(channel_id, message_ts, thread_ts)
        print(channel_type, is_bot_mentioned, has_bot_responded_in_thread, subtype, message_text)
        try:
            # {'client_msg_id': '7e605650-8b39-4f61-99c5-795a1168fb7c', 'type': 'message', 'text': 'Hi there Chatterbot', 'user': 'U024LBTMX', 'ts': '1679289332.087509', 'blocks': [{'type': 'rich_text', 'block_id': 'ins/', 'elements': [{'type': 'rich_text_section', 'elements': [{'type': 'text', 'text': 'Hi there Chatterbot'}]}]}], 'team': 'T024LBTMV', 'channel': 'D04V265MYEM', 'event_ts': '1679289332.087509', 'channel_type': 'im'}

            logger.info(f"Received message event: {event}")
            # At first I thought we weren't told about our own messages, but I don't think that's true. Let's make sure we aren't hearing about our own:
            if event.get('user', None) == self.bot_user_id:
                logger.debug("Not handling message event since I sent the message.")
                return

            if subtype and not subtype in ['message', 'file_share']:
                print('Reached this portion')
                logger.debug("Not handling message event since this message is already processed")
                return

            # If this is a direct message, or if the message mentions us or bot has already responded in the thread, we should be participating if we are not already
            if (channel_type and channel_type == "im") or is_bot_mentioned or has_bot_responded_in_thread:
                await self.confirm_message_received(channel_id, thread_ts, message_ts, user_id)
                await self.respond_to_message(channel_id, thread_ts, message_ts, user_id, message_text, thread_history, message_files)

        except Exception as e:
            response = f":exclamation::exclamation::exclamation: Error: {e}"
            logger.exception(response)
            await say(text=response, thread_ts=thread_ts)

    async def on_member_joined_channel(self, event_data):
        # Get user ID and channel ID from event data
        user_id = event_data["user"]
        channel_id = event_data["channel"]

        user_info = await self.get_user_info_for_user_id(user_id)
        username = await self.get_username_for_user_id(user_id)
        profile = user_info.get("profile", {})
        llm_gpt3_turbo = OpenAI(temperature=1, model_name="gpt-3.5-turbo", request_timeout=30, max_retries=5, verbose=True)

        # TODO: Extract into yaml file instead:
        welcome_message = (await llm_gpt3_turbo.agenerate([f"""
You are a funny and creative slackbot {self.bot_user_name}
Someone just joined a Slack channel you are a member of, and you want to welcome them creatively and in a way that will make them feel special.
You are VERY EXCITED about someone joining the channel, and you want to convey that!
Their username is {username}, but when you mention their username, you should say "<@{user_id}>" instead.
Their title is: {profile.get("title")}
Their current status: "{profile.get("status_emoji")} {profile.get("status_text")}"
Write a slack message, formatted in Slack markdown, that encourages everyone to welcome them to the channel excitedly.
Use emojis. Maybe write a song. Maybe a poem.

Afterwards, tell the user that you look forward to "chatting" with them, and tell them that they can just mention <@{self.bot_user_id}> whenever they want to talk.
"""])).generations[0][0].text
        if welcome_message:
          try:
            # Send a welcome message to the user
            await self.client.chat_postMessage(channel=channel_id, text=welcome_message)
          except e:
            logger.exception("Error sending welcome message")


app = AsyncApp(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
client = app.client
slack_bot = SlackBot(app)

@app.event("message")
async def on_message(payload, say):
    logger.info("Processing message...")
    print("Processing message...")
    await slack_bot.on_message(payload, say)

# Define event handler for user joining a channel
@app.event("member_joined_channel")
async def handle_member_joined_channel(event_data):
    logger.info("Processing member_joined_channel event", event_data)
    await slack_bot.on_member_joined_channel(event_data)

@app.event('reaction_added')
async def on_reaction_added(payload):
    logger.info("Ignoring reaction_added")

@app.event('reaction_removed')
async def on_reaction_removed(payload):
    logger.info("Ignoring reaction_removed")

@app.event('app_mention')
async def on_app_mention(payload, say):
    logger.info("Ignoring app_mention in favor of handling it via the message handler...")
