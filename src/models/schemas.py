from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class APIResponse(BaseModel):
    success: bool
    code: int
    message: str
    data: Optional[Any] = None


class DocumentProcessorInput(BaseModel):
    file_path: str

    @field_validator("file_path")
    @classmethod
    def validate_file_exists(cls, value):
        path = Path(value)
        if not path.exists():
            raise ValueError(f"File not found: {value}")
        if path.suffix.lower() not in {".pdf", ".txt", ".docx"}:
            raise ValueError(
                "Unsupported file format. Only PDF, TXT, and DOCX are allowed."
            )


class DocumentResponse(BaseModel):
    # status: Literal["success", "error"]
    file_path: str
    file_type: str
    content: Optional[str] = Field(
        None, description="Extracted text content from the document"
    )


class SummaryResponse(BaseModel):
    status: Literal["success", "error"]
    summary: str
