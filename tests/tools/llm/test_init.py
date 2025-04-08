# tests/tools/llm/test_init.py
import pytest
from fbpyutils_ai.tools.llm import OpenAITool

# Note: Fixtures mock_env_api_key and mock_env_api_base are automatically available
# from the conftest.py file in the same directory.

def test_init_with_api_key_arg():
    """Test initialization with API key provided as argument."""
    tool = OpenAITool(model_id="test-model", api_key="arg_test_key")
    assert tool.api_key == "arg_test_key"
    assert tool.api_base == "https://api.openai.com" # Default

def test_init_with_api_key_env(mock_env_api_key):
    """Test initialization with API key from environment variable."""
    tool = OpenAITool(model_id="test-model")
    assert tool.api_key == "env_test_key"

def test_init_no_api_key_raises_error(monkeypatch):
    """Test initialization raises ValueError if no API key is found."""
    # Ensure the environment variable is unset for this specific test
    monkeypatch.delenv("FBPY_OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="API key is required"):
        OpenAITool(model_id="test-model") # No key arg, env explicitly unset

def test_init_with_api_base_arg():
    """Test initialization with API base provided as argument."""
    tool = OpenAITool(model_id="test-model", api_key="test_key", api_base="https://arg-api.example.com")
    assert tool.api_base == "https://arg-api.example.com"

def test_init_with_api_base_env(mock_env_api_base):
    """Test initialization with API base from environment variable."""
    tool = OpenAITool(model_id="test-model", api_key="test_key")
    assert tool.api_base == "https://env-api.example.com"

def test_init_anthropic_headers():
    """Test Anthropic specific headers are added when api_base matches."""
    tool = OpenAITool(model_id="claude-3", api_key="test_key", api_base="https://api.anthropic.com/v1")
    assert "x-api-key" in tool.api_headers
    assert "anthropic-version" in tool.api_headers
    assert tool.api_headers["x-api-key"] == "test_key"

def test_init_defaults():
    """Test default values for various parameters."""
    tool = OpenAITool(model_id="test-model", api_key="test_key")
    assert tool.model_id == "test-model"
    assert tool.embed_model == "test-model"
    assert tool.api_embed_base == "https://api.openai.com"
    assert tool.api_embed_key == "test_key"
    assert tool.vision_model == "test-model"
    assert tool.api_vision_base == "https://api.openai.com"
    assert tool.api_vision_key == "test_key"
    assert tool.timeout == 300
    assert tool.retries == 3

def test_init_custom_values():
    """Test custom values for various parameters."""
    tool = OpenAITool(
        model_id="main-model",
        api_key="main_key",
        api_base="https://main.example.com",
        embed_model="embed-model",
        api_embed_base="https://embed.example.com",
        api_embed_key="embed_key",
        vision_model="vision-model",
        api_vision_base="https://vision.example.com",
        api_vision_key="vision_key",
        timeout=60,
        session_retries=5,
    )
    assert tool.model_id == "main-model"
    assert tool.api_key == "main_key"
    assert tool.api_base == "https://main.example.com"
    assert tool.embed_model == "embed-model"
    assert tool.api_embed_base == "https://embed.example.com"
    assert tool.api_embed_key == "embed_key"
    assert tool.vision_model == "vision-model"
    assert tool.api_vision_base == "https://vision.example.com"
    assert tool.api_vision_key == "vision_key"
    assert tool.timeout == 60
    assert tool.retries == 5
