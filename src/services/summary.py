import os
import time
from pathlib import Path
from typing import List, Union

import langid
from dotenv import load_dotenv
from langchain.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel, ValidationError
from tenacity import retry, stop_after_attempt, wait_fixed

from src.utils.my_logging import setup_logger

logger = setup_logger()

from src.services.model_manager import ModelManager

class SummaryGenerator:
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager

    def chunk_text(self, text: str) -> List[str]:
        chunk_size, chunk_overlap = 1000, 100
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        return splitter.split_text(text)

    def generate_summary(self, text: str, summary_type: str = "brief") -> str:
        TEMPLATES = {
                "brief": "Provide a short and concise summary of the following text: {text}",
                "detailed": "Provide a detailed and comprehensive summary of the following text: {text}",
                "bullet points": "Summarize the following text in bullet points: {text}",
                "technical": "Provide a technical summary focusing on key concepts and terminologies: {text}",
                "layman": "Explain the following text in a simple manner suitable for a general audience: {text}",
            }

        chunks = self.chunk_text(text)
        summary_results = []

        for chunk in chunks:

            prompt = TEMPLATES.get(summary_type, "").format(text=chunk)
            print(prompt)

            try:
                # TODO oepnAI token expire
                # response = self.model_manager.generate_response(prompt)
                response = "This is the summarization"
                summary_results.append(response)
            except Exception as e:
                logger.error(f"Error generating summary: {e}")
                continue

        return "\n".join(summary_results)
