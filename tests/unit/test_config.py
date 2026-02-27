"""Unit tests for configuration management."""

import pytest
from pydantic import ValidationError

from src.config.settings import Settings, get_settings
from src.config.constants import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_EVALUATION_THRESHOLD,
    EVALUATION_METRICS,
)


class TestSettings:
    """Tests for the Settings class."""

    def test_default_environment_is_local(self):
        """Settings should default to local environment."""
        settings = Settings(openai_api_key="sk-test")
        assert settings.app_environment == "local"

    def test_valid_environments(self, monkeypatch):
        """Settings should accept all valid environment values."""
        valid_envs = ["local", "dev", "stg", "prod"]
        
        for env in valid_envs:
            monkeypatch.setenv("APP_ENVIRONMENT", env)
            monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
            settings = Settings()
            assert settings.app_environment == env

    def test_invalid_environment_raises_error(self, monkeypatch):
        """Settings should reject invalid environment values."""
        monkeypatch.setenv("APP_ENVIRONMENT", "invalid")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        
        assert "app_environment" in str(exc_info.value)

    def test_openai_api_key_validation(self, monkeypatch):
        """API key must start with 'sk-' if provided."""
        monkeypatch.setenv("OPENAI_API_KEY", "invalid-key")
        
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        
        assert "must start with 'sk-'" in str(exc_info.value)

    def test_empty_api_key_is_allowed(self):
        """Empty API key should be allowed (for testing)."""
        settings = Settings(openai_api_key="")
        assert settings.openai_api_key == ""

    def test_valid_api_key_accepted(self, monkeypatch):
        """Valid API key should be accepted."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-valid-test-key")
        settings = Settings()
        assert settings.openai_api_key == "sk-valid-test-key"

    def test_temperature_bounds(self, monkeypatch):
        """Temperature must be between 0.0 and 2.0."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        
        # Valid temperature
        monkeypatch.setenv("OPENAI_TEMPERATURE", "1.0")
        settings = Settings()
        assert settings.openai_temperature == 1.0
        
        # Invalid temperature (too high)
        monkeypatch.setenv("OPENAI_TEMPERATURE", "3.0")
        with pytest.raises(ValidationError):
            Settings()

    def test_database_pool_size_bounds(self, monkeypatch):
        """Pool size must be between 1 and 100."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        
        # Invalid pool size
        monkeypatch.setenv("DATABASE_POOL_SIZE", "0")
        with pytest.raises(ValidationError):
            Settings()

    def test_is_production_property(self):
        """is_production should return True only for prod environment."""
        settings = Settings(app_environment="prod", openai_api_key="sk-test")
        assert settings.is_production is True
        
        settings = Settings(app_environment="dev", openai_api_key="sk-test")
        assert settings.is_production is False

    def test_is_development_property(self):
        """is_development should return True for local and dev environments."""
        settings = Settings(app_environment="local", openai_api_key="sk-test")
        assert settings.is_development is True
        
        settings = Settings(app_environment="dev", openai_api_key="sk-test")
        assert settings.is_development is True
        
        settings = Settings(app_environment="prod", openai_api_key="sk-test")
        assert settings.is_development is False

    def test_database_url_sync_property(self):
        """database_url_sync should convert async URLs."""
        settings = Settings(
            database_url="postgresql+asyncpg://user:pass@host/db",
            openai_api_key="sk-test",
        )
        assert settings.database_url_sync == "postgresql://user:pass@host/db"

    def test_database_url_async_property(self):
        """database_url_async should add asyncpg driver."""
        settings = Settings(
            database_url="postgresql://user:pass@host/db",
            openai_api_key="sk-test",
        )
        assert settings.database_url_async == "postgresql+asyncpg://user:pass@host/db"

    def test_log_level_validation(self, monkeypatch):
        """Log level must be a valid level."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("LOG_LEVEL", "INVALID")
        
        with pytest.raises(ValidationError):
            Settings()

    def test_evaluation_sample_rate_bounds(self, monkeypatch):
        """Sample rate must be between 0.0 and 1.0."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("EVALUATION_SAMPLE_RATE", "1.5")
        
        with pytest.raises(ValidationError):
            Settings()


class TestGetSettings:
    """Tests for the get_settings function."""

    def test_get_settings_returns_settings_instance(self, monkeypatch):
        """get_settings should return a Settings instance."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        get_settings.cache_clear()  # Clear cache for test isolation
        
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_get_settings_is_cached(self, monkeypatch):
        """get_settings should return the same instance on repeated calls."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        get_settings.cache_clear()
        
        settings1 = get_settings()
        settings2 = get_settings()
        
        assert settings1 is settings2

    def test_cache_clear_reloads_settings(self, monkeypatch):
        """Clearing cache should reload settings."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test1")
        get_settings.cache_clear()
        settings1 = get_settings()
        
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test2")
        get_settings.cache_clear()
        settings2 = get_settings()
        
        assert settings1.openai_api_key != settings2.openai_api_key


class TestConstants:
    """Tests for configuration constants."""

    def test_default_max_retries_is_positive(self):
        """Max retries should be a positive number."""
        assert DEFAULT_MAX_RETRIES > 0

    def test_evaluation_threshold_is_valid(self):
        """Evaluation threshold should be between 0 and 1."""
        assert 0 <= DEFAULT_EVALUATION_THRESHOLD <= 1

    def test_evaluation_metrics_not_empty(self):
        """Evaluation metrics list should not be empty."""
        assert len(EVALUATION_METRICS) > 0
        assert all(isinstance(m, str) for m in EVALUATION_METRICS)
