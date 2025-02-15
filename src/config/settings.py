from pydantic import BaseModel, BaseSettings, ValidationError


class Config(BaseSettings):
    openai_api_key: str
    anthropic_api_key: str
    model_provider: str  # "openai" or "anthropic"

    class Config:
        env_file = ".env"
