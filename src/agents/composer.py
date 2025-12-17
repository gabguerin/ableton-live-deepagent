"""Composer Agent Creation Module."""

import os

from deepagents import CompiledSubAgent, SubAgent

from src.settings import SETTINGS

COMPOSER_PROMPT_PATH = "src/prompts/COMPOSER.md"


async def create_composer() -> CompiledSubAgent | SubAgent:
    """Create a composer agent from its configuration."""
    if not os.path.exists(COMPOSER_PROMPT_PATH):
        raise FileNotFoundError("Prompt file not found.")

    with open(COMPOSER_PROMPT_PATH, "r") as f:
        system_prompt = f.read()

    return {
        "name": "composer",
        "description": (
            "Agent specialized in any musical aspect. "
            "Can provide comprehensive musical guidance about tracks composition, drum patterns, chord progressions, and more."
        ),
        "system_prompt": system_prompt,
        "tools": [],
        "model": SETTINGS.composer_model,
    }
