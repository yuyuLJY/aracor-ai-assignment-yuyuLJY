import asyncio
import socket
from typing import List

import httpx
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config.settings import ConfigSettings
from src.models.schemas import APIResponse, SummaryResponse
from src.services.model_manager import ModelManager
from src.utils.my_logging import setup_logger

logger = setup_logger()
config = ConfigSettings()


class SummaryGenerator:
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager

    def chunk_text(self, text: str) -> List[str]:
        # would be better if identify language type
        chunk_size = config.CHUNK_SIZE
        chunk_overlap = config.CHUNK_OVERLAP
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        return splitter.split_text(text)

    def get_prompt(self, summary_type: str) -> str:
        templates = {
            "brief": """Provide a short and concise \
                    summary of the following text: {text}""",
            "detailed": """Provide a detailed and comprehensive summary \
                    of the following text: {text}""",
            "bullet points": """Summarize the following text \
                        in bullet points: {text}""",
            "technical": """Provide a technical summary focusing on \
                    key concepts and terminologies: {text}""",
            "layman": """Explain the following text in a simple manner suitable \
                    for a general audience: {text}""",
        }
        return templates.get(summary_type, "")

    def generate_summary(self, text: str, summary_type: str = "brief") -> str:

        chunks = self.chunk_text(text)
        summary_results = []

        for chunk in chunks:
            prompt = self.get_prompt(summary_type).format(text=chunk)
            try:
                response = self.model_manager.generate_response(prompt)
                # response = f"####### This is the summarization {chunk}"
                summary_results.append(response)
            except (
                requests.exceptions.Timeout,
                socket.timeout,
                httpx.TimeoutException,
                asyncio.TimeoutError,
            ) as e:
                logger.warning("Timeout occurred: %s. Returning partial results.", e)
                return APIResponse(
                    success=True,
                    code=500,
                    message=f"Timeout occurred: {e}. Returning partial results.",
                    data=SummaryResponse(
                        status="error",  # return partial result, use 'error' to indicate it
                        summary="\n".join(summary_results),
                    ),
                )
            except Exception as e:
                logger.error("Error generating summary: %s", e)
                return APIResponse(
                    success=False,
                    code=500,
                    message="Error generating summary: %s" % e,
                    data=None,
                )

        return APIResponse(
            success=True,
            code=200,
            message=f": Generate summarization successfully",
            data=SummaryResponse(
                status="success",
                summary="\n".join(summary_results),
            ),
        )
