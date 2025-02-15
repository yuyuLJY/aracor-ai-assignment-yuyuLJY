from dotenv import load_dotenv
from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class ConfigSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    # Model Configuration
    MODEL_PROVIDER: str
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    OPENAI_API_KEY: SecretStr
    ANTHROPIC_API_KEY: SecretStr

    # Rate Limiter Configuration
    REQUESTS_PER_SECOND: float = 0.05
    CHECK_EVERY_N_SECONDS: float = 0.1
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

    @field_validator("MODEL_PROVIDER", mode="before")
    @classmethod
    def validate_required_fields(cls, value: str) -> str:
        """Ensure required fields are present and not empty."""
        if value is None or not isinstance(value, str) or value.strip() == "":
            raise ValueError("MODEL_PROVIDER cannot be empty or missing")
        return value
