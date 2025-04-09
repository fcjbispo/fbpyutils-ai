# tests/tools/llm/test_vision.py
import pytest
import base64
import requests
from unittest.mock import patch, MagicMock, mock_open, ANY # Import ANY
from pytest_mock import MockerFixture # Import MockerFixture
from fbpyutils_ai.tools.llm import OpenAITool # Import for type hinting

# Note: Fixture openai_tool_instance is automatically available from conftest.py

# --- describe_image Tests ---

@patch('fbpyutils_ai.tools.llm._vision.os.path.exists')
@patch('fbpyutils_ai.tools.llm._vision.open', new_callable=mock_open, read_data=b'imagedata')
@patch('fbpyutils_ai.tools.llm.OpenAITool.generate_text') # Corrected patch target
def test_describe_image_local_file_success(
    mock_generate_text: MagicMock,
    mock_file_open: MagicMock,
    mock_exists: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
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
    mock_exists.assert_any_call(image_path) # Use assert_any_call to ignore other checks
    mock_file_open.assert_called_once_with(image_path, "rb")
    expected_full_prompt = (
        f"{prompt}\n\n"
        "Below is the image encoded in base64:\n"
        f"{expected_base64}\n\n"
        "Provide a detailed description of the image."
    )
    mock_generate_text.assert_called_once_with(
        # openai_tool_instance, # Removed self argument
        expected_full_prompt,
        max_tokens=150,
        temperature=0.5,
        vision=True
    )
    assert description == "Description of the local image."

@patch('fbpyutils_ai.tools.llm._vision.requests.Session.get')
@patch('fbpyutils_ai.tools.llm._vision.os.path.exists')
@patch('fbpyutils_ai.tools.llm.OpenAITool.generate_text') # Corrected patch target
def test_describe_image_remote_url_success(
    mock_generate_text: MagicMock,
    mock_exists: MagicMock,
    mock_requests_get: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
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
    mock_exists.assert_any_call(image_url) # Use assert_any_call
    # Assert that the session's get method was called (mock_requests_get is patching Session.get)
    mock_requests_get.assert_called_once_with(image_url, timeout=openai_tool_instance.timeout)
    mock_response.raise_for_status.assert_called_once()
    expected_full_prompt = (
        f"{prompt}\n\n"
        "Below is the image encoded in base64:\n"
        f"{expected_base64}\n\n"
        "Provide a detailed description of the image."
    )
    mock_generate_text.assert_called_once_with(
        # openai_tool_instance, # Removed self argument
        expected_full_prompt,
        max_tokens=300,
        temperature=0.4,
        vision=True # Defaults
    )
    assert description == "Description of the remote image."


@patch('fbpyutils_ai.tools.llm._vision.os.path.exists')
@patch('fbpyutils_ai.tools.llm.OpenAITool.generate_text') # Corrected patch target
def test_describe_image_base64_input_success(
    mock_generate_text: MagicMock,
    mock_exists: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test successful image description from base64 input."""
    # Arrange
    mock_exists.return_value = False # Not a local path
    mock_generate_text.return_value = "Description from base64."
    base64_image = base64.b64encode(b'base64data').decode('utf-8')
    prompt = "Analyze this."

    # Act
    description = openai_tool_instance.describe_image(base64_image, prompt)

    # Assert
    mock_exists.assert_any_call(base64_image) # Use assert_any_call
    expected_full_prompt = (
        f"{prompt}\n\n"
        "Below is the image encoded in base64:\n"
        f"{base64_image}\n\n"
        "Provide a detailed description of the image."
    )
    mock_generate_text.assert_called_once_with(
        # openai_tool_instance, # Removed self argument
        expected_full_prompt,
        max_tokens=300,
        temperature=0.4,
        vision=True # Defaults
    )
    assert description == "Description from base64."

@patch('fbpyutils_ai.tools.llm._vision.os.path.exists') # Target new location
@patch('fbpyutils_ai.tools.llm._vision.open', side_effect=IOError("File not found"))
def test_describe_image_local_file_read_error(
    mock_file_open: MagicMock,
    mock_exists: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
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
def test_describe_image_remote_url_download_error(
    mock_exists: MagicMock,
    mock_requests_get: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
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

@patch('fbpyutils_ai.tools.llm.OpenAITool.generate_text', return_value="") # Corrected patch target again
@patch('fbpyutils_ai.tools.llm._vision.os.path.exists', return_value=False)
def test_describe_image_generation_fails(
    mock_exists: MagicMock,
    mock_generate_text: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test describe_image returns empty string if generate_text fails."""
    # Arrange
    # Use valid base64, even if short, to pass initial decoding/validation
    base64_image = base64.b64encode(b'data').decode('utf-8') # Use valid base64
    prompt = "Analyze this."

    # Act
    description = openai_tool_instance.describe_image(base64_image, prompt)

    # Assert
    assert description == ""
    # Ensure generate_text was called with the instance and expected args
    mock_generate_text.assert_called_once_with(ANY, max_tokens=ANY, temperature=ANY, vision=True) # Removed self argument
