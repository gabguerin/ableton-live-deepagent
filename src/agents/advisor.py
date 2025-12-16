"""Dynamic advisor agents module using registry pattern.

This module provides a registry-based system for managing and creating
specialized advisor subagents dynamically.
"""

import os

from deepagents import CompiledSubAgent, SubAgent
from pydantic import BaseModel


class AdvisorInfo(BaseModel):
    """Advisor agent configuration model."""

    name: str
    prompt_file: str
    description: str


async def create_advisor(
    advisor_info: AdvisorInfo,
) -> CompiledSubAgent | SubAgent:
    """Create a advisor agent from its configuration."""
    if not os.path.exists(advisor_info.prompt_file):
        raise FileNotFoundError(f"Prompt file not found: {advisor_info.prompt_file}")

    with open(advisor_info.prompt_file, "r") as f:
        system_prompt = f.read()

    return {
        "name": advisor_info.name,
        "description": advisor_info.description,
        "system_prompt": system_prompt,
        "tools": [],
        "model": "gpt-5-nano",
    }
