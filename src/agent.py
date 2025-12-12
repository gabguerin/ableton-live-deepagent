"""Producer Agent - Deep agent for complex music production tasks.

This module implements a sophisticated music producer agent using LangChain's
deep agents framework. The agent provides:
- Music theory and composition guidance
- Sound design and synthesis advice
- Mixing and mastering techniques
- Creative workflow optimization
- Context-aware planning and memory management
"""

from typing import Optional

from deepagents import create_deep_agent
from langchain.chat_models import BaseChatModel, init_chat_model
from langchain_core.tools.base import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph.state import CompiledStateGraph

from src.settings import SETTINGS


class ProducerAgent:
    """Deep Agent specialized in music production assistance."""

    def __init__(self):
        """Initialize the Producer Agent."""
        self._agent: Optional[CompiledStateGraph] = None
        self._chat_model: Optional[BaseChatModel] = None
        self._system_prompt: Optional[str] = None
        self._tools: list[BaseTool] = []

    async def _setup_agent(self) -> None:
        """Set up the deep agent with music production specialization."""

        self._chat_model = await self._create_chat_model()
        self._system_prompt = await self._load_system_prompt()
        self._tools = [
            *await self._load_ableton_mcp_tools(),
            *await self._load_hooktheory_mcp_tools(),
        ]

        self._agent = create_deep_agent(
            model=self._chat_model,
            system_prompt=self._system_prompt,
            tools=self._tools,
        )

    async def _create_chat_model(self) -> BaseChatModel:
        """Load the model name from settings."""
        return init_chat_model(SETTINGS.model_name)

    async def _load_system_prompt(self) -> str:
        """Load the PROMPT.md file."""
        with open("src/PROMPT.md", "r") as f:
            system_prompt = f.read()
        return system_prompt

    async def _load_hooktheory_mcp_tools(self) -> list[BaseTool]:
        """Initialize the MCP client for AbletonMCP server connection."""
        self.mcp_client = MultiServerMCPClient(
            {
                "ableton": {
                    "transport": "stdio",
                    "command": "uvx",
                    "args": ["hooktheory-mcp"],
                    "env": {
                        "HOOKTHEORY_USERNAME": SETTINGS.hooktheory_username,
                        "HOOKTHEORY_PASSWORD": SETTINGS.hooktheory_password,
                    },
                }
            }
        )

        return await self.mcp_client.get_tools()

    async def _load_ableton_mcp_tools(self) -> list[BaseTool]:
        """Initialize the MCP client for AbletonMCP server connection."""

        self.mcp_client = MultiServerMCPClient(
            {
                "ableton": {
                    "transport": "stdio",
                    "command": "uvx",
                    "args": ["ableton-mcp"],
                }
            }
        )

        ableton_tools = []
        for tool in await self.mcp_client.get_tools():
            if tool.name == "add_notes_to_clip":
                tool = self._patch_add_notes_to_clip_tool(tool)
            ableton_tools.append(tool)

        return ableton_tools

    def _patch_add_notes_to_clip_tool(self, tool: BaseTool) -> BaseTool:
        """Patch the add_notes_to_clip tool to include quantization parameter."""
        from pydantic import BaseModel

        class Note(BaseModel):
            pitch: int
            start_time: float
            duration: float
            velocity: int
            mute: bool

        class AddNotesArgs(BaseModel):
            track_index: int
            clip_index: int
            notes: list[Note]

        tool.args_schema = AddNotesArgs
        return tool

    def get_agent(self) -> CompiledStateGraph:
        """Get the underlying deep agent instance."""
        if self._agent is None:
            raise ValueError("Producer Agent setup failed.")
        return self._agent


async def create_producer_agent() -> CompiledStateGraph:
    """Create and initialize a Producer Agent.

    Args:
        config: Optional configuration for the agent

    Returns:
        Configured ProducerAgent instance
    """
    producer_agent = ProducerAgent()
    await producer_agent._setup_agent()
    return producer_agent.get_agent()
