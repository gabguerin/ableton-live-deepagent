"""Settings for the Ableton Producer Agent project."""

from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    llm_provider: Literal["openai", "anthropic", "gemini"]
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None
    model_name: str

    @model_validator(mode="after")
    def validate_openai_api_key(self) -> "Settings":
        """Validate API keys for each LLM provider."""
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY must be set when LLM_PROVIDER is 'openai'."
            )
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY must be set when LLM_PROVIDER is 'anthropic'."
            )
        if self.llm_provider == "gemini" and not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY must be set when LLM_PROVIDER is 'gemini'."
            )
        return self

    class Config:
        """Configuration for the settings."""

        env_file = ".env"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get the project settings instance (cached singleton)."""
    return Settings()  # type: ignore[call-arg]


SETTINGS = get_settings()
