from pathlib import Path

from langchain.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from pydantic import ValidationError

from src.models.schemas import APIResponse, DocumentProcessorInput, DocumentResponse
from src.utils.my_logging import setup_logger

logger = setup_logger()


class DocumentProcessor:
    def __init__(self, file_path: str):
        """Initialize with validated file path."""
        try:
            validated_data = DocumentProcessorInput(file_path=file_path)
            self.file_path = Path(validated_data.file_path)
            self.validation_failed = False
        except ValidationError as e:
            logger.error(f"Validation Error: {e}")
            self.validation_failed = True
            error_msg = e.errors()[0]["msg"]
            self.response = APIResponse(success=False, message=error_msg, data=None)

    def extract_text(self) -> APIResponse:
        """Extract text from the document and return structured response."""
        # If validation failed, return the stored response
        if self.validation_failed:
            return self.response

        ext = self.file_path.suffix.lower()
        loader_map = {".pdf": PyPDFLoader, ".txt": TextLoader, ".docx": Docx2txtLoader}

        if ext not in loader_map:
            return APIResponse(
                success=False, message="Unsupported file type", data=None
            )

        try:
            loader = loader_map[ext](str(self.file_path))
            docs = loader.load()
            extracted_text = "\n".join([doc.page_content for doc in docs])

            return APIResponse(
                success=True,
                message="Text extracted successfully",
                data=DocumentResponse(
                    status="success",
                    file_path=str(self.file_path),
                    file_type=ext[1:],  # Remove the dot
                    content=extracted_text,
                ),
            )
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return APIResponse(
                success=False, message="Error processing document", data=str(e)
            )
