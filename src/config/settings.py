"""
Environment-aware configuration using Pydantic Settings.

Configuration precedence (highest to lowest):
1. Environment variables
2. .env file
3. Default values

Usage:
    from src.config.settings import get_settings
    
    settings = get_settings()
    print(settings.environment)  # "local", "dev", "stg", or "prod"
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    app_environment: Literal["local", "dev", "stg", "prod"] = Field(
        default="local",
        description="Deployment environment",
    )

    # LLM Configuration
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key for LLM calls",
    )
    openai_model: str = Field(
        default="gpt-4o",
        description="Default OpenAI model to use",
    )
    openai_temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="LLM temperature (0.0 = deterministic)",
    )

    # Database Configuration
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/langgraph_agent",
        description="PostgreSQL connection URL",
    )
    database_pool_size: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Database connection pool size",
    )
    database_max_overflow: int = Field(
        default=10,
        ge=0,
        le=100,
        description="Max overflow connections beyond pool size",
    )

    # Observability
    langchain_tracing_v2: bool = Field(
        default=False,
        description="Enable LangSmith tracing",
    )
    langchain_api_key: str = Field(
        default="",
        description="LangSmith API key",
    )
    langchain_project: str = Field(
        default="langgraph-agent",
        description="LangSmith project name",
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )
    log_format: Literal["json", "console"] = Field(
        default="console",
        description="Log output format",
    )

    # Feature Flags
    enable_caching: bool = Field(
        default=True,
        description="Enable response caching",
    )
    enable_rate_limiting: bool = Field(
        default=True,
        description="Enable API rate limiting",
    )
    enable_evaluation_sampling: bool = Field(
        default=False,
        description="Enable real-time evaluation sampling",
    )
    evaluation_sample_rate: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Percentage of requests to evaluate (0.0-1.0)",
    )

    @field_validator("openai_api_key")
    @classmethod
    def validate_api_key_format(cls, v: str) -> str:
        """Validate OpenAI API key format if provided."""
        if v and not v.startswith("sk-"):
            raise ValueError("OpenAI API key must start with 'sk-'")
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_environment == "prod"

    @property
    def is_development(self) -> bool:
        """Check if running in a development environment (local or dev)."""
        return self.app_environment in ("local", "dev")

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL (converts async URL if needed)."""
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")

    @property
    def database_url_async(self) -> str:
        """Get async database URL."""
        if "asyncpg" not in self.database_url:
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to ensure settings are only loaded once.
    Call get_settings.cache_clear() to reload settings (useful for testing).
    """
    return Settings()
