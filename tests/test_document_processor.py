import os
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from src.models.schemas import APIResponse  # Import APIResponse model
from src.processors.document import DocumentProcessor

# Test Files Directory
TEST_FILES_DIR = "tests/test_files/"


# Helper function to create test files
def create_test_file(file_path: str, content: str = "Sample text") -> None:
    """Create a test file with given content."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


@pytest.fixture(scope="session")
def _pdf_file() -> Generator[str, None, None]:
    """Fixture that provides a sample PDF file for testing."""
    file_path = os.path.join(TEST_FILES_DIR, "sample.pdf")
    create_test_file(file_path, "This is a test PDF file.")
    yield file_path

    if os.path.exists(file_path):
        os.remove(file_path)


@pytest.fixture
def _docx_file() -> str:
    """Fixture that provides a sample DOCX file for testing."""
    file_path = os.path.join(TEST_FILES_DIR, "sample.docx")
    create_test_file(file_path, "This is a test DOCX file.")
    return file_path


@pytest.fixture
def _txt_file() -> str:
    """Fixture that provides a sample TXT file for testing."""
    file_path = os.path.join(TEST_FILES_DIR, "sample.txt")
    create_test_file(file_path, "This is a test TXT file.")
    return file_path


@pytest.fixture
def _empty_file() -> str:
    """Fixture that provides an empty text file for testing."""
    file_path = os.path.join(TEST_FILES_DIR, "empty.txt")
    create_test_file(file_path, "")
    return file_path


@pytest.fixture
def _large_file() -> str:
    """Fixture that provides a large text file (>10MB) for testing."""
    file_path = os.path.join(TEST_FILES_DIR, "large.txt")
    create_test_file(file_path, "A" * (10 * 1024 * 1024 + 1))  # >10MB
    return file_path


@pytest.fixture
def _unsupported_file() -> str:
    """Fixture that provides a file with an unsupported extension for testing."""
    file_path = os.path.join(TEST_FILES_DIR, "unsupported.xyz")
    create_test_file(file_path, "This file has an unsupported extension.")
    return file_path


@pytest.fixture
def _corrupted_file() -> str:
    """Fixture that provides a corrupted PDF file for testing."""
    file_path = os.path.join(TEST_FILES_DIR, "corrupted.pdf")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(b"\x00\x01\x02")  # Writing invalid content
    return file_path


@pytest.fixture
def _nonexistent_file() -> str:
    """Fixture that provides a path to a nonexistent file for testing."""
    return os.path.join(TEST_FILES_DIR, "nonexistent.txt")


# Test Successful PDF Processing
# @patch("src.processors.document.PyPDFLoader")
# def test_successful_pdf_processing(mock_loader: MagicMock, _pdf_file: str) -> None:
#     """Test that a valid PDF file is processed correctly."""
#     mock_loader_instance = mock_loader.return_value
#     mock_loader_instance.load.return_value = [MagicMock(page_content="Extracted PDF content")]

#     processor = DocumentProcessor(_pdf_file)
#     response = processor.extract_text()

#     assert isinstance(response, APIResponse)
#     assert response.success is True
#     assert response.message == "Text extracted successfully"
#     assert response.data is not None
#     assert response.data.file_path == _pdf_file
#     assert response.data.file_type == "pdf"
#     assert response.data.content == "Extracted PDF content"

#     mock_loader.assert_called_once_with(_pdf_file)
#     mock_loader_instance.load.assert_called_once()


def test_successful_pdf_processing(_pdf_file: str) -> None:
    """Test that a valid PDF file is processed correctly."""

    with patch("src.processors.document.PyPDFLoader") as mock_loader:
        mock_instance = mock_loader.return_value
        mock_instance.load.return_value = [
            MagicMock(page_content="Extracted PDF content")
        ]

        # Run the function under test
        processor = DocumentProcessor(_pdf_file)
        response = processor.extract_text()

        # Assertions
        assert isinstance(response, APIResponse)
        assert response.success is True
        assert response.message == "Text extracted successfully"
        assert response.data is not None
        assert response.data.file_path == _pdf_file
        assert response.data.file_type == "pdf"
        assert response.data.content == "Extracted PDF content"

        # Verify PyPDFLoader was called
        mock_loader.assert_called_once_with(_pdf_file)
        mock_instance.load.assert_called_once()


# Test Successful DOCX Processing
@patch("src.processors.document.Docx2txtLoader")
def test_successful_docx_processing(mock_loader: MagicMock, _docx_file: str) -> None:
    """Test that a valid DOCX file is processed correctly."""
    mock_loader.return_value.load.return_value = [
        MagicMock(page_content="Extracted DOCX content")
    ]
    processor = DocumentProcessor(_docx_file)
    response = processor.extract_text()

    assert response.success is True
    assert response.message == "Text extracted successfully"
    assert response.data is not None
    assert response.data.file_path == _docx_file
    assert response.data.file_type == "docx"
    assert response.data.content == "Extracted DOCX content"


# Test Successful TXT Processing
def test_successful_txt_processing(_txt_file: str) -> None:
    """Test that a valid TXT file is processed correctly."""
    processor = DocumentProcessor(_txt_file)
    response = processor.extract_text()

    assert response.success is True
    assert response.message == "Text extracted successfully"
    assert response.data is not None
    assert response.data.file_path == _txt_file
    assert response.data.file_type == "txt"
    assert response.data.content == "This is a test TXT file."


# Test Handling of Large Files (>10MB)
def test_handling_large_files(_large_file: str) -> None:
    """Test that a large file (>10MB) is processed correctly."""
    processor = DocumentProcessor(_large_file)
    response = processor.extract_text()

    assert response.success is True
    assert response.message == "Text extracted successfully"

    # Ensure response.data is not None before accessing content
    assert response.data is not None
    assert len(response.data.content) == (10 * 1024 * 1024 + 1)


# Test File Does Not Exist
def test_file_does_not_exist(_nonexistent_file: str) -> None:
    """Test that a nonexistent file returns an error."""
    processor = DocumentProcessor(_nonexistent_file)
    response = processor.extract_text()

    assert response.success is False
    assert response.message == f"Value error, File not found: {_nonexistent_file}"
    assert response.data is None


# Test Handling of Corrupted Files
@patch("src.processors.document.PyPDFLoader")
def test_handling_corrupted_files(mock_loader: MagicMock, _corrupted_file: str) -> None:
    """Test that a corrupted PDF file is handled properly."""
    mock_loader.return_value.load.side_effect = Exception("File corruption error")
    processor = DocumentProcessor(_corrupted_file)
    response = processor.extract_text()

    assert response.success is False
    assert response.message == "Error processing document"
    assert response.data is None  # Error details should be included


# Test Handling of Empty Files
def test_handling_empty_files(_empty_file: str) -> None:
    """Test that an empty file is processed correctly."""
    processor = DocumentProcessor(_empty_file)
    response = processor.extract_text()

    assert response.success is False  # Empty files are still technically valid
    assert response.message == "No text found in document"
    assert response.data is None


# Test Handling of Unsupported File Formats
def test_handling_unsupported_formats(_unsupported_file: str) -> None:
    """Test that an unsupported file format is rejected properly."""
    processor = DocumentProcessor(_unsupported_file)
    response = processor.extract_text()

    assert response.success is False
    assert (
        response.message
        == "Value error, Unsupported file format. Only PDF, TXT, and DOCX are allowed."
    )
    assert response.data is None
