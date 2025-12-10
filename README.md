# Ableton Producer Agent

A multi-agent system using LangChain v1+ for intelligent music production workflows with Ableton Live.

## Architecture

- **Router Agent**: LangGraph-based intelligent routing between agents
- **Producer Agent**: Deep agent for complex creative tasks (melody generation, harmonies, arrangements)
- **Assistant Agent**: Standard agent for simple Ableton operations (play, stop, mute, volume)
- **MCP Integration**: Connected to Ableton-MCP tools via uvx

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export OPENAI_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"
```

3. Run the application:
```bash
python src/main.py
```

## Project Structure

```
src/
├── router/       # LangGraph routing logic
├── agents/       # Producer and Assistant agents
├── mcp/          # Ableton-MCP integration
└── utils/        # Shared utilities
```

## Features

- **Intelligent Routing**: LLM classifies tasks by complexity
- **Creative Tools**: Generate melodies, harmonies, and arrangements
- **Simple Controls**: Transport, track management, parameter control
- **Persistent State**: LangGraph checkpointing for complex workflows
- **Streaming**: Real-time feedback for long-running tasks