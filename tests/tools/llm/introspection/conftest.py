# tests/tools/llm/introspection/conftest.py
import pytest
from unittest.mock import MagicMock
from fbpyutils_ai.tools.llm import OpenAITool

@pytest.fixture
def openai_tool_instance():
    """Fixture providing a basic OpenAITool instance for testing."""
    return OpenAITool(model_id="test-model", api_key="test-key")
