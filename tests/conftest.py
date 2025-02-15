import os

import pytest
from dotenv import load_dotenv
from pydantic import ValidationError

from src.config.settings import ConfigSettings

config = ConfigSettings()

# Load environment variables for testing
load_dotenv()


def test_valid_config():
    """Test ConfigSettings with valid environment variables."""
    os.environ["MODEL_PROVIDER"] = "openai"
    os.environ["OPENAI_API_KEY"] = "sk-test-1234"
    os.environ["ANTHROPIC_API_KEY"] = "sk-anthropic-5678"

    config = ConfigSettings()
    assert config.MODEL_PROVIDER == "openai"
    assert config.OPENAI_API_KEY.get_secret_value() == "sk-test-1234"
    assert config.ANTHROPIC_API_KEY.get_secret_value() == "sk-anthropic-5678"


def test_invalid_secretstr():
    """Test ConfigSettings raises validation error when secret values are invalid."""
    os.environ["MODEL_PROVIDER"] = "openai"
    os.environ["OPENAI_API_KEY"] = ""  # Empty secret
    os.environ["ANTHROPIC_API_KEY"] = ""  # Empty secret

    with pytest.raises(ValidationError):
        ConfigSettings()


def test_env_example_missing():
    example_env_path = ".env"
    assert os.path.exists(example_env_path), "The .env.example file is missing!"
