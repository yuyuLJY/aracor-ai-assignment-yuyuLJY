import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

# from src.config.settings import Config  # Import your updated Config class

# Ensure tests use .env.example
# @pytest.fixture(scope="session", autouse=True)
# def set_testing_env():
#     os.environ["TESTING"] = "true"  # Ensure TESTING=true before Config is loaded


# Test case: Successful loading from .env.example
# def test_config_success():
#     config = Config() # TODO the class use .env rather than .env.example even though I set os.environ["TESTING"] = "true"
#     assert config.OPENAI_API_KEY == "your_real_openai_api_key"
#     assert config.ANTHROPIC_API_KEY == "your_real_anthropic_api_key"
#     assert config.MODEL_PROVIDER == "openai"

# # Test case: Missing required environment variables
# def test_config_missing_env_vars():
#     with patch.dict("os.environ", {}, clear=True):  # Simulate empty environment
#         with pytest.raises(ValidationError) as exc_info:
#             Config()

#         errors = exc_info.value.errors()
#         assert len(errors) == 3  # Expecting 3 missing variables
#         assert errors[0]["loc"] == ("openai_api_key",)
#         assert errors[1]["loc"] == ("anthropic_api_key",)
#         assert errors[2]["loc"] == ("model_provider",)

# # Test case: Invalid model provider value
# def test_config_invalid_model_provider():
#     with patch.dict("os.environ", {
#         "OPENAI_API_KEY": "dummy_openai_key",
#         "ANTHROPIC_API_KEY": "dummy_anthropic_key",
#         "MODEL_PROVIDER": "invalid_provider"
#     }):
#         with pytest.raises(ValidationError) as exc_info:
#             Config()

#         assert "invalid value" in str(exc_info.value)
