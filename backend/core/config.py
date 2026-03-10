"""Application configuration with environment validation."""

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

    # Database
    database_url: str = Field(
        default="postgresql://agentos:agentos@localhost:5432/agentos",
        description="PostgreSQL connection URL",
    )

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    # Security
    rate_limit_per_minute: int = Field(
        default=60, description="API rate limit per minute per IP"
    )

    # Skills (Progressive Disclosure)
    skills_dir: str = Field(
        default="skills",
        description="Directory containing skill definitions (metadata.json, SKILL.md, resources/)",
    )


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
