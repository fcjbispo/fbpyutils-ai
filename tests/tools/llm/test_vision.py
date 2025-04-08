# tests/tools/llm/test_vision.py
import pytest
import base64
import requests
from unittest.mock import patch, MagicMock, mock_open

# Note: Fixture openai_tool_instance is automatically available from conftest.py

# --- describe_image Tests ---

@patch('fbpyutils_ai.tools.llm._vision.os.path.exists') # Target new location
@patch('builtins.open', new_callable=mock_open, read_data=b'imagedata')
@patch('fbpyutils_ai.tools.llm._completion.generate_text') # Target new location
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

@patch('fbpyutils_ai.tools.llm._vision.requests.Session.get') # Target Session.get used in _vision
@patch('fbpyutils_ai.tools.llm._vision.os.path.exists') # Target new location
@patch('fbpyutils_ai.tools.llm._completion.generate_text') # Target new location
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
    # Assert that the session's get method was called
    openai_tool_instance.session.get.assert_called_once_with(image_url, timeout=openai_tool_instance.timeout)
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


@patch('fbpyutils_ai.tools.llm._vision.os.path.exists') # Target new location
@patch('fbpyutils_ai.tools.llm._completion.generate_text') # Target new location
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

@patch('fbpyutils_ai.tools.llm._vision.os.path.exists') # Target new location
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

@patch('fbpyutils_ai.tools.llm._vision.requests.Session.get') # Target Session.get used in _vision
@patch('fbpyutils_ai.tools.llm._vision.os.path.exists') # Target new location
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

@patch('fbpyutils_ai.tools.llm._completion.generate_text', return_value="") # Target new location
@patch('fbpyutils_ai.tools.llm._vision.os.path.exists', return_value=False) # Target new location
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
