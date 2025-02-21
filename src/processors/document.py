from pathlib import Path

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from pydantic import ValidationError

from src.models.schemas import APIResponse, DocumentProcessorInput, DocumentResponse
from src.utils.my_logging import setup_logger

logger = setup_logger()


class DocumentProcessor:
    def __init__(self, file_path: str):
        """Initialize with validated file path."""
        self.file_path = file_path

    def validate_file(self) -> APIResponse | None:
        try:
            DocumentProcessorInput(file_path=self.file_path)
            return None
        except ValidationError as err:
            logger.error("Validation Error: %s", err)
            message = ",".join([error["msg"] for error in err.errors()])
            response = APIResponse(success=False, code=400, message=message, data=None)
            return response

    def extract_text(self) -> APIResponse:
        """Extract text from the document and return structured response."""
        # If validation failed, return the stored response
        validation_reponse = self.validate_file()
        if validation_reponse:
            return validation_reponse

        print("!!", self.file_path)
        ext = Path(self.file_path).suffix.lower()
        loader_map = {".pdf": PyPDFLoader, ".txt": TextLoader, ".docx": Docx2txtLoader}

        try:
            loader = loader_map[ext](self.file_path)
            docs = loader.load()
            extracted_text = "\n".join([doc.page_content for doc in docs])

            if not extracted_text.strip():
                return APIResponse(
                    success=False,
                    code=204,
                    message="No text found in document",
                    data=None,
                )

            return APIResponse(
                success=True,
                code=200,
                message="Text extracted successfully",
                data=DocumentResponse(
                    file_path=str(self.file_path),
                    file_type=ext[1:],  # Remove the dot
                    content=extracted_text,
                ),
            )
        except Exception as err:
            logger.error("Error processing document: %s", err)
            return APIResponse(
                success=False, code=500, message="Error processing document", data=None
            )
