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
    welcome_message = """## Welcome to the Ableton Producer Agent! 💃🕺 

Ready to make some music? 🎶"""

    await cl.Message(content=welcome_message).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming user messages."""
    producer_agent = await create_producer_agent()

    with cl.Step(name="AbletonMCP", type="run", language="json") as tool_steps:
        answer_message = cl.Message(content="")
        await answer_message.send()
        async for event_type, event_value in producer_agent.astream(
            {"messages": message.content},
            config={"configurable": {"thread_id": cl.context.session.id}},
            stream_mode=["updates", "messages"],
        ):
            if event_type == "messages":
                chunk, _ = event_value
                if isinstance(chunk, AIMessageChunk):
                    if isinstance(chunk.content, str):
                        await answer_message.stream_token(chunk.content)
                        await answer_message.update()
                    elif isinstance(chunk.content, list):
                        for item in chunk.content:
                            if item.get("type") == "text":
                                await answer_message.stream_token(item.get("text", ""))
                                await answer_message.update()

            if event_type == "updates":
                node_name, update = next(iter(event_value.items()))  # type: ignore[arg]

                logger.info(f"Update for node {node_name}: {update}")
                match node_name:
                    case "tools":
                        if "messages" in update and update.get("messages"):
                            last_msg = update["messages"][-1]
                            if last_msg.content:
                                await tool_steps.stream_token(last_msg.content + "\n")

                        if "todos" in update and update.get("todos"):
                            for todo in update["todos"]:
                                await tool_steps.stream_token(
                                    f"{todo.get('content')}: {todo.get('status')}\n"
                                )

                await tool_steps.update()
