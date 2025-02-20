import os

import pytest
from dotenv import load_dotenv
from pydantic import ValidationError

from src.config.settings import ConfigSettings

config = ConfigSettings()

# Load environment variables for testing
load_dotenv()


def test_valid_config(monkeypatch):
    """Test ConfigSettings with valid environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-1234")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-anthropic-5678")

    config = ConfigSettings()
    assert config.OPENAI_API_KEY.get_secret_value() == "sk-test-1234"
    assert config.ANTHROPIC_API_KEY.get_secret_value() == "sk-anthropic-5678"


def test_empty_api_keys(monkeypatch):
    """Test that empty API keys raise a ValidationError."""

    monkeypatch.setenv("OPENAI_API_KEY", " ")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")

    with pytest.raises(ValidationError, match="API key cannot be empty"):
        ConfigSettings()


@pytest.fixture
def reload_env():
    """Fixture to reload .env before and after a test."""
    load_dotenv(override=True)  # Ensure .env is loaded
    yield
    load_dotenv(override=True)  # Restore after test


def test_missing_api_keys(monkeypatch, reload_env):
    """Test missing API keys and restore .env afterward."""

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(ValidationError, match="Field required"):
        ConfigSettings(_env_file=None)


def test_env_example_missing():
    example_env_path = ".env"
    assert os.path.exists(example_env_path), "The .env.example file is missing!"
