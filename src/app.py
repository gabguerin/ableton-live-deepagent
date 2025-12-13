"""Main Chainlit application for the Ableton Producer Agent system.

This module creates the main Chainlit chat interface that integrates with
the multi-agent system (Router, Producer, Assistant) to provide an intelligent
music production assistant.
"""

import chainlit as cl
from loguru import logger

from src.agents.producer import create_producer_agent


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
        "in_progress": "⏳",
        "completed": "✅",
        "failed": "❌",
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
        answer_message = cl.Message(content="")
        await plan_message.send()
        async for _, graph_step in producer_agent.astream(
            {"messages": message.content}, stream_mode="updates", subgraphs=True
        ):
            node_name, update = next(iter(graph_step.items()))  # type: ignore
            if update is None:
                continue

            logger.info(f"Update for node {node_name}: {update}")
            match node_name:
                case "tools":
                    if "todos" in update and update.get("todos"):
                        logger.debug("Updating plan message with new todos.")
                        plan_md = format_todos_to_markdown(todos=update["todos"])
                        plan_message.content = ""
                        await plan_message.update()
                        await plan_message.stream_token(plan_md)

                    if "messages" in update and update.get("messages"):
                        logger.debug("Streaming final message update.")
                        last_msg = update["messages"][-1]
                        if last_msg.content:
                            await tool_calls.stream_token(last_msg.content + "\n")
                            await tool_calls.update()
                case "messages":
                    if update.get("content"):
                        logger.debug("Streaming final message update.")
                        await answer_message.stream_token(update["content"] + "\n")
                        await answer_message.update()
