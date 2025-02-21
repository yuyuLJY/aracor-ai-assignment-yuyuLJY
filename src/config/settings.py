from dotenv import load_dotenv
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)


class ConfigSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    # Model Configuration
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    OPENAI_API_KEY: SecretStr
    ANTHROPIC_API_KEY: SecretStr

    # Rate Limiter Configuration
    REQUESTS_PER_SECOND: float = 1
    CHECK_EVERY_N_SECONDS: float = 1
    MAX_BUCKET_SIZE: int = 10

    # Text Splitting Configuration
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100

    @field_validator("OPENAI_API_KEY", "ANTHROPIC_API_KEY", mode="before")
    @classmethod
    def validate_secret(cls, value: str) -> str:
        """Ensure API keys are not empty."""
        if not value or value.strip() == "":
            raise ValueError("API key cannot be empty")
        return value
