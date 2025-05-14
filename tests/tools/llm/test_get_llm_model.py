import pytest
from unittest.mock import patch, MagicMock

from fbpyutils_ai.tools.llm.utils import get_llm_model
from fbpyutils_ai.tools import LLMServiceModel

@patch('os.environ.get')
def test_get_llm_model_success_with_env_var(mock_getenv):
    """
    Test successful retrieval of LLM model when API base URL is in environment variable.
    """
    mock_getenv.side_effect = lambda key, default=None: "http://env.example.com" if key == "OPENAI_API_BASE_URL" else "fake_api_key" if key == "OPENAI_API_KEY" else default

    llm_providers = [
        {"provider": "openai", "api_base_url": "http://default.example.com", "env_api_key": "OPENAI_API_KEY"},
        {"provider": "anthropic", "api_base_url": "http://anthropic.example.com", "env_api_key": "ANTHROPIC_API_KEY"},
    ]
    provider_id = "openai"
    model_id = "gpt-4"

    model = get_llm_model(provider_id, model_id, llm_providers)

    mock_getenv.assert_any_call("OPENAI_API_BASE_URL", "http://default.example.com")
    mock_getenv.assert_any_call("OPENAI_API_KEY")
    assert isinstance(model, LLMServiceModel)
    assert model.provider == provider_id
    assert model.api_base_url == "http://env.example.com"
    assert model.api_key == "fake_api_key"
    assert model.model_id == model_id

@patch('os.environ.get')
def test_get_llm_model_success_with_default_url(mock_getenv):
    """
    Test successful retrieval of LLM model when API base URL is NOT in environment variable.
    """
    mock_getenv.side_effect = lambda key, default=None: "fake_api_key" if key == "ANTHROPIC_API_KEY" else default

    llm_providers = [
        {"provider": "openai", "api_base_url": "http://default.example.com", "env_api_key": "OPENAI_API_KEY"},
        {"provider": "anthropic", "api_base_url": "http://anthropic.example.com", "env_api_key": "ANTHROPIC_API_KEY"},
    ]
    provider_id = "anthropic"
    model_id = "claude-3"

    model = get_llm_model(provider_id, model_id, llm_providers)

    mock_getenv.assert_any_call("ANTHROPIC_API_BASE_URL", "http://anthropic.example.com")
    mock_getenv.assert_any_call("ANTHROPIC_API_KEY")
    assert isinstance(model, LLMServiceModel)
    assert model.provider == provider_id
    assert model.api_base_url == "http://anthropic.example.com"
    assert model.api_key == "fake_api_key"
    assert model.model_id == model_id

@patch('os.environ.get')
def test_get_llm_model_provider_not_found(mock_getenv):
    """
    Test case where the provider is not found in the list.
    """
    mock_getenv.return_value = None # Simulate no env vars set

    llm_providers = [
        {"provider": "openai", "api_base_url": "http://default.example.com", "env_api_key": "OPENAI_API_KEY"},
    ]
    provider_id = "non_existent_provider"
    model_id = "some_model"

    model = get_llm_model(provider_id, model_id, llm_providers)

    assert model is None
    mock_getenv.assert_not_called() # No env vars should be checked if provider not found
