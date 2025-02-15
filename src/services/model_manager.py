from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from tenacity import retry, stop_after_attempt, wait_fixed

from src.utils.my_logging import setup_logger

logger = setup_logger()

from src.config.settings import Config

config = Config()


class ModelManager:
    def __init__(self):
        self.model_provider = config.MODEL_PROVIDER.lower()
        if self.model_provider == "openai":
            self.model = ChatOpenAI(model = 'gpt-3.5-turbo', api_key=config.OPENAI_API_KEY)
        elif self.model_provider == "anthropic":
            self.model = ChatAnthropic(api_key=config.MODEL_PROVIDER)
        else:
            raise ValueError("Invalid model provider")

    def generate_response(self, prompt: str) -> str:
        try:
            return self.model.predict(prompt)
        except Exception as e:
            logger.error(f"Model error: {e}")
            raise
