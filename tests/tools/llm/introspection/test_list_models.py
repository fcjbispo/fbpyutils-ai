# tests/tools/llm/introspection/test_list_models.py
import pytest
import json
import requests
from unittest.mock import patch, MagicMock, ANY # Import ANY
from fbpyutils_ai.tools.llm import OpenAITool
from tests.tools.llm.introspection.common import MOCK_VALID_CAPABILITIES, MOCK_SCHEMA, create_mock_response

@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get')
def test_list_models_base(mock_get: MagicMock, openai_tool_instance: OpenAITool) -> None:
    """Test listing models for the base API."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [{"name": "text-davinci-003", "id": "davinci"}]}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    
    models = openai_tool_instance.list_models(api_base_type="base")
    
    assert len(models) == 1
    assert models[0]["id"] == "davinci"
    mock_get.assert_called_once_with(
        f"{openai_tool_instance.api_base.rstrip('/')}/v1/models",
        headers=openai_tool_instance.api_headers,
        timeout=openai_tool_instance.timeout
    )

@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get')
def test_list_models_embed(mock_get: MagicMock) -> None:
    """Test listing models for the embed API."""
    tool = OpenAITool(model_id="m", api_key="k", api_embed_base="https://embed.example.com", api_embed_key="ek") # Added embed key
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [{"id": "embed-model-1"}]}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    expected_headers = tool.api_headers.copy() # Get headers after potential init adjustments
    expected_headers["Authorization"] = f"Bearer {tool.api_embed_key}"

    models = tool.list_models(api_base_type="embed_base")
    
    mock_get.assert_called_once_with(
        "https://embed.example.com/v1/models", # Expect /v1/
        headers=expected_headers,
        timeout=tool.timeout
    )
    assert len(models) == 1
    assert models[0]["id"] == "embed-model-1"

@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get')
def test_list_models_vision(mock_get: MagicMock) -> None:
    """Test listing models for the vision API."""
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [{"id": "vision-model-1"}]}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    tool = OpenAITool(model_id="m", api_key="k", api_vision_base="https://vision.example.com", api_vision_key="vk")
    expected_headers = tool.api_headers.copy()
    # Ensure correct key is used for assertion if different
    expected_headers["Authorization"] = f"Bearer {tool.api_vision_key}"

    # Act
    models = tool.list_models(api_base_type="vision_base")

    # Assert
    # Assert call includes /v1/ and uses the correct headers variable
    mock_get.assert_called_once_with(
        "https://vision.example.com/v1/models",
        headers=expected_headers, # Use the adjusted headers from the test setup
        timeout=tool.timeout
    )
    assert len(models) == 1
    assert models[0]["id"] == "vision-model-1"


@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get')
def test_list_models_invalid_api_base_type(
    mock_get: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test list_models raises ValueError for invalid api_base_type."""
    # Arrange
    tool = openai_tool_instance

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid api_base_type"):
        tool.list_models(api_base_type="invalid_base")

@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get')
def test_list_models_api_error(
    mock_get: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test list_models raises RequestException on API error."""
    # Arrange
    mock_get.side_effect = requests.exceptions.RequestException("API Error")
    tool = openai_tool_instance

    # Act & Assert
    with pytest.raises(requests.exceptions.RequestException):
        tool.list_models(api_base_type="base")

@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get')
def test_list_models_empty_data(
    mock_get: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test list_models handles empty data list from API."""
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": []} # Empty data list
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    tool = openai_tool_instance

    # Act
    models = tool.list_models(api_base_type="base")

    # Assert
    mock_get.assert_called_once()
    assert models == [] # Should return an empty list

@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get')
def test_list_models_missing_id(
    mock_get: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test list_models handles entries missing the 'id' field gracefully (should skip them)."""
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {"name": "model-without-id"}, # Entry missing 'id'
            {"id": "model-with-id"}
        ]
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    tool = openai_tool_instance

    # Act
    models = tool.list_models(api_base_type="base")

    # Assert
    mock_get.assert_called_once()
    assert len(models) == 1 # Only the entry with 'id' should be returned
    assert models[0]["id"] == "model-with-id"

# --- New list_models format tests ---

@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get')
def test_list_models_direct_list_format(
    mock_get: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test list_models handles direct list response format."""
    # Arrange
    mock_response = MagicMock()
    # Simulate API returning a direct list
    mock_response.json.return_value = [{"id": "direct-list-model-1"}, {"id": "direct-list-model-2"}]
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    tool = openai_tool_instance

    # Act
    models = tool.list_models(api_base_type="base")

    # Assert
    mock_get.assert_called_once()
    assert len(models) == 2
    assert models[0]["id"] == "direct-list-model-1"
    assert models[1]["id"] == "direct-list-model-2"

@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get')
def test_list_models_ollama_format(
    mock_get: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test list_models handles Ollama-like response format."""
    # Arrange
    mock_response = MagicMock()
    # Simulate API returning Ollama-like structure
    mock_response.json.return_value = {
        "models": [
            {"name": "ollama-model:latest", "modified_at": "...", "size": 123, "id": "ollama-model:latest"}, # Ollama often uses name as id
            {"name": "another-model:7b", "modified_at": "...", "size": 456, "id": "another-model:7b"}
        ]
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    tool = openai_tool_instance

    # Act
    models = tool.list_models(api_base_type="base")

    # Assert
    mock_get.assert_called_once()
    assert len(models) == 2
    assert models[0]["id"] == "ollama-model:latest"
    assert models[1]["id"] == "another-model:7b"

# --- End new list_models format tests ---
@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get')
def test_list_models_simple_list_format(
    mock_get: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test list_models handles simple list of strings response format."""
    # Arrange
    mock_response = MagicMock()
    # Simulate API returning a simple list of strings
    mock_response.json.return_value = ["model-name-1", "model-name-2"]
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    tool = openai_tool_instance

    # Act
    models = tool.list_models(api_base_type="base")

    # Assert
    mock_get.assert_called_once()
    assert len(models) == 2
    # The function should convert strings to dicts with 'id'
    assert models[0]["id"] == "model-name-1"
    assert models[1]["id"] == "model-name-2"

@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get')
def test_list_models_unrecognized_format(
    mock_get: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test list_models handles unrecognized response format."""
    # Arrange
    mock_response = MagicMock()
    # Simulate API returning an unexpected format
    mock_response.json.return_value = {"unexpected_key": "some_value"}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    tool = openai_tool_instance

    # Act
    models = tool.list_models(api_base_type="base")

    # Assert
    mock_get.assert_called_once()
    assert models == [] # Should return empty list for unrecognized format

@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get')
def test_list_models_json_decode_error(
    mock_get: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test list_models raises JSONDecodeError on invalid JSON response."""
    # Arrange
    mock_response = MagicMock()
    # Simulate json() raising an error
    mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
    mock_response.raise_for_status = MagicMock()
    # Provide some text for the logging fallback
    mock_response.text = "This is not JSON"
    mock_get.return_value = mock_response
    tool = openai_tool_instance

    # Act & Assert
    with pytest.raises(json.JSONDecodeError):
        tool.list_models(api_base_type="base")
    mock_get.assert_called_once()
# - list_models_direct_list_format
# - list_models_ollama_format
# - list_models_simple_list_format
# - list_models_unrecognized_format
# - list_models_json_decode_error

# Note: For brevity, I'm showing the pattern with 2 tests. The full file would include all list_models tests
# from the original file following this same structure.
