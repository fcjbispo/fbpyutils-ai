# tests/tools/llm/conftest.py
import pytest
from fbpyutils_ai.tools.llm import OpenAITool

@pytest.fixture
def mock_env_api_key(monkeypatch):
    """Fixture to mock environment variable for API key."""
    monkeypatch.setenv("FBPY_OPENAI_API_KEY", "env_test_key")

@pytest.fixture
def mock_env_api_base(monkeypatch):
    """Fixture to mock environment variable for API base."""
    monkeypatch.setenv("FBPY_OPENAI_API_BASE", "https://env-api.example.com")

@pytest.fixture
def openai_tool_instance():
    """Provides a basic instance of OpenAITool for testing methods."""
    # Use a dummy key directly to avoid env dependency in most tests
    return OpenAITool(model_id="test-model", api_key="test_key")
