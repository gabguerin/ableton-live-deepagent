"""Producer Agent - Deep agent for complex music production tasks.

This module implements a sophisticated music producer agent using LangChain's
deep agents framework. The agent provides:
- Music theory and composition guidance
- Sound design and synthesis advice
- Mixing and mastering techniques
- Creative workflow optimization
- Context-aware planning and memory management
"""

from deepagents import create_deep_agent
from langgraph.graph.state import CompiledStateGraph

from src.ableton_tools import load_ableton_tools
from src.agents.drum_composer_agent import create_drum_composer_subagent
from src.agents.melody_composer_agent import create_melody_chord_composer_subagent
from src.settings import SETTINGS


async def create_producer_agent() -> CompiledStateGraph:
    """Create and initialize a Producer Agent."""
    with open("src/prompts/MELODY_CHORD_COMPOSER_PROMPT.md", "r") as f:
        system_prompt = f.read()

    tools = await load_ableton_tools(exclude=["add_notes_to_clip"])

    drum_composer_subagent = await create_drum_composer_subagent()
    melody_chord_composer_subagent = await create_melody_chord_composer_subagent()

    return create_deep_agent(
        model=SETTINGS.model_name,
        system_prompt=system_prompt,
        tools=tools,
        subagents=[
            drum_composer_subagent,
            melody_chord_composer_subagent,
        ],
    )
