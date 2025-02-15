import asyncio
import socket

import httpx
import requests
from langchain_anthropic import ChatAnthropic
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_openai import ChatOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from src.config.settings import ConfigSettings
from src.utils.my_logging import setup_logger

logger = setup_logger()
config = ConfigSettings()


class ModelManager:
    def __init__(self):
        rate_limiter = InMemoryRateLimiter(
            requests_per_second=config.REQUESTS_PER_SECOND,
            check_every_n_seconds=config.CHECK_EVERY_N_SECONDS,
            max_bucket_size=config.MAX_BUCKET_SIZE,
        )
        self.model_provider = config.MODEL_PROVIDER.lower()
        if self.model_provider == "openai":
            self.model = ChatOpenAI(
                model=config.OPENAI_MODEL,
                api_key=config.OPENAI_API_KEY.get_secret_value(),
                rate_limiter=rate_limiter,
            )
        elif self.model_provider == "anthropic":
            self.model = ChatAnthropic(
                mode=config.ANTHROPIC_MODEL,
                api_key=config.MODEL_PROVIDER.get_secret_value(),
            )
        else:
            raise ValueError("Invalid model provider")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(Exception),
    )
    def generate_response(self, prompt: str) -> str:
        try:
            return self.model.predict(prompt)
        except (
            requests.exceptions.Timeout,
            socket.timeout,
            httpx.TimeoutException,
            asyncio.TimeoutError,
        ) as e:
            logger.error("Timeout error: %s", e)
            raise
        except Exception as e:
            logger.error("Model error: %s", e)
            raise
