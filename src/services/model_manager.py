from langchain.llms import Anthropic, OpenAI
from tenacity import retry, stop_after_attempt, wait_fixed

from src.utils.my_logging import setup_logger

logger = setup_logger()

from src.config.settings import Config

config = Config()


class ModelManager:
    def __init__(self):
        self.model_provider = config.model_provider.lower()
        if self.model_provider == "openai":
            self.model = OpenAI(api_key=config.openai_api_key)
        elif self.model_provider == "anthropic":
            self.model = Anthropic(api_key=config.anthropic_api_key)
        else:
            raise ValueError("Invalid model provider")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def generate_response(self, prompt: str) -> str:
        try:
            return self.model.predict(prompt)
        except Exception as e:
            logger.error(f"Model error: {e}")
            raise
