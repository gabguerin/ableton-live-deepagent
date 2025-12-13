"""Ableton tools loading module for the Producer Agent.

This module provides utilities for loading and filtering Ableton MCP tools
based on agent requirements.
"""

from langchain_core.tools.base import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from src.models import AddNotesArgs


async def load_ableton_tools(
    include: list[str] | None = None, exclude: list[str] | None = None
) -> list[BaseTool]:
    """Load Ableton MCP tools with include/exclude filtering.

    Args:
        include: List of tool names to include. If None, includes all tools.
        exclude: List of tool names to exclude. Applied after include filter.

    Returns:
        List of filtered BaseTool instances for Ableton Live interaction.
    """
    mcp_client = MultiServerMCPClient(
        {
            "ableton": {
                "transport": "stdio",
                "command": "uvx",
                "args": ["ableton-mcp"],
            }
        }
    )

    tools = []
    for tool in await mcp_client.get_tools():
        if include is not None and tool.name not in include:
            continue

        if exclude is not None and tool.name in exclude:
            continue

        if tool.name == "add_notes_to_clip":
            tool.args_schema = AddNotesArgs

        tools.append(tool)

    return tools
