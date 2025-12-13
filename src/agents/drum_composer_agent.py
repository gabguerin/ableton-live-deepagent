"""Drum Composer Agent module.

This module provides the drum composer subagent specialized in rhythm and
percussion programming with access to the add_notes_to_clip tool.
"""

from deepagents import CompiledSubAgent
from langchain.agents import create_agent

from src.ableton_tools import load_ableton_tools
from src.settings import SETTINGS


async def create_drum_composer_subagent() -> CompiledSubAgent:
    """Create drum composer subagent with only add_notes_to_clip tool."""
    with open("src/prompts/DRUM_COMPOSER_PROMPT.md", "r") as f:
        system_prompt = f.read()

    tools = await load_ableton_tools(include=["add_notes_to_clip"])

    agent = create_agent(
        model=SETTINGS.model_name,
        system_prompt=system_prompt,
        tools=tools,
    )

    return CompiledSubAgent(
        name="drum-composer-agent",
        description="Agent specialized in drum programming and rhythmic patterns. Creates kick, snare, hi-hat, and percussion patterns across all genres.",
        runnable=agent,
    )
