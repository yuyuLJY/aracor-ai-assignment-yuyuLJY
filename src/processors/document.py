import os
import time
from typing import Union, List
from pathlib import Path
from langchain.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader

from src.utils.my_logging import setup_logger
logger = setup_logger()

class DocumentProcessor:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        
    def extract_text(self) -> str:
        if not self.file_path.exists():
            logger.error(f"File not found: {self.file_path}")
            return ""
        
        ext = self.file_path.suffix.lower()
        try:
            if ext == ".pdf":
                loader = PyPDFLoader(str(self.file_path))
            elif ext == ".txt":
                loader = TextLoader(str(self.file_path))
            elif ext == ".docx":
                loader = Docx2txtLoader(str(self.file_path))
            else:
                raise ValueError("Unsupported file format")
            
            docs = loader.load()
            return "\n".join([doc.page_content for doc in docs])
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return ""