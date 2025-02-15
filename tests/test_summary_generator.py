import pytest
from unittest.mock import MagicMock
from src.services.model_manager import ModelManager
from src.services.summary import SummaryGenerator
from src.models.schemas import APIResponse, SummaryResponse

@pytest.fixture
def mock_model_manager():
    """Mock the ModelManager class."""
    mock = MagicMock(spec=ModelManager)
    mock.generate_response.side_effect = lambda prompt: f"Mocked summary for: {prompt}"
    return mock

@pytest.fixture
def summary_generator(mock_model_manager):
    """Initialize the SummaryGenerator with a mock model manager."""
    return SummaryGenerator(mock_model_manager)

@pytest.mark.parametrize("text, summary_type", [
    ("This is a test input for summary generation.", "brief"),
    ("This is a detailed summary test input with more content.", "detailed"),
    ("This is a bullet point summary test.", "bullet points"),
])
def test_summary_generation(summary_generator, text, summary_type):
    """Test different types of summary generation."""
    response = summary_generator.generate_summary(text, summary_type)
    assert isinstance(response, APIResponse)
    assert response.success
    assert response.code == 200
    assert response.data.status == "success"
    assert response.data.summary.startswith("Mocked summary for:")

@pytest.mark.parametrize("text", [
    ("Lorem ipsum dolor sit amet, " * 1000),  # Very long input
    ("Short."),  # Very short input
    ("Special characters: !@#$%^&*()_+{}|:<>?~`"),  # Special characters
    ("Bonjour, это тест, こんにちは, مرحباً"),  # Multiple languages
    ("The algorithm has a complexity of O(n log n) and uses a heap-based approach."),  # Technical content
])
def test_special_cases(summary_generator, text):
    """Test handling of edge cases like long input, short input, special characters, multiple languages, and technical content."""
    response = summary_generator.generate_summary(text, "brief")
    assert isinstance(response, APIResponse)
    assert response.success
    assert response.code == 200
    assert response.data.status == "success"
    assert response.data.summary.startswith("Mocked summary for:")
