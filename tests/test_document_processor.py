import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.models.schemas import APIResponse  # Import APIResponse model
from src.processors.document import DocumentProcessor

# Test Files Directory
TEST_FILES_DIR = "tests/test_files/"


# Helper function to create test files
def create_test_file(file_path, content="Sample text"):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


@pytest.fixture
def pdf_file():
    file_path = os.path.join(TEST_FILES_DIR, "sample.pdf")
    create_test_file(file_path, "This is a test PDF file.")
    return file_path


@pytest.fixture
def docx_file():
    file_path = os.path.join(TEST_FILES_DIR, "sample.docx")
    create_test_file(file_path, "This is a test DOCX file.")
    return file_path


@pytest.fixture
def txt_file():
    file_path = os.path.join(TEST_FILES_DIR, "sample.txt")
    create_test_file(file_path, "This is a test TXT file.")
    return file_path


@pytest.fixture
def empty_file():
    file_path = os.path.join(TEST_FILES_DIR, "empty.txt")
    create_test_file(file_path, "")
    return file_path


@pytest.fixture
def large_file():
    file_path = os.path.join(TEST_FILES_DIR, "large.txt")
    create_test_file(file_path, "A" * (10 * 1024 * 1024 + 1))  # >10MB
    return file_path


@pytest.fixture
def unsupported_file():
    file_path = os.path.join(TEST_FILES_DIR, "unsupported.xyz")
    create_test_file(file_path, "This file has an unsupported extension.")
    return file_path


@pytest.fixture
def corrupted_file():
    file_path = os.path.join(TEST_FILES_DIR, "corrupted.pdf")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(b"\x00\x01\x02")  # Writing invalid content
    return file_path


@pytest.fixture
def nonexistent_file():
    return os.path.join(TEST_FILES_DIR, "nonexistent.txt")


# Test Successful PDF Processing
@patch("src.processors.document.PyPDFLoader")
def test_successful_pdf_processing(mock_loader, pdf_file):
    mock_loader.return_value.load.return_value = [
        MagicMock(page_content="Extracted PDF content")
    ]
    processor = DocumentProcessor(pdf_file)
    response = processor.extract_text()

    assert isinstance(response, APIResponse)
    assert response.success is True
    assert response.message == "Text extracted successfully"
    assert response.data.file_path == pdf_file
    assert response.data.file_type == "pdf"
    assert response.data.content == "Extracted PDF content"


# Test Successful DOCX Processing
@patch("src.processors.document.Docx2txtLoader")
def test_successful_docx_processing(mock_loader, docx_file):
    mock_loader.return_value.load.return_value = [
        MagicMock(page_content="Extracted DOCX content")
    ]
    processor = DocumentProcessor(docx_file)
    response = processor.extract_text()

    assert response.success is True
    assert response.message == "Text extracted successfully"
    assert response.data.file_path == docx_file
    assert response.data.file_type == "docx"
    assert response.data.content == "Extracted DOCX content"


# Test Successful TXT Processing
def test_successful_txt_processing(txt_file):
    processor = DocumentProcessor(txt_file)
    response = processor.extract_text()

    assert response.success is True
    assert response.message == "Text extracted successfully"
    assert response.data.file_path == txt_file
    assert response.data.file_type == "txt"
    assert response.data.content == "This is a test TXT file."


# Test Handling of Corrupted Files
@patch("src.processors.document.PyPDFLoader")
def test_handling_corrupted_files(mock_loader, corrupted_file):
    mock_loader.return_value.load.side_effect = Exception("File corruption error")
    processor = DocumentProcessor(corrupted_file)
    response = processor.extract_text()

    assert response.success is False
    assert response.message == "Error processing document"
    assert response.data is not None  # Error details should be included


# Test Handling of Unsupported File Formats
def test_handling_unsupported_formats(unsupported_file):
    processor = DocumentProcessor(unsupported_file)
    response = processor.extract_text()

    assert response.success is False
    assert (
        response.message
        == "Value error, Unsupported file format. Only PDF, TXT, and DOCX are allowed."
    )
    assert response.data is None


# Test Handling of Empty Files
def test_handling_empty_files(empty_file):
    processor = DocumentProcessor(empty_file)
    response = processor.extract_text()

    assert response.success is True  # Empty files are still technically valid
    assert response.message == "Text extracted successfully"
    assert response.data.content == ""


# Test Handling of Large Files (>10MB)
def test_handling_large_files(large_file):
    processor = DocumentProcessor(large_file)
    response = processor.extract_text()

    assert response.success is True
    assert response.message == "Text extracted successfully"
    assert len(response.data.content) == (10 * 1024 * 1024 + 1)


# Test File Does Not Exist
def test_file_does_not_exist(nonexistent_file):
    processor = DocumentProcessor(nonexistent_file)
    response = processor.extract_text()

    assert response.success is False
    assert response.message == f"Value error, File not found: {nonexistent_file}"
    assert response.data is None