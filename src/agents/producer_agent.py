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

from deepagents import SubAgent, create_deep_agent
from langchain_core.tools.base import BaseTool
from langgraph.graph.state import CompiledStateGraph


class ProducerAgent:
    """Deep Agent specialized in music production assistance."""

    def __init__(self):
        """Initialize the Producer Agent."""
        self._agent: Optional[CompiledStateGraph] = None

    async def _setup_agent(self) -> None:
        """Set up the deep agent with music production specialization."""

        system_prompt = await self._create_system_prompt()
        ableton_tools = await self._load_ableton_tools()
        composer_subagent = await self._create_composer_subagent()

        self._agent = create_deep_agent(
            model="gpt-5.1",
            system_prompt=system_prompt,
            tools=ableton_tools,
            # subagents=[composer_subagent],
        )

    async def _create_system_prompt(self) -> str:
        """Load the PROMPT.md file."""
        with open("src/prompts/PRODUCER_AGENT_PROMPT.md", "r") as f:
            system_prompt = f.read()
        return system_prompt

    async def _load_ableton_mcp_tools(self) -> list[BaseTool]:
        """Initialize the MCP client for AbletonMCP server connection."""
        from langchain_mcp_adapters.client import MultiServerMCPClient

        self.mcp_client = MultiServerMCPClient(
            {
                "ableton": {
                    "transport": "stdio",
                    "command": "uvx",
                    "args": ["ableton-mcp"],
                }
            }
        )

        return await self.mcp_client.get_tools()

    async def _load_ableton_tools(self) -> list[BaseTool]:
        """Load improved Ableton tools with better type safety and user experience."""
        from src.tools.ableton_tools import get_improved_ableton_tools

        return await get_improved_ableton_tools()

    async def _create_composer_subagent(self) -> SubAgent:
        """Create and return the Composer sub-agent."""
        with open("src/prompts/COMPOSER_AGENT_PROMPT.md", "r") as f:
            system_prompt = f.read()

        return {
            "name": "composer_agent",
            "description": "Composer agent specialized in generating structured music ideas for Ableton Live projects. Should be called to plan and create musical ideas, chord progressions, basslines, and drum patterns.",
            "system_prompt": system_prompt,
            "tools": [],
        }

    def get_agent(self) -> CompiledStateGraph:
        """Get the underlying deep agent instance."""
        if self._agent is None:
            raise ValueError("Producer Agent setup failed.")
        return self._agent


# Factory function for easy agent creation
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
