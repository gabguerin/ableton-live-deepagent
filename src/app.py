"""Main Chainlit application for the Ableton Producer Agent system.

This module creates the main Chainlit chat interface that integrates with
the multi-agent system (Router, Producer, Assistant) to provide an intelligent
music production assistant.
"""

import uuid

import chainlit as cl
from langchain.messages import AIMessageChunk, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from loguru import logger

from src.agents.producer import create_producer_agent

STATUS_ICONS = {
    "pending": "⏳",
    "in_progress": "🔄",
    "completed": "✅",
    "failed": "❌",
}

THREAD_ID = uuid.uuid4().hex
checkpointer = InMemorySaver()


@cl.on_chat_start
async def on_chat_start():
    """Initialize a new chat session."""
    welcome_message = """## Welcome to the Ableton Producer Agent! 💃🕺 

#### Ready to make some music? 🎶"""

    await cl.Message(content=welcome_message).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming user messages."""
    logger.info(f"Started new chat session with THREAD_ID: {THREAD_ID}")

    producer_agent = await create_producer_agent(checkpointer=checkpointer)

    with cl.Step(name="AbletonMCP", type="run", language="json") as tool_steps:
        answer_message = cl.Message(content="")
        await answer_message.send()

        todo_text = cl.Text(name="📋 Todo list", content="Creating plan...")
        todo_list = cl.Message(content="", elements=[todo_text])
        await todo_list.send()
        async for event_type, event_value in producer_agent.astream(
            {"messages": [HumanMessage(content=message.content)]},
            config={"configurable": {"thread_id": THREAD_ID}},
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
                        if "todos" in update and update.get("todos"):
                            todo_content = ""
                            for todo in update["todos"]:
                                status_icon = STATUS_ICONS[
                                    todo.get("status", "pending")
                                ]
                                content = todo.get("content", "No description")
                                todo_content += f"{status_icon} {content}\n"

                            await todo_list.remove()
                            todo_text = cl.Text(
                                name="📋 Todo list", content=todo_content
                            )
                            todo_list = cl.Message(content="", elements=[todo_text])
                            await todo_list.send()

                        if "messages" in update and update.get("messages"):
                            last_msg = update["messages"][-1]
                            await tool_steps.stream_token(f'"{last_msg.name}":\n')
                            if last_msg.content:
                                await tool_steps.stream_token(last_msg.content + "\n")

                await tool_steps.update()
