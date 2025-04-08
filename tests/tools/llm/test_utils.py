# tests/tools/llm/test_utils.py
import pytest
from unittest.mock import patch, MagicMock

# Note: Fixture openai_tool_instance is automatically available from conftest.py

# --- generate_tokens Tests ---

@patch('fbpyutils_ai.tools.llm._utils.tiktoken.encoding_for_model') # Target new location
def test_generate_tokens_success(mock_encoding_for_model, openai_tool_instance):
    """Test successful token generation."""
    # Arrange
    mock_encoder = MagicMock()
    mock_encoder.encode.return_value = [101, 2000, 102]
    mock_encoding_for_model.return_value = mock_encoder
    text = "Sample text"

    # Act
    tokens = openai_tool_instance.generate_tokens(text)

    # Assert
    mock_encoding_for_model.assert_called_once_with(openai_tool_instance.model_id)
    mock_encoder.encode.assert_called_once_with(text)
    assert tokens == [101, 2000, 102]

@patch('fbpyutils_ai.tools.llm._utils.tiktoken.encoding_for_model') # Target new location
@patch('fbpyutils_ai.tools.llm._utils.tiktoken.get_encoding') # Target new location
def test_generate_tokens_model_not_found_fallback(mock_get_encoding, mock_encoding_for_model, openai_tool_instance):
    """Test token generation fallback to default encoding if model not found."""
    # Arrange
    mock_encoding_for_model.side_effect = KeyError("Model not found")
    mock_default_encoder = MagicMock()
    mock_default_encoder.encode.return_value = [500, 600]
    mock_get_encoding.return_value = mock_default_encoder
    text = "Sample text"

    # Act
    tokens = openai_tool_instance.generate_tokens(text)

    # Assert
    mock_encoding_for_model.assert_called_once_with(openai_tool_instance.model_id)
    mock_get_encoding.assert_called_once_with("cl100k_base")
    mock_default_encoder.encode.assert_called_once_with(text)
    assert tokens == [500, 600]

# --- _sanitize_json_response Tests ---

def test_sanitize_json_response_success(openai_tool_instance):
    """Test successful extraction of JSON from markers."""
    raw_response = "Some text before ```json\n{\"key\": \"value\"}\n``` and after."
    expected_json = "{\"key\": \"value\"}"
    sanitized = openai_tool_instance._sanitize_json_response(raw_response)
    assert sanitized == expected_json

def test_sanitize_json_response_no_markers_looks_like_json(openai_tool_instance):
    """Test sanitization when no markers but content looks like JSON."""
    raw_response = " {\"key\": \"value\"} " # Leading/trailing whitespace
    expected_json = "{\"key\": \"value\"}"
    sanitized = openai_tool_instance._sanitize_json_response(raw_response)
    assert sanitized == expected_json

def test_sanitize_json_response_no_markers_not_json(openai_tool_instance):
    """Test sanitization when no markers and content is not JSON."""
    raw_response = "Just plain text."
    sanitized = openai_tool_instance._sanitize_json_response(raw_response)
    assert sanitized == ""

def test_sanitize_json_response_invalid_content(openai_tool_instance):
    """Test sanitization when content within markers is not valid JSON structure."""
    raw_response = "```json\nnot really json\n```"
    sanitized = openai_tool_instance._sanitize_json_response(raw_response)
    assert sanitized == "" # Fails the start/end check

def test_sanitize_json_response_empty_markers(openai_tool_instance):
    """Test sanitization with empty content within markers."""
    raw_response = "```json\n```"
    sanitized = openai_tool_instance._sanitize_json_response(raw_response)
    assert sanitized == "" # Fails the start/end check
