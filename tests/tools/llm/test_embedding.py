# tests/tools/llm/test_embedding.py
import pytest
import requests
from unittest.mock import patch

# Note: Fixture openai_tool_instance is automatically available from conftest.py

# --- generate_embedding Tests ---

@patch('fbpyutils_ai.tools.llm.OpenAITool._make_request') # Target the method on the class
def test_generate_embedding_success(mock_make_request, openai_tool_instance):
    """Test successful embedding generation."""
    # Arrange
    mock_response = {"data": [{"embedding": [0.1, 0.2, 0.3]}]}
    mock_make_request.return_value = mock_response
    text_to_embed = "This is a test text."

    # Act
    embedding = openai_tool_instance.generate_embedding(text_to_embed)

    # Assert
    mock_make_request.assert_called_once_with(
        f"{openai_tool_instance.api_embed_base.rstrip('/')}/v1/embeddings", # Expect /v1/
        openai_tool_instance.api_headers,
        {"model": openai_tool_instance.embed_model, "input": text_to_embed}
    )
    assert embedding == [0.1, 0.2, 0.3]

@patch('fbpyutils_ai.tools.llm.OpenAITool._make_request')
def test_generate_embedding_api_error(mock_make_request, openai_tool_instance):
    """Test embedding generation failure due to API error."""
    # Arrange
    mock_make_request.side_effect = requests.exceptions.RequestException("API Error")
    text_to_embed = "This is a test text."

    # Act
    embedding = openai_tool_instance.generate_embedding(text_to_embed)

    # Assert
    assert embedding is None

@patch('fbpyutils_ai.tools.llm.OpenAITool._make_request')
def test_generate_embedding_parsing_error(mock_make_request, openai_tool_instance):
    """Test embedding generation failure due to response parsing error."""
    # Arrange
    mock_response = {"invalid_structure": "no data"} # Malformed response
    mock_make_request.return_value = mock_response
    text_to_embed = "This is a test text."

    # Act
    embedding = openai_tool_instance.generate_embedding(text_to_embed)

    # Assert
    assert embedding is None
