"""Environment-based configuration for lane using pydantic-settings."""

from __future__ import annotations

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class LaneSettings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    openrouter_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    llm_model: str = "openai/gpt-4o-mini"
    llm_base_url: str = "https://openrouter.ai/api/v1"
    llm_timeout: int = 60
    llm_max_retries: int = 3
    max_commits: int = 30

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
    )

    @property
    def api_key(self) -> Optional[str]:
        """Return the first available API key."""
        return self.openrouter_api_key or self.openai_api_key


_settings: Optional[LaneSettings] = None


def get_settings() -> LaneSettings:
    """Return a cached singleton of LaneSettings."""
    global _settings
    if _settings is None:
        _settings = LaneSettings()
    return _settings
