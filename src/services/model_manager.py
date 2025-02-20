import asyncio
import socket
from abc import ABC, abstractmethod

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


class Model(ABC):
    """Abstract base class for AI models."""

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generate a response based on the given prompt."""
        pass


class ModelManager:
    """Factory class to get the appropriate model based on configuration."""

    @staticmethod
    def get_model(model_type) -> Model:
        if model_type == "openai":
            return OpenAIModel()
        elif model_type == "anthropic":
            return AnthropicModel()
        else:
            raise ValueError(f"Invalid model provider: {model_type}")


class OpenAIModel(Model):
    """OpenAI model integration."""

    def __init__(self):
        self.rate_limiter = InMemoryRateLimiter(
            requests_per_second=config.REQUESTS_PER_SECOND,
            check_every_n_seconds=config.CHECK_EVERY_N_SECONDS,
            max_bucket_size=config.MAX_BUCKET_SIZE,
        )
        self.model = ChatOpenAI(
            model=config.OPENAI_MODEL,
            api_key=config.OPENAI_API_KEY.get_secret_value(),
            rate_limiter=self.rate_limiter,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(0.1),
        retry=retry_if_exception_type(Exception),
    )
    def generate_response(self, prompt: str) -> str:
        try:
            return self.model.predict(prompt)
        except (
            requests.Timeout,
            socket.timeout,
            httpx.TimeoutException,
            asyncio.TimeoutError,
        ) as e:
            logger.error("Timeout error: %s", e)
            raise
        except Exception as e:
            logger.error("Model error: %s", e)
            raise


class AnthropicModel(Model):
    """Anthropic model integration."""

    def __init__(self):
        self.rate_limiter = InMemoryRateLimiter(
            requests_per_second=config.REQUESTS_PER_SECOND,
            check_every_n_seconds=config.CHECK_EVERY_N_SECONDS,
            max_bucket_size=config.MAX_BUCKET_SIZE,
        )
        self.model = ChatAnthropic(
            model=config.ANTHROPIC_MODEL,
            api_key=config.ANTHROPIC_API_KEY.get_secret_value(),  # Fixed API key reference
            rate_limiter=self.rate_limiter,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(Exception),
    )
    def generate_response(self, prompt: str) -> str:
        try:
            return self.model.predict(prompt)
        except (
            requests.Timeout,
            socket.timeout,
            httpx.TimeoutException,
            asyncio.TimeoutError,
        ) as e:
            logger.error("Timeout error: %s", e)
            raise
        except Exception as e:
            logger.error("Model error: %s", e)
            raise
