"""Dynamic musician agents module using registry pattern.

This module provides a registry-based system for managing and creating
specialized musician subagents dynamically.
"""

import os

from deepagents import CompiledSubAgent, SubAgent
from langchain.agents import create_agent
from openai import BaseModel

from src.ableton_tools import load_ableton_tools
from src.settings import SETTINGS


class MusicianInfo(BaseModel):
    """Musician agent configuration model."""

    name: str
    prompt_file: str
    description: str


async def create_musician(
    musician_info: MusicianInfo,
) -> CompiledSubAgent | SubAgent:
    """Create a musician agent from its configuration."""
    if not os.path.exists(musician_info.prompt_file):
        raise FileNotFoundError(f"Prompt file not found: {musician_info.prompt_file}")

    with open(musician_info.prompt_file, "r") as f:
        system_prompt = f.read()

    tools = await load_ableton_tools(include=["add_notes_to_clip"])

    agent = create_agent(
        model=SETTINGS.model_name,
        system_prompt=system_prompt,
        tools=tools,
    )

    return CompiledSubAgent(
        name=musician_info.name,
        description=musician_info.description,
        runnable=agent,
    )
