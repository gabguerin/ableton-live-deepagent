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
            name="composer",
            prompt_file="src/prompts/COMPOSER_ADVISOR_PROMPT.md",
            description=(
                "Agent specialized in overall song structure and arrangement. "
                "Decides on which tracks to create and their roles across all genres."
            ),
        ),
        AdvisorInfo(
            name="drums",
            prompt_file="src/prompts/DRUMS_ADVISOR_PROMPT.md",
            description=(
                "Agent specialized in drum programming and rhythmic patterns. "
                "Creates kick, snare, hi-hat, and percussion patterns across all genres."
            ),
        ),
        AdvisorInfo(
            name="harmony",
            prompt_file="src/prompts/HARMONY_ADVISOR_PROMPT.md",
            description=(
                "Agent specialized in harmonic content and foundation. "
                "Creates chord progressions, bass lines, and harmonic support across all genres."
            ),
        ),
        AdvisorInfo(
            name="leads",
            prompt_file="src/prompts/LEADS_ADVISOR_PROMPT.md",
            description=(
                "Agent specialized in melodic leads and featured parts. "
                "Creates lead lines, solos, and melodic content across all genres."
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
