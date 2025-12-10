"""Main Chainlit application for the Ableton Producer Agent system.

This module creates the main Chainlit chat interface that integrates with
the multi-agent system (Router, Producer, Assistant) to provide an intelligent
music production assistant.
"""

import os

import chainlit as cl
from loguru import logger

from src.agents.producer_agent import create_producer_agent


@cl.on_chat_start
async def on_chat_start():
    """Initialize a new chat session."""
    welcome_message = """🎵 **Welcome to the Ableton Producer Agent!** 🎵

Ready to make some music? 🎶"""

    await cl.Message(content=welcome_message).send()


def format_todos_to_markdown(todos):
    md_lines = ["### Current Plan"]
    status_map = {
        "pending": "⚪",
        "in_progress": "Hz",  # Using a spinner or distinct icon
        "completed": "✅",
        "failed": "XY",
    }

    for todo in todos:
        icon = status_map.get(todo.get("status"), "⚪")
        content = todo.get("content", "")
        if todo.get("status") == "in_progress":
            content = f"**{content}**"
        md_lines.append(f"{icon} {content}")

    return "\n".join(md_lines)


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming user messages."""
    producer_agent = await create_producer_agent()

    with cl.Step(name="AbletonMCP", type="run", language="json") as tool_calls:
        plan_message = cl.Message(content="Gathering plan...")
        await plan_message.send()
        async for _, graph_step in producer_agent.astream(
            {"messages": message.content}, stream_mode="updates", subgraphs=True
        ):
            node_name, update = next(iter(graph_step.items()))
            if update is None:
                continue

            logger.info(f"Update for node {node_name}: {update}")
            match node_name:
                case "tools":
                    if "todos" in update and update.get("todos"):
                        logger.debug("Updating plan message with new todos.")
                        plan_md = format_todos_to_markdown(todos=update["todos"])
                        await plan_message.remove()
                        plan_message = cl.Message(content=plan_md)
                        await plan_message.send()

                    if "messages" in update and update.get("messages"):
                        logger.debug("Streaming final message update.")
                        last_msg = update["messages"][-1]
                        if last_msg.content:
                            await tool_calls.stream_token(last_msg.content + "\n")
            await tool_calls.update()


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print(
            "⚠️  Warning: OPENAI_API_KEY not set. Please set it before running the app."
        )
        print("   export OPENAI_API_KEY='your-api-key'")

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ℹ️  Note: ANTHROPIC_API_KEY not set (optional, for Claude models)")

    print("🎵 Starting Ableton Producer Agent...")
    print("📝 Open your browser to http://localhost:8000 when the server starts")
