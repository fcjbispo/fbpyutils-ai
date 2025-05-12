import pytest
from unittest.mock import patch, MagicMock, AsyncMock, PropertyMock # Import PropertyMock
import requests
import httpx
import json
import logging # Import logging
import tenacity # Import tenacity
from tenacity import RetryError, stop_after_attempt, wait_fixed
from tenacity.wait import wait_base # Import wait_base for type checking
from tenacity.stop import stop_base # Import stop_base for type checking

from fbpyutils_ai.tools.llm import OpenAITool, LLMServiceModel
from fbpyutils_ai.tools.http import RequestsManager, HTTPClient
from fbpyutils_ai.tools.llm.utils import get_llm_resources, sanitize_model_details # Import get_llm_resources and sanitize_model_details

# Get necessary constants by calling get_llm_resources
_, _, LLM_INTROSPECTION_PROMPT, LLM_INTROSPECTION_VALIDATION_SCHEMA = get_llm_resources()


# Mock LLMServiceModel for testing
@pytest.fixture
def mock_llm_service_model():
    return LLMServiceModel(
        provider="test_provider",
        model_id="test_model",
        api_base="https://test.com/api",
        api_base_url="https://test.com/api", # Added missing field
        api_key="test_key",
        embed_model_id="test_embed_model",
        embed_api_base="https://test.com/embed",
        embed_api_key="test_embed_key",
        vision_model_id="test_vision_model",
        vision_api_base="https://test.com/vision",
        vision_api_key="test_vision_key",
    )

# Mock RequestsManager.make_request for testing OpenAITool methods that use it
@pytest.fixture
def mock_requests_manager_make_request():
    with patch('fbpyutils_ai.tools.http.RequestsManager.make_request') as mock_make_request:
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"success": True})
        mock_make_request.return_value = mock_response
        yield mock_make_request

# Mock HTTPClient.async_request for testing OpenAITool methods that use it asynchronously
@pytest.fixture
def mock_http_client_async_request():
    with patch('fbpyutils_ai.tools.http.HTTPClient.async_request') as mock_async_request:
        mock_response = AsyncMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"async_success": True})
        mock_async_request.return_value = mock_response
        yield mock_async_request

# Test generate_completions uses _make_request with correct parameters
def test_generate_completions_uses_make_request(mock_llm_service_model):
    """Test that generate_completions calls _make_request with correct parameters."""
    tool = OpenAITool(base_model=mock_llm_service_model)

    # Mock the _make_request method and relevant properties on the specific tool instance
    with patch.object(tool, '_make_request') as mock_make_request, \
         patch.object(OpenAITool, 'api_base', new_callable=PropertyMock) as mock_api_base, \
         patch.object(OpenAITool, 'api_headers', new_callable=PropertyMock) as mock_api_headers, \
         patch.object(OpenAITool, 'model_id', new_callable=PropertyMock) as mock_model_id:

        mock_api_base.return_value = "https://mock.api/base"
        mock_api_headers.return_value = {"Mock-Header": "true"}
        mock_model_id.return_value = "mock-model"

        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"choices": [{"message": {"content": "response text"}}]})
        mock_make_request.return_value = mock_response

        messages = [{"role": "user", "content": "Hello"}]
        expected_url = f"{mock_api_base.return_value}/chat/completions"
        expected_headers = mock_api_headers.return_value
        expected_model_id = mock_model_id.return_value
        expected_data = {"model": expected_model_id, "messages": messages}

        tool.generate_completions(messages)

        mock_make_request.assert_called_once_with(
            expected_url,
            headers=expected_headers,
            json_data=expected_data,
            timeout=tool.timeout,
            stream=False,
            # Default retry parameters passed by generate_completions to _make_request
            wait=tenacity.wait_random_exponential(multiplier=1, max=40),
            stop=tenacity.stop_after_attempt(3)
        )


# Test generate_embeddings uses _make_request with correct parameters
def test_generate_embeddings_uses_make_request(mock_llm_service_model):
    """Test that generate_embeddings calls _make_request with correct parameters."""
    tool = OpenAITool(base_model=mock_llm_service_model, embed_model=mock_llm_service_model)

    with patch.object(tool, '_make_request') as mock_make_request, \
         patch.object(OpenAITool, 'api_embed_base', new_callable=PropertyMock) as mock_api_embed_base, \
         patch.object(OpenAITool, 'api_headers', new_callable=PropertyMock) as mock_api_headers, \
         patch.object(OpenAITool, 'embed_model_id', new_callable=PropertyMock) as mock_embed_model_id:

        mock_api_embed_base.return_value = "https://mock.api/embed"
        mock_api_headers.return_value = {"Mock-Embed-Header": "true"}
        mock_embed_model_id.return_value = "mock-embed-model"

        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"data": [{"embedding": [0.1, 0.2]}]})
        mock_make_request.return_value = mock_response

        input_text = ["embed this"]
        expected_url = f"{mock_api_embed_base.return_value}/embeddings"
        expected_headers = mock_api_headers.return_value
        expected_model_id = mock_embed_model_id.return_value
        expected_data = {"model": expected_model_id, "input": input_text}

        tool.generate_embeddings(input_text)

        mock_make_request.assert_called_once_with(
            expected_url,
            headers=expected_headers,
            json_data=expected_data,
            timeout=tool.timeout,
            stream=False,
            # Default retry parameters passed by generate_embeddings to _make_request
            wait=tenacity.wait_random_exponential(multiplier=1, max=40),
            stop=tenacity.stop_after_attempt(3)
        )


# Test generate_text uses _make_request with correct parameters
def test_generate_text_uses_make_request(mock_llm_service_model):
    """Test that generate_text calls _make_request with correct parameters."""
    tool = OpenAITool(base_model=mock_llm_service_model)

    with patch.object(tool, '_make_request') as mock_make_request, \
         patch.object(OpenAITool, 'api_base', new_callable=PropertyMock) as mock_api_base, \
         patch.object(OpenAITool, 'api_headers', new_callable=PropertyMock) as mock_api_headers, \
         patch.object(OpenAITool, 'model_id', new_callable=PropertyMock) as mock_model_id:

        mock_api_base.return_value = "https://mock.api/base"
        mock_api_headers.return_value = {"Mock-Header": "true"}
        mock_model_id.return_value = "mock-model"

        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"choices": [{"text": "generated text"}]})
        mock_make_request.return_value = mock_response

        prompt = "generate text"
        expected_url = f"{mock_api_base.return_value}/completions"
        expected_headers = mock_api_headers.return_value
        expected_model_id = mock_model_id.return_value
        expected_data = {"model": expected_model_id, "prompt": prompt}

        tool.generate_text(prompt)

        mock_make_request.assert_called_once_with(
            expected_url,
            headers=expected_headers,
            json_data=expected_data,
            timeout=tool.timeout,
            stream=False,
            # Default retry parameters passed by generate_text to _make_request
            wait=tenacity.wait_random_exponential(multiplier=1, max=40),
            stop=tenacity.stop_after_attempt(3)
        )


# Test describe_image uses generate_text with correct parameters
def test_describe_image_uses_generate_text(mock_llm_service_model):
    """Test that describe_image calls generate_text with correct parameters."""
    tool = OpenAITool(base_model=mock_llm_service_model, vision_model=mock_llm_service_model)

    # Mock the generate_text method on the specific tool instance
    with patch.object(tool, 'generate_text') as mock_generate_text:
        mock_generate_text.return_value = "image description"

        image_data = "base64_image_data"
        prompt = "describe this"
        # Construct the expected full prompt including base64 data
        expected_full_prompt = (
            f"{prompt}\n\n"
            "Below is the image encoded in base64:\n"
            f"{image_data}\n\n"
            "Provide a detailed description of the image."
        )

        tool.describe_image(image_data, prompt)

        mock_generate_text.assert_called_once_with(
            expected_full_prompt,
            vision=True,
            # Any additional kwargs passed to describe_image should be passed to generate_text
        )


# Test get_model_details uses get_api_model_response with correct parameters
def test_get_model_details_uses_get_api_model_response(mock_llm_service_model):
    """Test that get_model_details uses get_api_model_response with correct parameters."""
    tool = OpenAITool(base_model=mock_llm_service_model)

    # Mock get_api_model_response as it's the direct dependency
    with patch('fbpyutils_ai.tools.llm.utils.get_api_model_response') as mock_get_api_model_response, \
         patch.object(OpenAITool, 'model_map', new_callable=PropertyMock) as mock_model_map:

        # Configure the mocked model_map to return a mock LLMServiceModel with necessary attributes
        mock_model = MagicMock(spec=LLMServiceModel)
        mock_model.provider = "mock_provider"
        mock_model.model_id = "mock_model_id"
        mock_model.api_base_url = "https://mock.api/base"
        mock_model.api_key = "mock_api_key"
        mock_model_map.return_value = {"base": mock_model}

        mock_get_api_model_response.return_value = {"details": "mocked"}

        tool.get_model_details()

        expected_url = f"{mock_model.api_base_url}/models/{mock_model.model_id}"
        expected_api_key = mock_model.api_key

        mock_get_api_model_response.assert_called_once_with(
            expected_url,
            expected_api_key,
            timeout=tool.timeout, # Verify timeout is passed
            retries=tool.retries # Verify retries is passed
        )

# Test get_model_details introspection path uses generate_completions with correct parameters
def test_get_model_details_introspection_uses_generate_completions(mock_llm_service_model):
    """Test that get_model_details introspection path calls generate_completions."""
    tool = OpenAITool(base_model=mock_llm_service_model)

    # Mock get_api_model_response and generate_completions
    with patch('fbpyutils_ai.tools.llm.utils.get_api_model_response') as mock_get_api_model_response, \
         patch.object(tool, 'generate_completions') as mock_generate_completions, \
         patch.object(OpenAITool, 'model_map', new_callable=PropertyMock) as mock_model_map:

        # Configure the mocked model_map to return a mock LLMServiceModel with necessary attributes
        mock_model = MagicMock(spec=LLMServiceModel)
        mock_model.provider = "mock_provider"
        mock_model.model_id = "mock_model_id"
        mock_model.api_base_url = "https://mock.api/base"
        mock_model.api_key = "mock_api_key"
        mock_model_map.return_value = {"base": mock_model}

        mock_get_api_model_response.return_value = {"details": "mocked"}

        # Simulate a valid JSON response from generate_completions
        mock_response_content = json.dumps({
            "model_name": "test_model",
            "description": "A test model",
            "capabilities": ["text_generation"],
            "pricing": {"input": 0.001, "output": 0.002},
            "max_tokens": 1000,
            "training_data": "unknown",
            "architecture": "transformer",
            "knowledge_cut_off": "2023-01-01",
            "provider": "test_provider",
            "api_base": "https://test.com/api"
        })
        mock_generate_completions.return_value = {
            "choices": [{"message": {"content": f"```json\n{mock_response_content}\n```"}}]
        }

        tool.get_model_details(introspection=True)

        mock_get_api_model_response.assert_called_once()
        mock_generate_completions.assert_called_once()
        # Verify the arguments passed to generate_completions, including retry parameters
        call_args, call_kwargs = mock_generate_completions.call_args
        assert 'wait' in call_kwargs
        assert 'stop' in call_kwargs
        assert isinstance(call_kwargs['wait'], tenacity.wait_base)
        assert isinstance(call_kwargs['stop'], tenacity.stop_base)
        # Verify other expected arguments
        assert call_kwargs['messages'] == [{"role": "system", "content": LLM_INTROSPECTION_PROMPT}, {"role": "user", "content": "Please list me ALL the details about this model."}]
        assert call_kwargs['model'] == mock_model.model_id
        assert call_kwargs['timeout'] == tool.timeout # Use tool's timeout
        assert call_kwargs['stream'] is False


# Test get_model_details introspection path handles JSONDecodeError (should not retry locally)
def test_get_model_details_introspection_json_error(mock_llm_service_model, caplog):
    """Test that get_model_details introspection handles JSONDecodeError without local retry."""
    tool = OpenAITool(base_model=mock_llm_service_model)

    with patch('fbpyutils_ai.tools.llm.utils.get_api_model_response') as mock_get_api_model_response, \
         patch.object(tool, 'generate_completions') as mock_generate_completions, \
         patch.object(OpenAITool, 'model_map', new_callable=PropertyMock) as mock_model_map:

        # Configure the mocked model_map to return a mock LLMServiceModel with necessary attributes
        mock_model = MagicMock(spec=LLMServiceModel)
        mock_model.provider = "mock_provider"
        mock_model.model_id = "mock_model_id"
        mock_model.api_base_url = "https://mock.api/base"
        mock_model.api_key = "mock_api_key"
        mock_model_map.return_value = {"base": mock_model}

        mock_get_api_model_response.return_value = {"details": "mocked"}

        # Simulate a JSONDecodeError from generate_completions
        mock_generate_completions.side_effect = json.JSONDecodeError("Invalid JSON", doc="invalid", pos=0)

        caplog.set_level(logging.ERROR)

        with pytest.raises(json.JSONDecodeError): # Expect the exception to be re-raised
             tool.get_model_details(introspection=True)

        mock_get_api_model_response.assert_called_once()
        mock_generate_completions.assert_called_once() # Should only be called once, retry is handled by HTTPClient
        assert "Error decoding JSON" in caplog.text # Verify logging


# Test get_model_details introspection path handles ValidationError (should not retry locally)
def test_get_model_details_introspection_validation_error(mock_llm_service_model, caplog):
    """Test that get_model_details introspection handles ValidationError without local retry."""
    tool = OpenAITool(base_model=mock_llm_service_model)

    with patch('fbpyutils_ai.tools.llm.utils.get_api_model_response') as mock_get_api_model_response, \
         patch.object(tool, 'generate_completions') as mock_generate_completions, \
         patch.object(OpenAITool, 'model_map', new_callable=PropertyMock) as mock_model_map, \
         patch('fbpyutils_ai.tools.llm.utils.sanitize_model_details') as mock_sanitize: # Mock sanitize_model_details

        # Configure the mocked model_map to return a mock LLMServiceModel with necessary attributes
        mock_model = MagicMock(spec=LLMServiceModel)
        mock_model.provider = "mock_provider"
        mock_model.model_id = "mock_model_id"
        mock_model.api_base_url = "https://mock.api/base"
        mock_model.api_key = "mock_api_key"
        mock_model_map.return_value = {"base": mock_model}

        mock_get_api_model_response.return_value = {"details": "mocked"}

        # Simulate a response that fails validation
        mock_response_content = json.dumps({
            "model_name": "test_model",
            # Missing required fields to cause validation error
        })
        mock_generate_completions.return_value = {
            "choices": [{"message": {"content": f"```json\n{mock_response_content}\n```"}}]
        }

        mock_sanitize.return_value = ({}, {}) # Return empty dicts for sanitized details and changes

        caplog.set_level(logging.INFO)

        tool.get_model_details(introspection=True) # Should not raise, sanitization handles it

        mock_get_api_model_response.assert_called_once()
        mock_generate_completions.assert_called_once() # Should only be called once
        mock_sanitize.assert_called_once() # Sanitize should be called after validation error
        assert "JSON Validation error" in caplog.text # Verify logging


# Test that _make_request passes retry parameters to RequestsManager.make_request
def test__make_request_passes_retry_params(mock_llm_service_model):
    """Test that _make_request passes wait and stop parameters to RequestsManager.make_request."""
    tool = OpenAITool(base_model=mock_llm_service_model)

    # Mock RequestsManager.make_request globally for this test
    with patch('fbpyutils_ai.tools.http.RequestsManager.make_request') as mock_requests_manager_make_request:
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"success": True})
        mock_requests_manager_make_request.return_value = mock_response

        test_wait = tenacity.wait_fixed(5)
        test_stop = tenacity.stop_after_attempt(5)

        tool._make_request(
            url="https://test.com/api",
            headers={},
            json_data={},
            timeout=10,
            method="POST",
            wait=test_wait,
            stop=test_stop
        )

        mock_requests_manager_make_request.assert_called_once()
        call_args, call_kwargs = mock_requests_manager_make_request.call_args
        assert 'wait' in call_kwargs
        assert 'stop' in call_kwargs
        # Compare types and parameters, not object identity
        assert isinstance(call_kwargs['wait'], wait_base) # Use imported type
        assert call_kwargs['wait'].__dict__ == test_wait.__dict__
        assert isinstance(call_kwargs['stop'], stop_base) # Use imported type
        assert call_kwargs['stop'].__dict__ == test_stop.__dict__
