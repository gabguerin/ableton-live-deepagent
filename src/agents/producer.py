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

from deepagents import CompiledSubAgent, SubAgent, create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph

from src.ableton_tools import load_ableton_tools
from src.agents.advisor import AdvisorInfo, create_advisor
from src.settings import SETTINGS


async def create_producer_agent() -> CompiledStateGraph:
    """Create and initialize a Producer Agent with dynamic advisor subagents."""
    with open("src/prompts/PRODUCER_PROMPT.md", "r") as f:
        system_prompt = f.read()

    tools = await load_ableton_tools()

    advisors = await _create_advisors()

    return create_deep_agent(
        model=SETTINGS.model,
        system_prompt=system_prompt,
        tools=tools,
        subagents=advisors,
        checkpointer=InMemorySaver(),
    )


async def _create_advisors() -> list[CompiledSubAgent | SubAgent]:
    advisors = [
        AdvisorInfo(
            name="musical_advisor",
            prompt_file="src/prompts/MUSICAL_ADVISOR_PROMPT.md",
            description=(
                "Agent specialized in any musical aspect. "
                "Can provide comprehensive musical guidance about tracks composition, drum patterns, chord progressions, and more."
            ),
        ),
    ]

    music_band = []
    for advisor_config in advisors:
        agent = await create_advisor(
            advisor_info=advisor_config,
        )
        music_band.append(agent)

    return music_band
