"""LLM Factory for creating chat models with provider-specific configurations."""

import os

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI

from src.settings import SETTINGS


def create_llm() -> BaseChatModel:
    """Create a chat model based on settings with specified temperature.

    Args:
        temperature: Temperature for the model (0.0-1.0). Lower values are more
                    deterministic, higher values are more creative.

    Returns:
        Configured chat model instance

    Raises:
        ValueError: If provider is not supported or required API key is missing
    """
    provider = SETTINGS.llm_provider
    model_name = SETTINGS.model_name
    temperature = SETTINGS.model_temperature

    if provider == "openai":
        if not SETTINGS.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set when using OpenAI provider")

        os.environ["OPENAI_API_KEY"] = SETTINGS.openai_api_key

        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
        )

    elif provider == "anthropic":
        if not SETTINGS.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY must be set when using Anthropic provider"
            )

        os.environ["ANTHROPIC_API_KEY"] = SETTINGS.anthropic_api_key

        return ChatAnthropic(
            model=model_name,
            temperature=temperature,
        )

    elif provider in "google":
        if not SETTINGS.google_api_key:
            raise ValueError("GOOGLE_API_KEY must be set when using Google provider")

        os.environ["GOOGLE_API_KEY"] = SETTINGS.google_api_key

        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
        )

    elif provider == "mistral":
        if not SETTINGS.mistral_api_key:
            raise ValueError("MISTRAL_API_KEY must be set when using Mistral provider")

        os.environ["MISTRAL_API_KEY"] = SETTINGS.mistral_api_key

        return ChatMistralAI(
            model=model_name,
            temperature=temperature,
        )

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported providers: openai, anthropic, google"
        )


def get_model_info() -> dict:
    """Get information about the configured model.

    Returns:
        Dictionary with model provider and name information
    """
    return {
        "provider": SETTINGS.llm_provider,
        "model_name": SETTINGS.model_name,
        "supported_providers": ["openai", "anthropic", "google"],
    }
