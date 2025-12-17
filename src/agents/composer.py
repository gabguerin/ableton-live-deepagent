"""Dynamic advisor agents module using registry pattern.

This module provides a registry-based system for managing and creating
specialized advisor subagents dynamically.
"""

import os

from deepagents import CompiledSubAgent, SubAgent
from pydantic import BaseModel


class ComposerInfo(BaseModel):
    """Composer agent configuration model."""

    name: str
    prompt_file: str
    description: str


async def create_composer(
    composer_info: ComposerInfo,
) -> CompiledSubAgent | SubAgent:
    """Create a composer agent from its configuration."""
    if not os.path.exists(composer_info.prompt_file):
        raise FileNotFoundError(f"Prompt file not found: {composer_info.prompt_file}")

    with open(composer_info.prompt_file, "r") as f:
        system_prompt = f.read()

    return {
        "name": composer_info.name,
        "description": composer_info.description,
        "system_prompt": system_prompt,
        "tools": [],
        "model": "gpt-5-nano",
    }
