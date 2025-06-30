# SlackBolt Langflow Bot

A powerful Slack bot built with Slack Bolt that integrates with Langflow to provide AI-powered conversation capabilities. This bot can handle direct messages, thread conversations, and file processing through a customizable Langflow workflow.

## Features

- **Direct Message Support**: Responds to direct messages automatically
- **Thread Conversation Handling**: Maintains context in threaded conversations
- **File Processing**: Can process and analyze uploaded files (including PDFs)
- **Mention Detection**: Responds when mentioned in channels
- **User Welcome Messages**: Automatically welcomes new users to channels
- **Context Awareness**: Maintains conversation history for better responses
- **Reaction Feedback**: Provides visual feedback with emoji reactions

## Architecture

The bot consists of two main components:

1. **Slack Bot (`slackbot.py`)**: Handles Slack events and communication
2. **Langflow Integration**: Processes messages through a customizable AI workflow

### Key Components

- `slackbot.py`: Main bot logic and Slack event handlers
- `run.py`: Entry point for running the bot
- `Magic Summarizer Bot Flow.json`: Langflow workflow configuration
- `bot_envs/`: Environment configuration files

## Prerequisites

- Python 3.7+
- Slack App with appropriate permissions
- Langflow instance running locally or remotely
- OpenAI API key (configured in Langflow)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd slackbolt-langflow-bot
   ```

2. **Install Langflow**:
   ```bash
   pip install langflow
   ```

3. **Install bot dependencies**:
   ```bash
   pip install slack-bolt httpx requests python-dotenv
   ```

4. **Set up environment variables**:
   ```bash
   cp bot_envs/.env_sample bot_envs/.env_your_bot_name
   ```

5. **Configure your environment file**:
   Edit `bot_envs/.env_your_bot_name` with your Slack app credentials:
   ```
   SLACK_BOT_TOKEN = 'xoxb-your-bot-token'
   SLACK_APP_TOKEN = 'xapp-your-app-token'
   SLACK_SIGNING_SECRET = 'your-signing-secret'
   LANGFLOW_FLOW_ID = 'your-langflow-flow-id'
   ```

## Slack App Setup

1. Create a new Slack app at [api.slack.com/apps](https://api.slack.com/apps)
2. Configure the following OAuth scopes:
   - `channels:history`
   - `channels:read`
   - `chat:write`
   - `files:read`
   - `groups:history`
   - `groups:read`
   - `im:history`
   - `im:read`
   - `mpim:history`
   - `mpim:read`
   - `reactions:write`
   - `users:read`
   - `users:read.email`

3. Enable Socket Mode in your app settings
4. Install the app to your workspace
5. Copy the required tokens to your environment file

## Langflow Setup

1. **Install and run Langflow**:
   ```bash
   pip install langflow
   langflow run
   ```

2. **Import the workflow**:
   - Open Langflow at `http://localhost:7860`
   - Import the `Magic Summarizer Bot Flow.json` file
   - Note the Flow ID for your environment configuration

3. **Configure the workflow**:
   - Set up your OpenAI API key in the workflow
   - Customize the prompt and processing logic as needed

## Usage

### Running the Bot

1. **Start Langflow** (if not already running):
   ```bash
   langflow run
   ```

2. **Run the bot**:
   ```bash
   python run.py
   ```

### Bot Interactions

- **Direct Messages**: Send any message to the bot in a DM
- **Mentions**: Mention the bot in any channel with `@your-bot-name`
- **Threads**: The bot will maintain context in threaded conversations
- **File Uploads**: Upload files for the bot to process and analyze

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SLACK_BOT_TOKEN` | Your Slack bot token (starts with `xoxb-`) | Yes |
| `SLACK_APP_TOKEN` | Your Slack app token (starts with `xapp-`) | Yes |
| `SLACK_SIGNING_SECRET` | Your Slack app signing secret | Yes |
| `LANGFLOW_FLOW_ID` | The ID of your Langflow workflow | Yes |

### Multiple Bot Instances

You can run multiple bot instances by creating different environment files:

```bash
# Create environment for different bots
cp bot_envs/.env_sample bot_envs/.env_bot1
cp bot_envs/.env_sample bot_envs/.env_bot2

# Modify run.py to use different environment files
```

## Development

### Project Structure

```
slackbolt-langflow-bot/
├── slackbot.py              # Main bot logic
├── run.py                   # Entry point
├── bot_envs/                # Environment configurations
│   ├── .env_sample         # Template environment file
│   └── .env_*              # Bot-specific environment files
├── Magic Summarizer Bot Flow.json  # Langflow workflow
└── README.md               # This file
```

### Key Classes and Methods

- `SlackBot`: Main bot class handling Slack events
- `on_message()`: Handles incoming messages
- `respond_to_message()`: Processes messages through Langflow
- `process_thread_history()`: Maintains conversation context

### Customizing the Workflow

1. Open the Langflow workflow in the Langflow UI
2. Modify the prompt templates and processing logic
3. Export the updated workflow
4. Replace the `Magic Summarizer Bot Flow.json` file

## Troubleshooting

### Common Issues

1. **Bot not responding**:
   - Check that Langflow is running on `http://localhost:7860`
   - Verify your Slack app tokens are correct
   - Ensure the bot has been invited to the channel

2. **Permission errors**:
   - Verify all required OAuth scopes are enabled
   - Check that the bot has been properly installed to your workspace

3. **Langflow connection issues**:
   - Ensure Langflow is running and accessible
   - Verify the Flow ID is correct
   - Check that the workflow is properly configured

### Logging

The bot uses Python's logging module. To enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions:
- Check the troubleshooting section above
- Review Slack API documentation
- Consult Langflow documentation
- Open an issue in the repository