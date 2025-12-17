"""Producer Agent - Deep agent for complex music production tasks.

This module implements a sophisticated music producer agent using LangChain's
deep agents framework. The agent provides:
- Music theory and composition guidance
- Sound design and synthesis advice
- Mixing and mastering techniques
- Creative workflow optimization
- Context-aware planning and memory management
- Genre-aware dynamic advisor agent selection
"""

from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph

from src.ableton_tools import load_ableton_tools
from src.agents.composer import create_composer
from src.settings import SETTINGS


async def create_producer_agent(checkpointer: InMemorySaver) -> CompiledStateGraph:
    """Create and initialize a Producer Agent with dynamic advisor subagents."""
    with open("src/prompts/PRODUCER.md", "r") as f:
        system_prompt = f.read()

    tools = await load_ableton_tools()

    composer = await create_composer()

    return create_deep_agent(
        model=SETTINGS.producer_model,
        system_prompt=system_prompt,
        tools=tools,
        subagents=[composer],
        checkpointer=checkpointer,
    )
