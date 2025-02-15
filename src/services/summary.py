from typing import List

import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.models.schemas import APIResponse, SummaryResponse
from src.services.model_manager import ModelManager
from src.utils.my_logging import setup_logger

logger = setup_logger()


class SummaryGenerator:
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager

    def chunk_text(self, text: str) -> List[str]:
        chunk_size, chunk_overlap = 2000, 100
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )
        return splitter.split_text(text)

    def generate_summary(self, text: str, summary_type: str = "brief") -> str:
        templates = {
            "brief": """Provide a short and concise \
                    summary of the following text: {text}""",
            "detailed": """Provide a detailed and comprehensive summary \
                    of the following text: {text}""",
            "bullet points": """Summarize the following text in bullet points: {text}""",
            "technical": """Provide a technical summary focusing on \
                    key concepts and terminologies: {text}""",
            "layman": """Explain the following text in a simple manner suitable \
                    for a general audience: {text}""",
        }

        chunks = self.chunk_text(text)
        summary_results = []

        for chunk in chunks:

            prompt = templates.get(summary_type, "").format(text=chunk)
            print("#" * 15, prompt)

            try:
                # response = self.model_manager.generate_response(prompt)
                response = f"####### This is the summarization {chunk}"
                summary_results.append(response)
            except openai.error.Timeout as timeout_err:
                logger.warning(
                    "Timeout occurred: %s. Returning partial results.", timeout_err
                )
                return APIResponse(
                    success=True,
                    code=500,
                    message=f"Timeout occurred: {timeout_err}. Returning partial results.",
                    data=SummaryResponse(
                        status="error",
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
