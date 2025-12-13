"""Producer Agent - Deep agent for complex music production tasks.

This module implements a sophisticated music producer agent using LangChain's
deep agents framework. The agent provides:
- Music theory and composition guidance
- Sound design and synthesis advice
- Mixing and mastering techniques
- Creative workflow optimization
- Context-aware planning and memory management
"""

from deepagents import CompiledSubAgent, create_deep_agent
from langchain.agents import create_agent
from langchain.chat_models import BaseChatModel, init_chat_model
from langchain_core.tools.base import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph.state import CompiledStateGraph

from src.models import AddNotesArgs
from src.settings import SETTINGS


class ProducerAgent:
    """Deep Agent specialized in music production assistance."""

    def __init__(self):
        """Initialize the Producer Agent."""
        self._agent: CompiledStateGraph | None = None

    async def _setup_agent(self) -> None:
        """Set up the deep agent with music production specialization."""

        chat_model = await self._create_chat_model()
        system_prompt = await self._load_system_prompt()
        tools = await self._load_ableton_mcp_tools()

        drum_composer_subagent = await self._create_drum_composer_subagent()
        melody_chord_composer_subagent = (
            await self._create_melody_chord_composer_subagent()
        )

        self._agent = create_deep_agent(
            model=chat_model,
            system_prompt=system_prompt,
            tools=tools,
            subagents=[drum_composer_subagent, melody_chord_composer_subagent],
        )

    async def _create_chat_model(self) -> BaseChatModel:
        """Load the model name from settings."""
        return init_chat_model(SETTINGS.model_name)

    async def _load_system_prompt(self) -> str:
        """Load the PRODUCER_PROMPT.md file."""
        with open("src/prompts/PRODUCER_PROMPT.md", "r") as f:
            system_prompt = f.read()
        return system_prompt

    async def _create_drum_composer_subagent(self) -> CompiledSubAgent:
        """Initialize the Drum Composer SubAgent for rhythm and percussion tasks."""
        with open("src/prompts/DRUM_COMPOSER_PROMPT.md", "r") as f:
            system_prompt = f.read()

        drum_composer_agent = create_agent(
            model=SETTINGS.model_name,
            system_prompt=system_prompt,
        )
        return CompiledSubAgent(
            name="drum-composer-agent",
            description="Agent specialized in drum programming and rhythmic patterns. Creates kick, snare, hi-hat, and percussion patterns across all genres.",
            runnable=drum_composer_agent,
        )

    async def _create_melody_chord_composer_subagent(self) -> CompiledSubAgent:
        """Initialize the Melody & Chord Composer SubAgent for harmonic and melodic tasks."""
        with open("src/prompts/MELODY_CHORD_COMPOSER_PROMPT.md", "r") as f:
            system_prompt = f.read()

        melody_chord_composer_agent = create_agent(
            model=SETTINGS.model_name,
            system_prompt=system_prompt,
        )
        return CompiledSubAgent(
            name="melody-chord-composer-agent",
            description="Agent specialized in harmony and sophisticated melodies. Creates chord progressions, bass lines, and complex off-beat melodic content.",
            runnable=melody_chord_composer_agent,
        )

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
                tool.args_schema = AddNotesArgs
            ableton_tools.append(tool)

        return ableton_tools

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
