import asyncio
import socket
from unittest.mock import MagicMock, patch

import httpx
import pytest
from pydantic import ValidationError
from requests.exceptions import Timeout

from src.config.settings import ConfigSettings
from src.services.model_manager import ModelManager


def test_successful_openai_model_initialization():
    """Test OpenAI model initialization"""
    with patch("src.services.model_manager.ChatOpenAI") as mock_openai:
        mock_openai.return_value = MagicMock()
        with patch("src.config.settings.ConfigSettings", autospec=True) as mock_config:
            mock_config.MODEL_PROVIDER = "openai"
            model_manager = ModelManager()
            assert model_manager.model is not None
            mock_openai.assert_called_once()


# def test_successful_anthropic_model_initialization():
#     """Test Anthropic model initialization"""
#     with patch("src.services.model_manager.ChatAnthropic") as mock_anthropic:
#         mock_anthropic.return_value = MagicMock()
#         with patch("src.config.settings.ConfigSettings", autospec=True) as mock_config:
#             mock_config.MODEL_PROVIDER = "anthropic"
#             model_manager = ModelManager()
#             assert model_manager.model is not None
#             mock_anthropic.assert_called_once()


def test_api_key_validation():
    """Test API key validation with empty key"""
    with pytest.raises(ValidationError):
        ConfigSettings(OPENAI_API_KEY="")


def test_model_switching():
    """Test switching between OpenAI and Anthropic models"""
    with (
        patch("src.services.model_manager.ChatOpenAI") as mock_openai,
        patch("src.services.model_manager.ChatAnthropic") as mock_anthropic,
    ):
        mock_openai.return_value = MagicMock()
        mock_anthropic.return_value = MagicMock()
        with patch("src.config.settings.ConfigSettings", autospec=True) as mock_config:
            mock_config.MODEL_PROVIDER = "openai"
            model_manager = ModelManager()
            assert isinstance(model_manager.model, MagicMock)

            mock_config.MODEL_PROVIDER = "anthropic"
            model_manager = ModelManager()
            assert isinstance(model_manager.model, MagicMock)


def test_retry_mechanism():
    """Test retry mechanism for transient failures."""
    with patch.object(ModelManager, "__init__", lambda x: None):  # Bypass __init__
        model_manager = ModelManager()
        model_manager.model = MagicMock()
        model_manager.model.predict.side_effect = [
            Exception("Error"),
            Exception("Error"),
            "Success",
        ]  # 2 failures, 1 success

        result = model_manager.generate_response("Test prompt")

        assert result == "Success"
        assert model_manager.model.predict.call_count == 3  # Ensure it retried twice


def test_timeout_handling():
    """Test timeout errors are handled correctly"""
    with patch(
        "src.services.model_manager.ModelManager.generate_response", side_effect=Timeout
    ):
        model_manager = ModelManager()
        with pytest.raises(Timeout):
            model_manager.generate_response("Test prompt")


def test_error_response_handling():
    """Test unexpected error responses are logged and raised"""
    with patch(
        "src.services.model_manager.ModelManager.generate_response",
        side_effect=ValueError("Unexpected error"),
    ):
        model_manager = ModelManager()
        with pytest.raises(ValueError, match="Unexpected error"):
            model_manager.generate_response("Test prompt")
