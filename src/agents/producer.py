"""Producer Agent - Deep agent for complex music production tasks.

This module implements a sophisticated music producer agent using LangChain's
deep agents framework. The agent provides:
- Music theory and composition guidance
- Sound design and synthesis advice
- Mixing and mastering techniques
- Creative workflow optimization
- Context-aware planning and memory management
- Genre-aware dynamic musician agent selection
"""

from deepagents import CompiledSubAgent, SubAgent, create_deep_agent
from langgraph.graph.state import CompiledStateGraph

from src.ableton_tools import load_ableton_tools
from src.agents.musician import MusicianInfo, create_musician
from src.settings import SETTINGS


async def create_producer_agent() -> CompiledStateGraph:
    """Create and initialize a Producer Agent with dynamic musician subagents."""
    with open("src/prompts/PRODUCER_PROMPT.md", "r") as f:
        system_prompt = f.read()

    tools = await load_ableton_tools(exclude=["add_notes_to_clip"])

    music_band = await _create_music_band()

    return create_deep_agent(
        model=SETTINGS.model_name,
        system_prompt=system_prompt,
        tools=tools,
        subagents=music_band,
    )


async def _create_music_band() -> list[CompiledSubAgent | SubAgent]:
    musicians = [
        MusicianInfo(
            name="drummer",
            prompt_file="src/prompts/DRUMMER_PROMPT.md",
            description=(
                "Agent specialized in drum programming and rhythmic patterns. "
                "Creates kick, snare, hi-hat, and percussion patterns across all genres."
            ),
        ),
        MusicianInfo(
            name="bassist",
            prompt_file="src/prompts/BASSIST_PROMPT.md",
            description=(
                "Agent specialized in bass lines and low-end foundation. "
                "Creates walking bass, funk patterns, and harmonic support across all genres."
            ),
        ),
        MusicianInfo(
            name="pianist",
            prompt_file="src/prompts/PIANIST_PROMPT.md",
            description=(
                "Agent specialized in piano/keyboard parts and harmonic content. "
                "Creates chord progressions, comping patterns, and harmonic sophistication."
            ),
        ),
        MusicianInfo(
            name="guitarist",
            prompt_file="src/prompts/GUITARIST_PROMPT.md",
            description=(
                "Agent specialized in guitar parts and melodic content. "
                "Creates rhythm guitar, lead lines, and melodic embellishments."
            ),
        ),
    ]

    music_band = []
    for musician_config in musicians:
        agent = await create_musician(
            musician_info=musician_config,
        )
        music_band.append(agent)

    return music_band
