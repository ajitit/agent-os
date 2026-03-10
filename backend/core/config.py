"""
File: config.py

Purpose:
Manages application configuration settings, loading them from environment variables
and providing a strongly-typed settings object.

Key Functionalities:
- Define `Settings` Pydantic model for environment validation
- Provide a cached singleton instance of global settings via `get_settings()`

Inputs:
- Environment variables (from `.env` or system environment)

Outputs:
- Validated `Settings` instance containing application configs

Interacting Files / Modules:
- None
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="AgentOS", description="Application name")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Runtime environment"
    )
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")

    # API
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins",
    )

    database_url: str = Field(
        default="postgresql://agentos:agentos@localhost:5432/agentos",
        description="PostgreSQL connection URL",
    )

    # Security
    jwt_secret_key: str = Field(default="secret", description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    rate_limit_per_minute: int = Field(
        default=60, description="API rate limit per minute per IP"
    )

    # LLM Integrations
    openai_api_key: str | None = Field(default=None, description="OpenAI API Key")
    anthropic_api_key: str | None = Field(default=None, description="Anthropic API Key")

    # Skills (Progressive Disclosure)
    skills_dir: str = Field(
        default="skills",
        description="Directory containing skill definitions (metadata.json, SKILL.md, resources/)",
    )


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
