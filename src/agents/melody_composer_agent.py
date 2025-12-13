"""Melody & Chord Composer Agent module.

This module provides the melody and chord composer subagent specialized in
harmony and melodic sophistication with access to the add_notes_to_clip tool.
"""

from deepagents import CompiledSubAgent
from langchain.agents import create_agent

from src.ableton_tools import load_ableton_tools
from src.settings import SETTINGS


async def create_melody_chord_composer_subagent() -> CompiledSubAgent:
    """Create melody/chord composer subagent with only add_notes_to_clip tool."""
    with open("src/prompts/MELODY_CHORD_COMPOSER_PROMPT.md", "r") as f:
        system_prompt = f.read()

    tools = await load_ableton_tools(include=["add_notes_to_clip"])

    agent = create_agent(
        model=SETTINGS.model_name,
        system_prompt=system_prompt,
        tools=tools,
    )

    return CompiledSubAgent(
        name="melody-chord-composer-agent",
        description="Agent specialized in harmony and sophisticated melodies. Creates chord progressions, bass lines, and complex off-beat melodic content.",
        runnable=agent,
    )
