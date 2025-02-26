import pytest
from unittest.mock import patch, MagicMock
import requests
from fbpyutils_ai.tools.llm import OpenAITool

@patch('fbpyutils_ai.tools.llm.requests.Session.get')
def test_list_models_base(mock_get):
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {
                "name": "text-davinci-003",
                "id": "davinci",
                "version": "3",
                "capabilities": ["text generation"],
                "is_tool": True,
                "is_vision_enabled": False,
                "is_embedding_model": False,
                "has_reasoning_capability": True,
                "context_length": 4096,
                "parameter_count": 175000000000,
                "deprecation_status": False,
                "availability": "available"
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    tool = OpenAITool(model="text-davinci-003", api_key="test_key")

    # Act
    models = tool.list_models(api_base_type="base")

    # Assert
    assert len(models) == 1
    assert models[0]["name"] == "text-davinci-003"
    assert models[0]["is_tool"] is True

@patch('fbpyutils_ai.tools.llm.requests.Session.get')
def test_list_models_invalid_api_base_type(mock_get):
    # Arrange
    tool = OpenAITool(model="text-davinci-003", api_key="test_key")

    # Act & Assert
    with pytest.raises(ValueError):
        tool.list_models(api_base_type="invalid_base")

@patch('fbpyutils_ai.tools.llm.requests.Session.get')
def test_list_models_api_error(mock_get):
    # Arrange
    mock_get.side_effect = requests.exceptions.RequestException("API Error")
    tool = OpenAITool(model="text-davinci-003", api_key="test_key")

    # Act & Assert
    with pytest.raises(requests.exceptions.RequestException):
        tool.list_models(api_base_type="base")