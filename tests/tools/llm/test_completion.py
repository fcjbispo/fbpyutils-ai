# tests/tools/llm/test_completion.py
import pytest
import requests
from unittest.mock import patch
from fbpyutils_ai.tools.llm import OpenAITool # Needed for test_generate_text_vision_success

# Note: Fixture openai_tool_instance is automatically available from conftest.py

# --- generate_text Tests ---

@patch('fbpyutils_ai.tools.llm._base._make_request')
def test_generate_text_success(mock_make_request, openai_tool_instance):
    """Test successful text generation."""
    # Arrange
    mock_response = {"choices": [{"text": " Generated text response. "}]}
    mock_make_request.return_value = mock_response
    prompt = "Generate some text."

    # Act
    generated_text = openai_tool_instance.generate_text(prompt, max_tokens=100, temperature=0.7)

    # Assert
    expected_data = {
        "model": openai_tool_instance.model_id,
        "prompt": prompt,
        "max_tokens": 100,
        "temperature": 0.7,
    }
    mock_make_request.assert_called_once_with(
        f"{openai_tool_instance.api_base.rstrip('/')}/v1/completions", # Expect /v1/
        openai_tool_instance.api_headers,
        expected_data
    )
    assert generated_text == "Generated text response."

@patch('fbpyutils_ai.tools.llm._base._make_request')
def test_generate_text_vision_success(mock_make_request):
    """Test successful text generation in vision mode."""
    # Arrange
    tool = OpenAITool(
        model_id="main-model",
        api_key="main_key",
        vision_model="vision-model",
        api_vision_base="https://vision.example.com",
        api_vision_key="vision_key"
    )
    mock_response = {"choices": [{"text": " Vision generated text. "}]}
    mock_make_request.return_value = mock_response
    prompt = "Describe this image."

    # Act
    generated_text = tool.generate_text(prompt, vision=True)

    # Assert
    expected_data = {
        "model": tool.vision_model,
        "prompt": prompt,
        "max_tokens": 300, # Default
        "temperature": 0.8, # Default
    }
    expected_headers = tool.api_headers.copy()
    expected_headers["Authorization"] = f"Bearer {tool.api_vision_key}"
    mock_make_request.assert_called_once_with(
        f"{tool.api_vision_base.rstrip('/')}/v1/completions", # Expect /v1/
        expected_headers,
        expected_data
    )
    assert generated_text == "Vision generated text."

@patch('fbpyutils_ai.tools.llm._base._make_request')
def test_generate_text_api_error(mock_make_request, openai_tool_instance):
    """Test text generation failure due to API error."""
    # Arrange
    mock_make_request.side_effect = requests.exceptions.RequestException("API Error")
    prompt = "Generate some text."

    # Act
    generated_text = openai_tool_instance.generate_text(prompt)

    # Assert
    assert generated_text == ""

@patch('fbpyutils_ai.tools.llm._base._make_request')
def test_generate_text_parsing_error(mock_make_request, openai_tool_instance):
    """Test text generation failure due to response parsing error."""
    # Arrange
    mock_response = {"invalid": "structure"}
    mock_make_request.return_value = mock_response
    prompt = "Generate some text."

    # Act
    generated_text = openai_tool_instance.generate_text(prompt)

    # Assert
    assert generated_text == ""

# --- generate_completions Tests ---

@patch('fbpyutils_ai.tools.llm._base._make_request')
def test_generate_completions_success(mock_make_request, openai_tool_instance):
    """Test successful chat completion generation."""
    # Arrange
    mock_response = {"choices": [{"message": {"content": " Chat response. "}}]}
    mock_make_request.return_value = mock_response
    messages = [{"role": "user", "content": "Hello"}]

    # Act
    response = openai_tool_instance.generate_completions(messages, temperature=0.5)

    # Assert
    expected_data = {
        "model": openai_tool_instance.model_id,
        "messages": messages,
        "temperature": 0.5,
    }
    mock_make_request.assert_called_once_with(
        f"{openai_tool_instance.api_base.rstrip('/')}/v1/chat/completions", # Expect /v1/
        openai_tool_instance.api_headers,
        expected_data
    )
    assert response == "Chat response."

@patch('fbpyutils_ai.tools.llm._base._make_request')
def test_generate_completions_api_error(mock_make_request, openai_tool_instance):
    """Test chat completion failure due to API error."""
    # Arrange
    mock_make_request.side_effect = requests.exceptions.RequestException("API Error")
    messages = [{"role": "user", "content": "Hello"}]

    # Act
    response = openai_tool_instance.generate_completions(messages)

    # Assert
    assert response == ""

@patch('fbpyutils_ai.tools.llm._base._make_request')
def test_generate_completions_parsing_error(mock_make_request, openai_tool_instance):
    """Test chat completion failure due to response parsing error."""
    # Arrange
    mock_response = {"choices": [{"message": {"no_content": "here"}}]} # Malformed
    mock_make_request.return_value = mock_response
    messages = [{"role": "user", "content": "Hello"}]

    # Act
    response = openai_tool_instance.generate_completions(messages)

    # Assert
    assert response == ""

@patch('fbpyutils_ai.tools.llm._base._make_request')
def test_generate_completions_empty_choices(mock_make_request, openai_tool_instance):
    """Test chat completion failure due to empty choices array."""
    # Arrange
    mock_response = {"choices": []}
    mock_make_request.return_value = mock_response
    messages = [{"role": "user", "content": "Hello"}]

    # Act
    response = openai_tool_instance.generate_completions(messages)

    # Assert
    assert response == ""
