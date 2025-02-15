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


class SummaryPromptManager:
    TEMPLATES = {
        "brief": "Provide a short and concise summary of the following text: {text}",
        "detailed": "Provide a detailed and comprehensive summary of the following text: {text}",
        "bullet points": "Summarize the following text in bullet points: {text}",
        "technical": "Provide a technical summary focusing on key concepts and terminologies: {text}",
        "layman": "Explain the following text in a simple manner suitable for a general audience: {text}",
    }

    def get_prompt(cls, summary_type: str, text: str) -> str:
        return cls.TEMPLATES.get(summary_type, cls.TEMPLATES["brief"]).format(text=text)


class SummaryGenerator:
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager

    def get_chunk_size(self, text: str) -> str:
        language, _ = langid.classify(text)
        language_settings = {
            "en": (1000, 200),  # English: Large chunks
            "zh": (500, 100),  # Chinese: Small chunks
            "ar": (600, 150),  # Arabic: Medium chunks
            "fr": (800, 200),  # French: Medium chunks
            "de": (800, 200),  # German: Medium chunks
            "ja": (400, 100),  # Japanese: Small chunks
        }
        return language_settings.get(language, (600, 150))

    def chunk_text(self, text: str) -> List[str]:
        chunk_size, chunk_overlap = self.get_chunk_size(text)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        return splitter.split_text(text)

    def generate_summary(self, text: str, summary_type: str = "brief") -> str:
        chunks = self.chunk_text(text)
        summary_results = []

        for chunk in chunks:

            prompt = SummaryPromptManager.get_prompt(summary_type, chunk)
            try:
                response = self.model_manager.generate_response(prompt)
                summary_results.append(response)
            except Exception as e:
                logger.error(f"Error generating summary: {e}")
                continue

        return "\n".join(summary_results)
