"""Ableton tools for the Producer Agent."""

from typing import List

from langchain_core.tools import BaseTool, tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from loguru import logger

from .midi_models import MidiNote


class AbletonTools:
    """Collection of tools for Ableton Live integration."""

    def __init__(self):
        """Initialize Ableton tools."""
        self._tools = []
        self._mcp_client = None

    async def _initialize_mcp_client(self):
        """Initialize the MCP client for AbletonMCP server connection."""
        self._mcp_client = MultiServerMCPClient(
            {
                "ableton": {
                    "transport": "stdio",
                    "command": "uvx",
                    "args": ["ableton-mcp"],
                }
            }
        )

    async def _get_mcp_tools(self) -> list[BaseTool]:
        """Get the list of Ableton tools."""
        await self._initialize_mcp_client()
        if self._mcp_client is None:
            raise RuntimeError("MCP client is not initialized.")

        return await self._mcp_client.get_tools()

    async def get_all_tools(self) -> list[BaseTool]:
        """Get all available tools including MCP tools and improved wrappers."""
        mcp_tools = await self._get_mcp_tools()

        improved_tools = [
            self._create_add_notes_tool(),
        ]

        filtered_mcp_tools = [
            mcp_tool
            for mcp_tool in mcp_tools
            if not (hasattr(mcp_tool, "name") and "add_notes_to_clip" in mcp_tool.name)
        ]

        return filtered_mcp_tools + improved_tools

    async def _get_mcp_add_notes_tool(self) -> BaseTool:
        """Get the add_notes_to_clip tool from MCP."""
        tools = await self._get_mcp_tools()
        for tool_ in tools:
            if hasattr(tool_, "name") and "add_notes_to_clip" in tool_.name:
                return tool_
        raise RuntimeError("add_notes_to_clip tool not found in MCP tools")

    async def add_notes_to_clip_improved(
        self, track_index: int, clip_index: int, notes: List[MidiNote]
    ) -> str:
        """
        Add MIDI notes to a clip with improved type safety and validation.

        This is a wrapper around the MCP add_notes_to_clip tool that provides
        better type safety, validation, and user experience.

        Args:
            track_index: The index of the track containing the clip
            clip_index: The index of the clip slot containing the clip
            notes: List of MidiNote objects with proper validation

        Returns:
            Success/error message string
        """
        try:
            if not notes:
                return "No notes provided to add to clip"

            for i, note_obj in enumerate(notes):
                if not isinstance(note_obj, MidiNote):
                    raise ValueError(f"Note {i} is not a valid MidiNote object")

            if self._mcp_client is None:
                await self._initialize_mcp_client()

            notes_data = [note_obj.to_ableton_dict() for note_obj in notes]

            add_notes_tool = await self._get_mcp_add_notes_tool()
            if add_notes_tool is None:
                raise RuntimeError("add_notes_to_clip tool not found in MCP tools")

            await add_notes_tool.ainvoke(
                {
                    "track_index": track_index,
                    "clip_index": clip_index,
                    "notes": notes_data,
                }
            )

            logger.info(
                f"Added {len(notes)} notes to track {track_index}, clip {clip_index}"
            )
            return f"Successfully added {len(notes)} notes to clip at track {track_index}, slot {clip_index}"

        except Exception as e:
            error_msg = f"Error adding notes to clip: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _create_add_notes_tool(self) -> BaseTool:
        """Create a LangChain tool wrapper for improved add_notes_to_clip."""

        @tool("add_notes_to_clip_improved")
        async def add_notes_wrapper(
            track_index: int, clip_index: int, notes: List[MidiNote]
        ) -> str:
            """Add MIDI notes to a clip with improved type safety and validation.

            Args:
                track_index: The index of the track containing the clip
                clip_index: The index of the clip slot containing the clip
                notes: List of MidiNote objects with proper validation
            """
            return await self.add_notes_to_clip_improved(track_index, clip_index, notes)

        return add_notes_wrapper


async def get_improved_ableton_tools() -> List[BaseTool]:
    """Get all improved Ableton tools as LangChain tools.

    This function creates an AbletonTools instance and returns all available tools
    including both MCP tools and improved wrappers, ready to be used by LangChain agents.

    Returns:
        List of BaseTool instances for LangChain integration

    Usage:
        >>> tools = await get_improved_ableton_tools()
        >>> # Use with LangChain agents
        >>> agent = create_agent(model="gpt-4", tools=tools, ...)
    """
    ableton_tools = AbletonTools()
    return await ableton_tools.get_all_tools()
