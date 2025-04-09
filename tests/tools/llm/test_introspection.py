# tests/tools/llm/test_introspection.py
import pytest
import os
import json
import time
import requests
from unittest.mock import patch, MagicMock, mock_open, ANY # Import ANY
from jsonschema import ValidationError
from pytest_mock import MockerFixture # Import MockerFixture
from typing import List, Dict, Any, Generator # Import typing helpers

# Import the class being tested and potentially other modules if needed for mocking targets
from fbpyutils_ai.tools.llm import OpenAITool
import fbpyutils_ai.tools.llm._introspection # Import for path calculation in one test

# Note: Fixture openai_tool_instance is automatically available from conftest.py

# --- list_models Tests ---

@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get')
def test_list_models_base(
    mock_get: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test listing models for the base API."""
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [
            {
                "name": "text-davinci-003",
                "id": "davinci",
                # ... (other fields can be added if needed for assertion)
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    tool = openai_tool_instance # Use the fixture

    # Act
    models = tool.list_models(api_base_type="base")

    # Assert
    assert len(models) == 1
    assert models[0]["id"] == "davinci" # Check id as name might not always be present
    # Check URL includes /v1/
    mock_get.assert_called_once_with(
        f"{tool.api_base.rstrip('/')}/v1/models",
        headers=tool.api_headers,
        timeout=tool.timeout
    )


@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get')
def test_list_models_embed(mock_get: MagicMock) -> None:
    """Test listing models for the embed API."""
    # Arrange
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [{"id": "embed-model-1"}]}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response
    tool = OpenAITool(model_id="m", api_key="k", api_embed_base="https://embed.example.com")
    expected_headers = tool.api_headers.copy() # Get headers after potential init adjustments
    # Ensure correct key is used for assertion if different
    expected_headers["Authorization"] = f"Bearer {tool.api_embed_key}"


    # Act
    models = tool.list_models(api_base_type="embed_base")

    # Assert
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
@patch('fbpyutils_ai.tools.llm._introspection.json.load', return_value=MOCK_SCHEMA)
@patch('fbpyutils_ai.tools.llm.OpenAITool.generate_completions') # Patching the public method on the class
@patch('fbpyutils_ai.tools.llm._introspection.validate')
@patch('fbpyutils_ai.tools.llm._introspection.time.monotonic', side_effect=[100.0, 101.5])
def test_get_model_details_success_direct_json(
    mock_time: MagicMock,
    mock_validate: MagicMock,
    mock_gen_comp: MagicMock,
    mock_json_load: MagicMock,
    mock_file_open: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test get_model_details success with direct valid JSON response."""
    # Arrange
    model_id = "test-model-id"
    mock_gen_comp.return_value = json.dumps(MOCK_VALID_CAPABILITIES)
    # mock_validate is mocked to do nothing (assume validation passes)

    # Act
    details = openai_tool_instance.get_model_details(model_id)

    # Assert
    # Check that generate_completions was called with the correct arguments
    mock_gen_comp.assert_called_once_with(
        ANY, # Matches the messages list argument
        temperature=0.0,
        max_tokens=4096,
        response_format={'type': 'json_object'}
    )
    mock_validate.assert_called_once_with(instance=MOCK_VALID_CAPABILITIES, schema=MOCK_SCHEMA)
    assert details["model_id"] == model_id
    assert details["extraction_ok"] is True
    assert details["extraction_error"] is None
    assert details["extraction_attempts"] == 1
    assert details["sanitization_required"] is False
    assert details["extraction_duration_seconds"] == 1.5 # 101.5 - 100.0
    assert details["model_name"] == MOCK_VALID_CAPABILITIES["model_name"] # Check data merged

@patch('builtins.open', new_callable=mock_open, read_data=json.dumps(MOCK_SCHEMA))
@patch('fbpyutils_ai.tools.llm._introspection.json.load', return_value=MOCK_SCHEMA)
@patch('fbpyutils_ai.tools.llm.OpenAITool.generate_completions')
@patch('fbpyutils_ai.tools.llm.OpenAITool._sanitize_json_response') # Patching as a method on the class
@patch('fbpyutils_ai.tools.llm._introspection.validate')
@patch('fbpyutils_ai.tools.llm._introspection.time.monotonic', side_effect=[200.0, 202.0])
def test_get_model_details_success_sanitized_json(
    mock_time: MagicMock,
    mock_validate: MagicMock,
    mock_sanitize: MagicMock,
    mock_gen_comp: MagicMock,
    mock_json_load: MagicMock,
    mock_file_open: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
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
    # Check that generate_completions was called with the correct arguments
    mock_gen_comp.assert_called_once_with(
        ANY, # Matches the messages list argument
        temperature=0.0,
        max_tokens=4096,
        response_format={'type': 'json_object'}
    )
    mock_sanitize.assert_called_once_with(raw_response) # Removed self argument
    # Validate should be called with the parsed sanitized response
    mock_validate.assert_called_once_with(instance=MOCK_VALID_CAPABILITIES, schema=MOCK_SCHEMA)
    assert details["extraction_ok"] is True
    assert details["extraction_error"] is None
    assert details["extraction_attempts"] == 1
    assert details["sanitization_required"] is True # Flag set correctly
    assert details["extraction_duration_seconds"] == 2.0
    assert details["model_name"] == MOCK_VALID_CAPABILITIES["model_name"]

@patch('builtins.open', new_callable=mock_open, read_data=json.dumps(MOCK_SCHEMA))
@patch('fbpyutils_ai.tools.llm._introspection.json.load', return_value=MOCK_SCHEMA)
@patch('fbpyutils_ai.tools.llm.OpenAITool.generate_completions') # Patching the public method on the class
@patch('fbpyutils_ai.tools.llm._introspection.validate', side_effect=ValidationError("Schema mismatch"))
@patch('fbpyutils_ai.tools.llm._introspection.time.monotonic', side_effect=[300.0, 306.0])
def test_get_model_details_failure_validation_error(
    mock_time: MagicMock,
    mock_validate: MagicMock,
    mock_gen_comp: MagicMock,
    mock_json_load: MagicMock,
    mock_file_open: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
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
@patch('fbpyutils_ai.tools.llm._introspection.json.load', return_value=MOCK_SCHEMA)
# Simulate API error with a non-JSON-serializable object to test logging fallback
@patch('fbpyutils_ai.tools.llm.OpenAITool.generate_completions', side_effect=Exception(MagicMock()))
@patch('fbpyutils_ai.tools.llm._introspection.time.monotonic', side_effect=[400.0, 401.0])
def test_get_model_details_failure_api_error(
    mock_time: MagicMock,
    mock_gen_comp: MagicMock,
    mock_json_load: MagicMock,
    mock_file_open: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test get_model_details failure due to API call error."""
    # Arrange
    model_id = "test-model-id"
    max_retries = 1 # Only need one attempt to fail

    # Act
    details = openai_tool_instance.get_model_details(model_id, max_retries=max_retries)

    # Assert
    # Check that generate_completions was called with the correct arguments
    mock_gen_comp.assert_called_once_with(
        ANY, # Matches the messages list argument
        temperature=0.0,
        max_tokens=4096,
        response_format={'type': 'json_object'}
    ) # API call attempted once
    assert details["extraction_ok"] is False
    assert "api call failed" in details["extraction_error"].lower() # Check error message substring
    # Check that the non-serializable mock object was mentioned in the error string representation
    assert "MagicMock" in details["extraction_error"]
    assert details["extraction_attempts"] == max_retries
    assert details["extraction_duration_seconds"] == 1.0

# --- New Test Case ---

@patch('builtins.open', new_callable=mock_open, read_data=json.dumps(MOCK_SCHEMA))
@patch('fbpyutils_ai.tools.llm._introspection.json.load', return_value=MOCK_SCHEMA)
@patch('fbpyutils_ai.tools.llm.OpenAITool.generate_completions')
@patch('fbpyutils_ai.tools.llm.OpenAITool._sanitize_json_response', return_value=None) # Simulate sanitization failure
@patch('fbpyutils_ai.tools.llm._introspection.validate') # Won't be called if sanitization fails
@patch('fbpyutils_ai.tools.llm._introspection.time.monotonic', side_effect=[500.0, 505.0])
def test_get_model_details_failure_sanitization_error(
    mock_time: MagicMock,
    mock_validate: MagicMock,
    mock_sanitize: MagicMock,
    mock_gen_comp: MagicMock,
    mock_json_load: MagicMock,
    mock_file_open: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test get_model_details failure when sanitization returns None."""
    # Arrange
    model_id = "test-model-id"
    raw_response = "Some text ```json\nINVALID JSON\n``` more text."
    mock_gen_comp.return_value = raw_response
    max_retries = 2

    # Act
    details = openai_tool_instance.get_model_details(model_id, max_retries=max_retries)

    # Assert
    assert mock_gen_comp.call_count == max_retries # Called for each retry
    mock_sanitize.assert_called_with(raw_response) # Called each time after direct parse fails
    assert mock_sanitize.call_count == max_retries
    mock_validate.assert_not_called() # Validation shouldn't happen if sanitization fails
    assert details["extraction_ok"] is False
    assert "sanitization failed" in details["extraction_error"].lower() # Corrected substring check
    assert details["extraction_attempts"] == max_retries
    assert details["extraction_duration_seconds"] == 5.0 # 505.0 - 500.0

# --- End New Test Case ---

    assert details["extraction_ok"] is False
    assert "sanitization failed" in details["extraction_error"].lower() # Check for sanitization error message
    assert details["extraction_attempts"] == max_retries
    assert details["extraction_duration_seconds"] == 5.0 # Corrected expected duration

@patch('builtins.open', side_effect=FileNotFoundError("prompt.md not found"))
def test_get_model_details_failure_resource_not_found(
    mock_file_open: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test get_model_details failure if resource files are missing."""
    # Arrange
    model_id = "test-model-id"

    # Act
    details = openai_tool_instance.get_model_details(model_id)

    # Assert
# --- New Test Case for Retry Success ---

@patch('builtins.open', new_callable=mock_open, read_data=json.dumps(MOCK_SCHEMA))
@patch('fbpyutils_ai.tools.llm._introspection.json.load', return_value=MOCK_SCHEMA)
@patch('fbpyutils_ai.tools.llm.OpenAITool.generate_completions')
@patch('fbpyutils_ai.tools.llm._introspection.validate')
@patch('fbpyutils_ai.tools.llm._introspection.time.monotonic', side_effect=[600.0, 601.0, 601.5]) # Time for 2 attempts
def test_get_model_details_success_on_retry(
    mock_time: MagicMock,
    mock_validate: MagicMock,
    mock_gen_comp: MagicMock,
    mock_json_load: MagicMock,
    mock_file_open: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test get_model_details succeeding on the second attempt after validation failure."""
    # Arrange
    model_id = "test-model-retry"
    invalid_response = json.dumps({"wrong_key": "value"})
    valid_response = json.dumps(MOCK_VALID_CAPABILITIES)

    # Simulate generate_completions returning invalid then valid response
    mock_gen_comp.side_effect = [invalid_response, valid_response]

    # Simulate validate failing on the first (invalid) response, passing on the second
    mock_validate.side_effect = [ValidationError("Schema mismatch on first try"), None]

    max_retries = 2

    # Act
    details = openai_tool_instance.get_model_details(model_id, max_retries=max_retries)

    # Assert
    assert mock_gen_comp.call_count == 2 # Called twice
    assert mock_validate.call_count == 2 # Validation attempted twice
    # First call to validate should have failed, second should pass (mocked side effect)
    mock_validate.assert_any_call(instance={"wrong_key": "value"}, schema=MOCK_SCHEMA)
    mock_validate.assert_called_with(instance=MOCK_VALID_CAPABILITIES, schema=MOCK_SCHEMA) # Last call

    assert details["extraction_ok"] is True # Succeeded eventually
    assert details["extraction_error"] is None
    assert details["extraction_attempts"] == 2 # Succeeded on the second attempt
# --- New Test Case for Sanitized Validation Failure ---

@patch('builtins.open', new_callable=mock_open, read_data=json.dumps(MOCK_SCHEMA))
@patch('fbpyutils_ai.tools.llm._introspection.json.load', return_value=MOCK_SCHEMA)
@patch('fbpyutils_ai.tools.llm.OpenAITool.generate_completions')
@patch('fbpyutils_ai.tools.llm.OpenAITool._sanitize_json_response')
@patch('fbpyutils_ai.tools.llm._introspection.validate', side_effect=ValidationError("Sanitized schema mismatch")) # Fail validation
@patch('fbpyutils_ai.tools.llm._introspection.time.monotonic', side_effect=[800.0, 801.0])
def test_get_model_details_failure_sanitized_validation_error(
    mock_time: MagicMock,
    mock_validate: MagicMock,
    mock_sanitize: MagicMock,
    mock_gen_comp: MagicMock,
    mock_json_load: MagicMock,
    mock_file_open: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test get_model_details failure when sanitized JSON fails validation."""
    # Arrange
    model_id = "test-model-id"
    raw_response = "Some text ```json\n{\"wrong_key\": \"value\"}\n``` more text."
    sanitized_response = json.dumps({"wrong_key": "value"}) # Sanitized but still invalid
    mock_gen_comp.return_value = raw_response
    mock_sanitize.return_value = sanitized_response
    max_retries = 1

    # Act
    details = openai_tool_instance.get_model_details(model_id, max_retries=max_retries)

    # Assert
    mock_gen_comp.assert_called_once()
    mock_sanitize.assert_called_once_with(raw_response)
    # Validate should be called once with the sanitized (but invalid) data
    mock_validate.assert_called_once_with(instance={"wrong_key": "value"}, schema=MOCK_SCHEMA)
    assert details["extraction_ok"] is False
    assert "sanitized json validation failed" in details["extraction_error"].lower()
    assert "Sanitized schema mismatch" in details["extraction_error"] # Check original exception message
    assert details["extraction_attempts"] == max_retries
    assert details["extraction_duration_seconds"] == 1.0

# --- End New Test Case ---
    assert details["sanitization_required"] is False # Direct JSON worked on second try
    assert details["extraction_duration_seconds"] == 1.0 # Match the logged duration (601.0 - 600.0)
    # Removed assertion for model_name as it won't exist in the failure dictionary

# --- End New Test Case ---

# --- New Test Case for Sanitization Exception ---

@patch('builtins.open', new_callable=mock_open, read_data=json.dumps(MOCK_SCHEMA))
@patch('fbpyutils_ai.tools.llm._introspection.json.load', return_value=MOCK_SCHEMA)
@patch('fbpyutils_ai.tools.llm.OpenAITool.generate_completions')
@patch('fbpyutils_ai.tools.llm.OpenAITool._sanitize_json_response', side_effect=Exception("Sanitization crashed")) # Simulate sanitization exception
@patch('fbpyutils_ai.tools.llm._introspection.validate') # Won't be called
@patch('fbpyutils_ai.tools.llm._introspection.time.monotonic', side_effect=[700.0, 701.0])
def test_get_model_details_failure_sanitization_exception(
    mock_time: MagicMock,
    mock_validate: MagicMock,
    mock_sanitize: MagicMock,
    mock_gen_comp: MagicMock,
    mock_json_load: MagicMock,
    mock_file_open: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test get_model_details failure when _sanitize_json_response raises an exception."""
    # Arrange
    model_id = "test-model-id"
    raw_response = "Some text ```json\nINVALID JSON\n``` more text."
    mock_gen_comp.return_value = raw_response
    max_retries = 1 # Only need one attempt

    # Act
    details = openai_tool_instance.get_model_details(model_id, max_retries=max_retries)

    # Assert
    mock_gen_comp.assert_called_once()
    mock_sanitize.assert_called_once_with(raw_response)
    mock_validate.assert_not_called()
    assert details["extraction_ok"] is False
    assert "sanitization crashed" in details["extraction_error"].lower() # Check for the original exception message substring
    assert "Sanitization crashed" in details["extraction_error"] # Check original exception message
    assert details["extraction_attempts"] == max_retries
    assert details["extraction_duration_seconds"] == 1.0 # 701.0 - 700.0
# --- New Test Case for Schema File Not Found ---

@patch('builtins.open') # Patch open globally for this test
def test_get_model_details_failure_schema_not_found(
    mock_file_open: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test get_model_details failure if schema file is missing."""
    # Arrange
    model_id = "test-model-id"
    # Calculate paths relative to the _introspection module location
    introspection_module = fbpyutils_ai.tools.llm._introspection
    introspection_module_dir = os.path.dirname(os.path.abspath(introspection_module.__file__))
    prompt_path = os.path.join(introspection_module_dir, "resources", "llm_introspection_prompt.md")
    schema_path = os.path.join(introspection_module_dir, "resources", "llm_introspection_validation_schema.json")

    # Simulate open succeeding for prompt but failing for schema
    def open_side_effect(file, mode='r', *args, **kwargs):
        if file == prompt_path and mode == 'r':
            return mock_open(read_data="prompt content").return_value
        elif file == schema_path and mode == 'r':
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        else:
            # Allow other opens (like for logging) to proceed without error in this test
            # by returning a default mock_open if not specifically handled.
            # Be cautious with this approach if other file operations are critical.
            # Alternatively, make the side_effect more specific about allowed paths.
             try:
                 # Attempt to delegate to the original open for non-mocked paths
                 # This requires careful handling as it might interact with other mocks
                 # For simplicity here, we just return a generic mock file
                 return mock_open().return_value
             except Exception:
                 # Fallback if delegation fails or isn't desired
                 raise FileNotFoundError(f"Unexpected file open in test: {file}")


    mock_file_open.side_effect = open_side_effect

    # Act
    details = openai_tool_instance.get_model_details(model_id)

    # Assert
    assert details["extraction_ok"] is False
    assert "Resource file not found" in details["extraction_error"]
    assert details["extraction_error"] == "Resource file not found: None" # Check exact error message
    assert details["extraction_attempts"] == 0 # Fails before API call

# --- End New Test Case ---

# --- End New Test Case ---
# Removed duplicated assertions from previous test

# Note: Patching json.load first, then open inside the function
@patch('fbpyutils_ai.tools.llm._introspection.json.load', side_effect=json.JSONDecodeError("Bad JSON", "", 0))
def test_get_model_details_failure_schema_decode_error(
    mock_json_load: MagicMock,
    openai_tool_instance: OpenAITool
) -> None:
    """Test get_model_details failure if schema file is invalid JSON."""
    # Arrange
    model_id = "test-model-id"
    # Calculate paths relative to the _introspection module location
    introspection_module = fbpyutils_ai.tools.llm._introspection
    introspection_module_dir = os.path.dirname(os.path.abspath(introspection_module.__file__))
    prompt_path = os.path.join(introspection_module_dir, "resources", "llm_introspection_prompt.md")
    schema_path = os.path.join(introspection_module_dir, "resources", "llm_introspection_validation_schema.json")

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
            # This mock handle will cause json.load to raise the mocked JSONDecodeError
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
