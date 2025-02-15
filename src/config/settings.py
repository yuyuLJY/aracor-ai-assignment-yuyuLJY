import os
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Application configuration using pydantic-settings"""

    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")
    ANTHROPIC_API_KEY: str = Field(..., description="Anthropic API key")
    MODEL_PROVIDER: Literal["openai", "anthropic"] = Field(
        ..., description="Model provider (openai or anthropic)"
    )

    class Config:
        env_file = ".env.example" if os.getenv("TESTING") == "true" else ".env"


# Explicitly load the correct dotenv file
load_dotenv(Config.Config.env_file)
