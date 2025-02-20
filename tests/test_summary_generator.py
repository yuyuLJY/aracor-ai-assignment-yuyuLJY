from unittest.mock import MagicMock, patch

import pytest

from src.models.schemas import APIResponse, SummaryResponse
from src.services.model_manager import ModelManager
from src.services.summary import SummaryGenerator

from requests.exceptions import Timeout

def test_generate_summary_partial_failure():
    """
    Test case where some chunk generations succeed while others fail (partial response).
    """
    mock_model_manager = MagicMock()
    mock_model_manager.generate_response.side_effect = [
        "Summary 1",  
        Timeout("Timeout error"),  
        "Summary 3", 
    ]

    summary_generator = SummaryGenerator(mock_model_manager)
    summary_generator.chunk_text = MagicMock(return_value=["Chunk1.", "Chunk2.", "Chunk3."])

    text = "Chunk1. Chunk2. Chunk3."
    response = summary_generator.generate_summary(text, "brief")

    assert isinstance(response, APIResponse)
    assert response.success is True
    assert response.code == 206
    assert response.data.status == "partial"
    assert "Summary 1" in response.data.summary
    assert "Summary 3" in response.data.summary
    assert "Timeout error" in response.message

def test_generate_summary_chunk_text_runtime_error():
    mock_model_manager = MagicMock(spec=ModelManager)
    summary_generator = SummaryGenerator(mock_model_manager)
    # summary_generator.chunk_text = MagicMock(side_effect=RuntimeError("Chunking failed"))
    # or
    summary_generator.chunk_text = MagicMock()
    summary_generator.chunk_text.side_effect = RuntimeError("Chunking failed") 

    text = "This is a test text."
    response = summary_generator.generate_summary(text)

    expected_response = APIResponse(
        success=False,
        code=500,
        message="Chunking failed",
        data=None,
    )

    assert response.success == expected_response.success
    assert response.code == expected_response.code
    assert response.message == expected_response.message
    assert response.data == expected_response.data


@pytest.fixture
def mock_model_manager():
    mock_manager = MagicMock()
    mock_manager.generate_response.return_value = "summarization results"
    return mock_manager


@pytest.mark.parametrize(
    "summary_type, text",
    [
        ("brief", "This is a test input."),
        ("detailed", "This is a test input."),
        ("bullet points", "This is a test input."),
        ("echnical", "This is a test input."),
        ("layman", "This is a test input."),
        ("brief", "Lorem ipsum dolor sit amet, " * 1000),  # Very long input
        ("brief", "Special characters: !@#$%^&*()_+{}|:<>?~`"),  # Special characters
        ("brief", "Bonjour, это тест, こんにちは, مرحباً"),  # Multiple languages
        (
            "brief",
            "The algorithm has a complexity of O(n log n) and uses a heap-based approach.",
        ),  # Technical content
    ],
)
def test_summary_generation(mock_model_manager, summary_type, text):
    """Test summary generation process with a mocked model response."""

    summarizer = SummaryGenerator(mock_model_manager)
    response = summarizer.generate_summary(text, summary_type)

    # Assertions
    assert isinstance(response, APIResponse)
    assert response.success is True
    assert response.message == "Summarization successful."
    assert response.data is not None
    assert isinstance(response.data, SummaryResponse)
    assert response.data.summary.startswith("summarization results")

    # Ensure generate_response was called with expected prompt
    mock_model_manager.generate_response.assert_called()


@pytest.mark.parametrize(
    "summary_type, text",
    [
        ("brief", "This is a test input."),
        # ("detailed", "This is a test input."),
        # ("bullet points", "This is a test input."),
        # ("echnical", "This is a test input."),
        # ("layman", "This is a test input."),
        # ("brief", "Lorem ipsum dolor sit amet, " * 1000),  # Very long input
        # ("brief", "Special characters: !@#$%^&*()_+{}|:<>?~`"),  # Special characters
        # ("brief", "Bonjour, это тест, こんにちは, مرحباً"),  # Multiple languages
        # ("brief", "The algorithm has a complexity of O(n log n) and uses a heap-based approach."),  # Technical content
    ],
)
def test_summary_generation_business_logic(summary_type, text):
    """Test summary generation process with a mocked model response."""

    model_manager = ModelManager().get_model("openai")
    summarizer = SummaryGenerator(model_manager)
    response = summarizer.generate_summary(text, summary_type)

    # Assertions
    assert isinstance(response, APIResponse)
    assert response.success is True
    assert response.message == "Generate summarization successfully"
    assert response.data is not None
    assert isinstance(response.data, SummaryResponse)

