"""Shared pytest fixtures for all tests."""

import pytest
from unittest.mock import MagicMock, AsyncMock
from typing import Generator


@pytest.fixture
def mock_llm() -> MagicMock:
    """
    Fixture for deterministic LLM testing.
    
    Returns a mock LLM that can be configured to return specific responses.
    Use this for unit and integration tests to avoid real API calls.
    
    Example:
        def test_agent(mock_llm):
            mock_llm.invoke.return_value = AIMessage(content="Test response")
            result = my_function(llm=mock_llm)
            assert result == "Test response"
    """
    mock = MagicMock()
    mock.invoke = MagicMock(return_value=MagicMock(content="Mock response"))
    mock.ainvoke = AsyncMock(return_value=MagicMock(content="Mock async response"))
    mock.with_structured_output = MagicMock(return_value=mock)
    return mock


@pytest.fixture
def mock_llm_with_tool_call() -> MagicMock:
    """
    Fixture for testing tool-calling behavior.
    
    Returns a mock LLM that returns tool calls instead of text responses.
    """
    mock = MagicMock()
    tool_call_response = MagicMock(
        content="",
        tool_calls=[{
            "name": "test_tool",
            "args": {"arg1": "value1"},
            "id": "call_test123"
        }]
    )
    mock.invoke = MagicMock(return_value=tool_call_response)
    mock.ainvoke = AsyncMock(return_value=tool_call_response)
    return mock


@pytest.fixture
def sample_env_vars(monkeypatch) -> dict:
    """
    Fixture that sets up sample environment variables for testing.
    
    Uses monkeypatch to safely set env vars that are cleaned up after test.
    """
    env_vars = {
        "APP_ENVIRONMENT": "local",
        "OPENAI_API_KEY": "sk-test-key-for-testing",
        "OPENAI_MODEL": "gpt-4o",
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test_db",
        "LOG_LEVEL": "DEBUG",
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


@pytest.fixture
def temp_yaml_file(tmp_path) -> Generator:
    """
    Fixture that provides a temporary YAML file for testing.
    
    Example:
        def test_prompt_loading(temp_yaml_file):
            yaml_path = temp_yaml_file({"version": "1.0", "template": "Hello {name}"})
            prompt = load_prompt(yaml_path)
    """
    def _create_yaml(content: dict) -> str:
        import yaml
        file_path = tmp_path / "test.yaml"
        with open(file_path, "w") as f:
            yaml.dump(content, f)
        return str(file_path)
    
    return _create_yaml
