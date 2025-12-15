"""Settings for the Ableton Producer Agent project."""

from functools import lru_cache
from typing import Literal

from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    llm_provider: Literal["openai", "anthropic", "google", "mistral"]
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    mistral_api_key: str | None = None

    model_name: str
    model_temperature: float

    @computed_field
    @property
    def model(self) -> str:
        """Construct full model identifier based on provider and model name."""
        return f"{self.llm_provider}:{self.model_name}"

    @model_validator(mode="after")
    def validate_api_keys(self) -> "Settings":
        """Validate API keys for each LLM provider."""
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY must be set when LLM_PROVIDER is 'openai'."
            )
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY must be set when LLM_PROVIDER is 'anthropic'."
            )
        if self.llm_provider == "google" and not self.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY must be set when LLM_PROVIDER is 'google'."
            )
        if self.llm_provider == "mistral" and not self.mistral_api_key:
            raise ValueError(
                "MISTRAL_API_KEY must be set when LLM_PROVIDER is 'mistral'."
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
