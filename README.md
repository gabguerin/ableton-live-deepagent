# Ableton Producer Agent

An intelligent music production assistant using LangChain v1+ and deepagents for creative workflows with Ableton Live.

## Architecture

- **Producer Agent**: Deep agent powered by deepagents framework for complex music production tasks
- **Musical Advisor Subagent**: Specialized composer for musical guidance (chord progressions, arrangements, theory)
- **MCP Integration**: Direct connection to Ableton Live via Model Context Protocol (MCP)
- **Chainlit Interface**: Modern chat-based UI with streaming responses

## Quick Start

### Prerequisites
- Ableton Live (with ableton-mcp package installed)
- Python 3.11+
- uv package manager

### Installation

1. Clone and install dependencies:
```bash
git clone <repository-url>
cd ableton-producer-agent
make install
```

2. Set up environment variables (copy .env.example to .env):
```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
```bash
# LLM Provider (choose one)
LLM_PROVIDER=openai     # Options: openai, anthropic, google, mistral
PRODUCER_MODEL_NAME=gpt-5.2      # Model for the main producer agent
COMPOSER_MODEL_NAME=gpt-5-nano   # Model for the musical composer subagent
MODEL_TEMPERATURE=1.0   # Look for recommended temperature in the provider's documentation

# API Keys (configure based on your chosen provider)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
MISTRAL_API_KEY=your_mistral_api_key_here
```

3. Start the application:
```bash
make start
```

The app will launch at `http://localhost:8000` with auto-browser opening.

## Project Structure

```
src/
├── app.py              # Chainlit application entry point
├── settings.py         # Environment-based configuration
├── ableton_tools.py    # MCP tool loading and filtering
├── models.py           # Pydantic models and schemas
├── agents/
│   ├── producer.py     # Main producer agent with checkpointing
│   └── composer.py     # Musical advisor subagent factory
└── prompts/
    ├── PRODUCER.md     # Producer agent system prompt
    └── COMPOSER.md     # Musical advisor system prompt
```

## Features

- **Multi-LLM Support**: Compatible with OpenAI, Anthropic, Google, and Mistral models
- **Deep Agent Architecture**: Uses deepagents framework for sophisticated reasoning
- **Persistent Memory**: LangGraph checkpointing for conversation continuity
- **Real-time Streaming**: Live response streaming via Chainlit
- **MCP Integration**: Direct Ableton Live control through Model Context Protocol
- **Subagent System**: Specialized musical advisors for composition tasks
- **Environment Configuration**: Flexible settings via .env files

## Development

### Commands

- `make start` - Launch production-like server with auto-open
- `make install` - Install/sync dependencies via uv
- `make help` - Show available commands

### Configuration

The application uses environment-based configuration via `src/settings.py`. All settings can be configured through environment variables or `.env` file.

## MCP Integration

This project uses the `ableton-mcp` package to communicate with Ableton Live. The MCP tools are loaded dynamically and provide capabilities like:

- Session and track management
- MIDI clip creation and editing
- Instrument and effect loading
- Playback control
- Browser navigation

## Architecture Notes

The current architecture uses a simplified single-agent approach with subagents, rather than the traditional multi-agent router pattern. This provides better coherence and memory management for music production workflows.