import pytest
import os
import json
import base64
import time
from unittest.mock import patch, MagicMock, mock_open, call
import requests
from jsonschema import ValidationError # Import for testing get_model_details

# Assuming fbpyutils_ai.logging is configured elsewhere or mock it if needed
# from unittest.mock import patch
# patch('fbpyutils_ai.logging', MagicMock()).start()

from fbpyutils_ai.tools.llm import OpenAITool
from fbpyutils_ai.tools.http import RequestsManager # Needed for mocking _make_request target

# --- Fixtures ---

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
    return OpenAITool(model="test-model", api_key="test_key")

# --- __init__ Tests ---

def test_init_with_api_key_arg():
    """Test initialization with API key provided as argument."""
    tool = OpenAITool(model="test-model", api_key="arg_test_key")
    assert tool.api_key == "arg_test_key"
    assert tool.api_base == "https://api.openai.com" # Default

def test_init_with_api_key_env(mock_env_api_key):
    """Test initialization with API key from environment variable."""
    tool = OpenAITool(model="test-model")
    assert tool.api_key == "env_test_key"

def test_init_no_api_key_raises_error(monkeypatch):
    """Test initialization raises ValueError if no API key is found."""
    # Ensure the environment variable is unset for this specific test
    monkeypatch.delenv("FBPY_OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="API key is required"):
        OpenAITool(model="test-model") # No key arg, env explicitly unset
def test_init_with_api_base_arg():
    """Test initialization with API base provided as argument."""
    tool = OpenAITool(model="test-model", api_key="test_key", api_base="https://arg-api.example.com")
    assert tool.api_base == "https://arg-api.example.com"

def test_init_with_api_base_env(mock_env_api_base):
    """Test initialization with API base from environment variable."""
    tool = OpenAITool(model="test-model", api_key="test_key")
    assert tool.api_base == "https://env-api.example.com"

def test_init_anthropic_headers():
    """Test Anthropic specific headers are added when api_base matches."""
    tool = OpenAITool(model="claude-3", api_key="test_key", api_base="https://api.anthropic.com/v1")
    assert "x-api-key" in tool.api_headers
    assert "anthropic-version" in tool.api_headers
    assert tool.api_headers["x-api-key"] == "test_key"

def test_init_defaults():
    """Test default values for various parameters."""
    tool = OpenAITool(model="test-model", api_key="test_key")
    assert tool.model == "test-model"
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
        model="main-model",
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
    assert tool.model == "main-model"
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

# --- _make_request Tests (Tested indirectly via other methods) ---
# We mock _make_request in other tests, assuming RequestsManager.make_request works

# --- generate_embedding Tests ---

@patch.object(OpenAITool, '_make_request')
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
        f"{openai_tool_instance.api_embed_base}/embeddings",
        openai_tool_instance.api_headers,
        {"model": openai_tool_instance.embed_model, "input": text_to_embed}
    )
    assert embedding == [0.1, 0.2, 0.3]

@patch.object(OpenAITool, '_make_request')
def test_generate_embedding_api_error(mock_make_request, openai_tool_instance):
    """Test embedding generation failure due to API error."""
    # Arrange
    mock_make_request.side_effect = requests.exceptions.RequestException("API Error")
    text_to_embed = "This is a test text."

    # Act
    embedding = openai_tool_instance.generate_embedding(text_to_embed)

    # Assert
    assert embedding is None

@patch.object(OpenAITool, '_make_request')
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

# --- generate_text Tests ---

@patch.object(OpenAITool, '_make_request')
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
        "model": openai_tool_instance.model,
        "prompt": prompt,
        "max_tokens": 100,
        "temperature": 0.7,
    }
    mock_make_request.assert_called_once_with(
        f"{openai_tool_instance.api_base}/completions",
        openai_tool_instance.api_headers,
        expected_data
    )
    assert generated_text == "Generated text response."

@patch.object(OpenAITool, '_make_request')
def test_generate_text_vision_success(mock_make_request):
    """Test successful text generation in vision mode."""
    # Arrange
    tool = OpenAITool(
        model="main-model",
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
        f"{tool.api_vision_base}/completions",
        expected_headers,
        expected_data
    )
    assert generated_text == "Vision generated text."

@patch.object(OpenAITool, '_make_request')
def test_generate_text_api_error(mock_make_request, openai_tool_instance):
    """Test text generation failure due to API error."""
    # Arrange
    mock_make_request.side_effect = requests.exceptions.RequestException("API Error")
    prompt = "Generate some text."

    # Act
    generated_text = openai_tool_instance.generate_text(prompt)

    # Assert
    assert generated_text == ""

@patch.object(OpenAITool, '_make_request')
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

@patch.object(OpenAITool, '_make_request')
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
        "model": openai_tool_instance.model,
        "messages": messages,
        "temperature": 0.5,
    }
    mock_make_request.assert_called_once_with(
        f"{openai_tool_instance.api_base}/chat/completions",
        openai_tool_instance.api_headers,
        expected_data
    )
    assert response == "Chat response."

@patch.object(OpenAITool, '_make_request')
def test_generate_completions_api_error(mock_make_request, openai_tool_instance):
    """Test chat completion failure due to API error."""
    # Arrange
    mock_make_request.side_effect = requests.exceptions.RequestException("API Error")
    messages = [{"role": "user", "content": "Hello"}]

    # Act
    response = openai_tool_instance.generate_completions(messages)

    # Assert
    assert response == ""

@patch.object(OpenAITool, '_make_request')
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

@patch.object(OpenAITool, '_make_request')
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

# --- generate_tokens Tests ---

@patch('fbpyutils_ai.tools.llm.tiktoken.encoding_for_model')
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
    mock_encoding_for_model.assert_called_once_with(openai_tool_instance.model)
    mock_encoder.encode.assert_called_once_with(text)
    assert tokens == [101, 2000, 102]

@patch('fbpyutils_ai.tools.llm.tiktoken.encoding_for_model')
@patch('fbpyutils_ai.tools.llm.tiktoken.get_encoding')
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
    mock_encoding_for_model.assert_called_once_with(openai_tool_instance.model)
    mock_get_encoding.assert_called_once_with("cl100k_base")
    mock_default_encoder.encode.assert_called_once_with(text)
    assert tokens == [500, 600]

# --- describe_image Tests ---

@patch('fbpyutils_ai.tools.llm.os.path.exists')
@patch('builtins.open', new_callable=mock_open, read_data=b'imagedata')
@patch.object(OpenAITool, 'generate_text')
def test_describe_image_local_file_success(mock_generate_text, mock_file_open, mock_exists, openai_tool_instance):
    """Test successful image description from a local file."""
    # Arrange
    mock_exists.return_value = True
    mock_generate_text.return_value = "Description of the local image."
    image_path = "/path/to/local/image.jpg"
    prompt = "Describe this picture."
    expected_base64 = base64.b64encode(b'imagedata').decode('utf-8')

    # Act
    description = openai_tool_instance.describe_image(image_path, prompt, max_tokens=150, temperature=0.5)

    # Assert
    mock_exists.assert_called_once_with(image_path)
    mock_file_open.assert_called_once_with(image_path, "rb")
    expected_full_prompt = (
        f"{prompt}\n\n"
        "Below is the image encoded in base64:\n"
        f"{expected_base64}\n\n"
        "Provide a detailed description of the image."
    )
    mock_generate_text.assert_called_once_with(
        expected_full_prompt, max_tokens=150, temperature=0.5, vision=True
    )
    assert description == "Description of the local image."

@patch('fbpyutils_ai.tools.llm.requests.get')
@patch('fbpyutils_ai.tools.llm.os.path.exists')
@patch.object(OpenAITool, 'generate_text')
def test_describe_image_remote_url_success(mock_generate_text, mock_exists, mock_requests_get, openai_tool_instance):
    """Test successful image description from a remote URL."""
    # Arrange
    mock_exists.return_value = False # It's not a local path
    mock_response = MagicMock()
    mock_response.content = b'remoteimagedata'
    mock_response.raise_for_status = MagicMock()
    mock_requests_get.return_value = mock_response
    mock_generate_text.return_value = "Description of the remote image."
    image_url = "https://example.com/image.png"
    prompt = "What is this?"
    expected_base64 = base64.b64encode(b'remoteimagedata').decode('utf-8')

    # Act
    description = openai_tool_instance.describe_image(image_url, prompt)

    # Assert
    mock_exists.assert_called_once_with(image_url)
    mock_requests_get.assert_called_once_with(image_url, timeout=openai_tool_instance.timeout)
    mock_response.raise_for_status.assert_called_once()
    expected_full_prompt = (
        f"{prompt}\n\n"
        "Below is the image encoded in base64:\n"
        f"{expected_base64}\n\n"
        "Provide a detailed description of the image."
    )
    mock_generate_text.assert_called_once_with(
        expected_full_prompt, max_tokens=300, temperature=0.4, vision=True # Defaults
    )
    assert description == "Description of the remote image."


@patch('fbpyutils_ai.tools.llm.os.path.exists')
@patch.object(OpenAITool, 'generate_text')
def test_describe_image_base64_input_success(mock_generate_text, mock_exists, openai_tool_instance):
    """Test successful image description from base64 input."""
    # Arrange
    mock_exists.return_value = False # Not a local path
    mock_generate_text.return_value = "Description from base64."
    base64_image = base64.b64encode(b'base64data').decode('utf-8')
    prompt = "Analyze this."

    # Act
    description = openai_tool_instance.describe_image(base64_image, prompt)

    # Assert
    mock_exists.assert_called_once_with(base64_image)
    expected_full_prompt = (
        f"{prompt}\n\n"
        "Below is the image encoded in base64:\n"
        f"{base64_image}\n\n"
        "Provide a detailed description of the image."
    )
    mock_generate_text.assert_called_once_with(
        expected_full_prompt, max_tokens=300, temperature=0.4, vision=True # Defaults
    )
    assert description == "Description from base64."

@patch('fbpyutils_ai.tools.llm.os.path.exists')
@patch('builtins.open', side_effect=IOError("File not found"))
def test_describe_image_local_file_read_error(mock_file_open, mock_exists, openai_tool_instance):
    """Test describe_image returns empty string on local file read error."""
    # Arrange
    mock_exists.return_value = True
    image_path = "/path/to/nonexistent/image.jpg"
    prompt = "Describe this."

    # Act
    description = openai_tool_instance.describe_image(image_path, prompt)

    # Assert
    assert description == ""

@patch('fbpyutils_ai.tools.llm.requests.get')
@patch('fbpyutils_ai.tools.llm.os.path.exists')
def test_describe_image_remote_url_download_error(mock_exists, mock_requests_get, openai_tool_instance):
    """Test describe_image returns empty string on URL download error."""
    # Arrange
    mock_exists.return_value = False
    mock_requests_get.side_effect = requests.exceptions.RequestException("Download failed")
    image_url = "https://example.com/invalid_image.png"
    prompt = "What is this?"

    # Act
    description = openai_tool_instance.describe_image(image_url, prompt)

    # Assert
    assert description == ""

@patch.object(OpenAITool, 'generate_text', return_value="")
@patch('fbpyutils_ai.tools.llm.os.path.exists', return_value=False) # Assume base64
def test_describe_image_generation_fails(mock_exists, mock_generate_text, openai_tool_instance):
    """Test describe_image returns empty string if generate_text fails."""
    # Arrange
    base64_image = "dummybase64"
    prompt = "Analyze this."

    # Act
    description = openai_tool_instance.describe_image(base64_image, prompt)

    # Assert
    assert description == ""
    mock_generate_text.assert_called_once() # Ensure it was called

# --- list_models Tests (Existing tests are kept) ---

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
def test_list_models_embed(mock_get):
    """Test listing models for embed_base."""
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [{"id": "embed-model-1"}]}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    tool = OpenAITool(model="m", api_key="k", api_embed_base="https://embed.example.com")

    # Act
    models = tool.list_models(api_base_type="embed_base")

    # Assert
    mock_get.assert_called_once_with(
        "https://embed.example.com/models",
        headers=tool.api_headers,
        timeout=tool.timeout
    )
    assert len(models) == 1
    assert models[0]["id"] == "embed-model-1"


@patch('fbpyutils_ai.tools.llm.requests.Session.get')
def test_list_models_vision(mock_get):
    """Test listing models for vision_base."""
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [{"id": "vision-model-1"}]}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    tool = OpenAITool(model="m", api_key="k", api_vision_base="https://vision.example.com")

    # Act
    models = tool.list_models(api_base_type="vision_base")

    # Assert
    mock_get.assert_called_once_with(
        "https://vision.example.com/models",
        headers=tool.api_headers,
        timeout=tool.timeout
    )
    assert len(models) == 1
    assert models[0]["id"] == "vision-model-1"


@patch('fbpyutils_ai.tools.llm.requests.Session.get')
def test_list_models_invalid_api_base_type(mock_get):
    # Arrange
    tool = OpenAITool(model="text-davinci-003", api_key="test_key")

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid api_base_type"):
        tool.list_models(api_base_type="invalid_base")

@patch('fbpyutils_ai.tools.llm.requests.Session.get')
def test_list_models_api_error(mock_get):
    # Arrange
    mock_get.side_effect = requests.exceptions.RequestException("API Error")
    tool = OpenAITool(model="text-davinci-003", api_key="test_key")

    # Act & Assert
    with pytest.raises(requests.exceptions.RequestException):
        tool.list_models(api_base_type="base")

# --- _sanitize_json_response Tests ---

def test_sanitize_json_response_success(openai_tool_instance):
    """Test successful extraction of JSON from markers."""
    raw_response = "Some text before ```json\n{\"key\": \"value\"}\n``` and after."
    expected_json = "{\"key\": \"value\"}"
    sanitized = openai_tool_instance._sanitize_json_response(raw_response)
    assert sanitized == expected_json

def test_sanitize_json_response_no_markers(openai_tool_instance):
    """Test sanitization when no JSON markers are present."""
    raw_response = "Just plain text {\"key\": \"value\"}."
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

# --- get_model_details Tests ---

# Mock data for successful validation
MOCK_VALID_CAPABILITIES = {
    "model_name": "test-model-id",
    "provider": "TestProvider",
    "architecture": "Transformer",
    "capabilities": ["text generation", "summarization"],
    "context_window_tokens": 8192,
    "output_formats": ["text", "json"],
    "training_data_cutoff": "2023-04-01",
    "strengths": ["Good at coding", "Creative writing"],
    "limitations": ["Cannot access real-time internet", "May hallucinate"],
    "multilingual_support": ["en", "es", "fr"],
    "fine_tuning_options": True,
    "api_access_details": {"endpoint": "/v1/completions", "authentication": "API Key"},
    "cost_per_token": {"input": 0.001, "output": 0.002},
    "response_time_avg_ms": 500,
    "ethical_considerations": ["Bias mitigation efforts in place"],
    "version_information": "v1.2.3",
    "documentation_link": "https://example.com/docs",
    "is_vision_capable": False,
    "is_embedding_model": False
}
MOCK_SCHEMA = {"type": "object", "properties": {"model_name": {"type": "string"}}, "required": ["model_name"]} # Simplified schema

@patch('builtins.open', new_callable=mock_open, read_data=json.dumps(MOCK_SCHEMA))
@patch('fbpyutils_ai.tools.llm.json.load', return_value=MOCK_SCHEMA) # Mock loading from file handle
@patch.object(OpenAITool, 'generate_completions')
@patch('fbpyutils_ai.tools.llm.validate') # Mock jsonschema validate
@patch('fbpyutils_ai.tools.llm.time.monotonic', side_effect=[100.0, 101.5]) # Mock time
def test_get_model_details_success_direct_json(mock_time, mock_validate, mock_gen_comp, mock_json_load, mock_file_open, openai_tool_instance):
    """Test get_model_details success with direct valid JSON response."""
    # Arrange
    model_id = "test-model-id"
    mock_gen_comp.return_value = json.dumps(MOCK_VALID_CAPABILITIES)
    # mock_validate is mocked to do nothing (assume validation passes)

    # Act
    details = openai_tool_instance.get_model_details(model_id)

    # Assert
    mock_gen_comp.assert_called_once()
    mock_validate.assert_called_once_with(instance=MOCK_VALID_CAPABILITIES, schema=MOCK_SCHEMA)
    assert details["model_id"] == model_id
    assert details["extraction_ok"] is True
    assert details["extraction_error"] is None
    assert details["extraction_attempts"] == 1
    assert details["sanitization_required"] is False
    assert details["extraction_duration_seconds"] == 1.5 # 101.5 - 100.0
    assert details["model_name"] == MOCK_VALID_CAPABILITIES["model_name"] # Check data merged

@patch('builtins.open', new_callable=mock_open, read_data=json.dumps(MOCK_SCHEMA))
@patch('fbpyutils_ai.tools.llm.json.load', return_value=MOCK_SCHEMA)
@patch.object(OpenAITool, 'generate_completions')
@patch.object(OpenAITool, '_sanitize_json_response')
@patch('fbpyutils_ai.tools.llm.validate')
@patch('fbpyutils_ai.tools.llm.time.monotonic', side_effect=[200.0, 202.0])
def test_get_model_details_success_sanitized_json(mock_time, mock_validate, mock_sanitize, mock_gen_comp, mock_json_load, mock_file_open, openai_tool_instance):
    """Test get_model_details success after sanitization."""
    # Arrange
    model_id = "test-model-id"
    raw_response = f"Some text ```json\n{json.dumps(MOCK_VALID_CAPABILITIES)}\n``` more text."
    sanitized_response = json.dumps(MOCK_VALID_CAPABILITIES)
    mock_gen_comp.return_value = raw_response
    mock_sanitize.return_value = sanitized_response # Simulate successful sanitization
    # mock_validate is mocked to do nothing

    # Act
    details = openai_tool_instance.get_model_details(model_id)

    # Assert
    mock_gen_comp.assert_called_once()
    mock_sanitize.assert_called_once_with(raw_response)
    # Validate should be called with the parsed sanitized response
    mock_validate.assert_called_once_with(instance=MOCK_VALID_CAPABILITIES, schema=MOCK_SCHEMA)
    assert details["extraction_ok"] is True
    assert details["extraction_error"] is None
    assert details["extraction_attempts"] == 1
    assert details["sanitization_required"] is True # Flag set correctly
    assert details["extraction_duration_seconds"] == 2.0
    assert details["model_name"] == MOCK_VALID_CAPABILITIES["model_name"]

@patch('builtins.open', new_callable=mock_open, read_data=json.dumps(MOCK_SCHEMA))
@patch('fbpyutils_ai.tools.llm.json.load', return_value=MOCK_SCHEMA)
@patch.object(OpenAITool, 'generate_completions')
@patch('fbpyutils_ai.tools.llm.validate', side_effect=ValidationError("Schema mismatch")) # Mock validation failure
@patch('fbpyutils_ai.tools.llm.time.monotonic', side_effect=[300.0, 306.0]) # Start time, End time after loop
def test_get_model_details_failure_validation_error(mock_time, mock_validate, mock_gen_comp, mock_json_load, mock_file_open, openai_tool_instance):
    """Test get_model_details failure due to validation error after retries."""
    # Arrange
    model_id = "test-model-id"
    # Simulate response that parses but fails validation on all attempts
    mock_gen_comp.return_value = json.dumps({"wrong_key": "value"})
    max_retries = 3

    # Act
    details = openai_tool_instance.get_model_details(model_id, max_retries=max_retries)

    # Assert
    assert mock_gen_comp.call_count == max_retries
    assert mock_validate.call_count == max_retries # Validation attempted each time
    assert details["extraction_ok"] is False
    assert "validation failed" in details["extraction_error"].lower() # Check error message
    assert details["extraction_attempts"] == max_retries
    assert details["extraction_duration_seconds"] == 6.0 # 306.0 - 300.0

@patch('builtins.open', new_callable=mock_open, read_data=json.dumps(MOCK_SCHEMA))
@patch('fbpyutils_ai.tools.llm.json.load', return_value=MOCK_SCHEMA)
@patch.object(OpenAITool, 'generate_completions', side_effect=Exception("API Call Failed"))
@patch('fbpyutils_ai.tools.llm.time.monotonic', side_effect=[400.0, 401.0]) # Only one attempt needed
def test_get_model_details_failure_api_error(mock_time, mock_gen_comp, mock_json_load, mock_file_open, openai_tool_instance):
    """Test get_model_details failure due to API call error."""
    # Arrange
    model_id = "test-model-id"
    max_retries = 1 # Only need one attempt to fail

    # Act
    details = openai_tool_instance.get_model_details(model_id, max_retries=max_retries)

    # Assert
    mock_gen_comp.assert_called_once() # API call attempted once
    assert details["extraction_ok"] is False
    assert "API Call Failed" in details["extraction_error"]
    assert details["extraction_attempts"] == max_retries
    assert details["extraction_duration_seconds"] == 1.0

@patch('builtins.open', side_effect=FileNotFoundError("prompt.md not found"))
def test_get_model_details_failure_resource_not_found(mock_file_open, openai_tool_instance):
    """Test get_model_details failure if resource files are missing."""
    # Arrange
    model_id = "test-model-id"

    # Act
    details = openai_tool_instance.get_model_details(model_id)

    # Assert
    assert details["extraction_ok"] is False
    assert "Resource file not found" in details["extraction_error"]
    assert details["extraction_attempts"] == 0 # Fails before API call

# Note: Patching json.load first, then open inside the function
@patch('fbpyutils_ai.tools.llm.json.load', side_effect=json.JSONDecodeError("Bad JSON", "", 0)) # Mock load failure
def test_get_model_details_failure_schema_decode_error(mock_json_load, openai_tool_instance):
    """Test get_model_details failure if schema file is invalid JSON."""
    # Arrange
    model_id = "test-model-id"
    # Calculate paths relative to the llm module location dynamically
    # Find the directory containing llm.py
    llm_module_path = os.path.abspath(openai_tool_instance.__class__.__module__.replace('.', os.path.sep) + '.py')
    llm_module_dir = os.path.dirname(llm_module_path)
    prompt_path = os.path.join(llm_module_dir, "resources", "llm_introspection_prompt.md")
    schema_path = os.path.join(llm_module_dir, "resources", "llm_introspection_validation_schema.json")

    # Define a side effect function for mock_open used *inside* the 'with' block
    def open_side_effect(file, mode='r', *args, **kwargs):
        # print(f"Mock open called with: {file}, mode: {mode}") # Debug print
        if file == prompt_path and mode == 'r':
            # Return a mock file handle for the prompt
            # print(f"Returning mock for prompt: {prompt_path}")
            return mock_open(read_data="prompt content").return_value
        elif file == schema_path and mode == 'r':
            # Return a mock file handle for the schema with invalid JSON content
            # print(f"Returning mock for schema: {schema_path}")
            return mock_open(read_data="invalid json").return_value
        else:
            # For any other file path, raise an error to catch unexpected opens
            # print(f"Raising FileNotFoundError for: {file}")
            raise FileNotFoundError(f"Unexpected file open in test: {file}")

    # Patch 'builtins.open' within the test function's scope using 'with'
    with patch('builtins.open', side_effect=open_side_effect) as mock_file_open:
        # Act
        details = openai_tool_instance.get_model_details(model_id)

        # Assert
        assert details["extraction_ok"] is False
        # Verify json.load was called (it should fail due to the side_effect)
        mock_json_load.assert_called_once()
        # Check the specific error message generated by the except block in get_model_details
        assert "Invalid JSON in schema file" in details["extraction_error"]
        assert details["extraction_attempts"] == 0 # Fails before API call
