"""Main Chainlit application for the Ableton Producer Agent system.

This module creates the main Chainlit chat interface that integrates with
the multi-agent system (Router, Producer, Assistant) to provide an intelligent
music production assistant.
"""

import chainlit as cl
from langchain.messages import AIMessageChunk
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
        answer_message = cl.Message(content="")
        await answer_message.send()
        async for event_type, event_value in producer_agent.astream(
            {"messages": message.content},
            config={"configurable": {"thread_id": cl.context.session.id}},
            stream_mode=["updates", "messages"],
        ):
            if event_type == "messages":
                chunk = event_value[0]
                if isinstance(chunk, AIMessageChunk):
                    await answer_message.stream_token(chunk.content)  # type: ignore[arg]
                    await answer_message.update()

            elif event_type == "updates":
                node_name, update = next(iter(event_value.items()))  # type: ignore[arg]

                logger.info(f"Update for node {node_name}: {update}")
                match node_name:
                    case "tools":
                        if "messages" in update and update.get("messages"):
                            last_msg = update["messages"][-1]
                            if last_msg.content:
                                await tool_calls.stream_token(last_msg.content + "\n")

                        # if "todos" in update and update.get("todos"):
                        #     plan_md = format_todos_to_markdown(todos=update["todos"])
                        #     plan_message = cl.Message(content=plan_md)
                        #     await plan_message.send()

                await tool_calls.update()
