"""Test suite for ModelManager, OpenAIModel, AnthropicModel, and SummaryGenerator."""

import os
from unittest.mock import MagicMock, patch

import pytest
import httpx
from pydantic import ValidationError
from requests.exceptions import Timeout
from tenacity import RetryError

from src.config.settings import ConfigSettings
from src.services.model_manager import ModelManager, OpenAIModel, AnthropicModel
from src.services.summary import SummaryGenerator
from src.models.schemas import APIResponse


def test_successful_openai_model_initialization():
    """Test OpenAI model initialization."""
    with patch("src.services.model_manager.ChatOpenAI") as mock_openai:
        mock_openai.return_value = MagicMock()
        model = ModelManager.get_model("openai")
        assert isinstance(model, OpenAIModel)
        mock_openai.assert_called_once()

def test_successful_anthropic_model_initialization():
    """Test Anthropic model initialization."""
    with patch("src.services.model_manager.ChatAnthropic") as mock_anthropic:
        mock_anthropic.return_value = MagicMock()
        model = ModelManager.get_model("anthropic")
        assert isinstance(model, AnthropicModel)
        mock_anthropic.assert_called_once()

def test_api_key_validation():
    """Test API key validation with empty key."""
    with pytest.raises(ValidationError):
        ConfigSettings(OPENAI_API_KEY="")

def test_model_switching():
    """Test switching between OpenAI and Anthropic models."""
    with (
        patch("src.services.model_manager.ChatOpenAI") as mock_openai,
        patch("src.services.model_manager.ChatAnthropic") as mock_anthropic,
    ):
        mock_openai.return_value = MagicMock()
        mock_anthropic.return_value = MagicMock()
        
        model = ModelManager.get_model("openai")
        assert isinstance(model, OpenAIModel)
        
        model = ModelManager.get_model("anthropic")
        assert isinstance(model, AnthropicModel)

def test_retry_mechanism():
    """Test retry mechanism for transient failures."""
    model = OpenAIModel()
    model.model = MagicMock()
    model.model.predict.side_effect = [
        Exception("Error"),
        Exception("Error"),
        "Success",
    ]  # Two failures, one success
    
    result = model.generate_response("Test prompt")
    assert result == "Success"
    assert model.model.predict.call_count == 3  # Ensure it retried twice

def test_timeout_handling():
    """Test timeout errors are handled correctly."""
    model = OpenAIModel()
    model.model = MagicMock()
    model.model.predict.side_effect = Timeout
    
    with pytest.raises(RetryError):
        model.generate_response("Test prompt")

def test_error_response_handling():
    """Test unexpected error responses are logged and raised."""
    model = OpenAIModel()
    model.model = MagicMock()
    model.model.predict.side_effect = ValueError("Unexpected error")
    
    with pytest.raises(RetryError):
        model.generate_response("Test prompt")

@pytest.fixture
def mock_model_manager():
    """Mock the ModelManager class."""
    mock = MagicMock()
    mock.configure_mock(**{"generate_response.side_effect": lambda prompt: f"Mocked summary for: {prompt}"})
    return mock

@pytest.fixture
def summary_generator(mock_model_manager):
    """Initialize the SummaryGenerator with a mock model manager."""
    return SummaryGenerator(mock_model_manager)

@pytest.mark.parametrize(
    "text, summary_type",
    [
        ("This is a test input for summary generation.", "brief"),
        ("This is a detailed summary test input with more content.", "detailed"),
        ("This is a bullet point summary test.", "bullet points"),
    ],
)
def test_summary_generation(summary_generator, text, summary_type):
    """Test different types of summary generation."""
    response = summary_generator.generate_summary(text, summary_type)
    assert isinstance(response, APIResponse)
    assert response.success
    assert response.code == 200
    assert response.data.status == "success"
    assert response.data.summary.startswith("Mocked summary for:")

@pytest.mark.parametrize(
    "text",
    [
        ("Lorem ipsum dolor sit amet, " * 1000),  # Very long input
        ("Short."),  # Very short input
        ("Special characters: !@#$%^&*()_+{}|:<>?~`"),  # Special characters
        ("Bonjour, это тест, こんにちは, مرحباً"),  # Multiple languages
        ("The algorithm has a complexity of O(n log n) and uses a heap-based approach."),  # Technical content
    ],
)
def test_special_cases(summary_generator, text):
    """Test handling of edge cases like long input, short input, special characters, multiple languages, and technical content."""
    response = summary_generator.generate_summary(text, "brief")
    assert isinstance(response, APIResponse)
    assert response.success
    assert response.code == 200
    assert response.data.status == "success"
    assert response.data.summary.startswith("Mocked summary for:")
