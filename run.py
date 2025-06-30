#!/usr/bin/env python3
import logging
logger = logging.getLogger(__name__)

import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

this_file_folder = os.path.dirname(os.path.realpath(__file__))
parent_folder = os.path.dirname(this_file_folder)

load_dotenv(Path(parent_folder) / Path(this_file_folder) / "bot_envs/.env_findmycoder_magic_summarizer_bot")

from slackbot import slack_bot


async def main():
    await slack_bot.start()

if __name__ == "__main__":
    asyncio.run(main())