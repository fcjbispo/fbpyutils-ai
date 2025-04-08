# tests/tools/llm/test_introspection.py
import pytest
import os
import json
import time
import requests
from unittest.mock import patch, MagicMock, mock_open
from jsonschema import ValidationError

# Import the class being tested and potentially other modules if needed for mocking targets
from fbpyutils_ai.tools.llm import OpenAITool
import fbpyutils_ai.tools.llm._introspection # Import for path calculation in one test

# Note: Fixture openai_tool_instance is automatically available from conftest.py

# --- list_models Tests ---

@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get') # Target new location
def test_list_models_base(mock_get, openai_tool_instance): # Added instance fixture
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


@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get') # Target new location
def test_list_models_embed(mock_get):
    """Test listing models for embed_base."""
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


@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get') # Target new location
def test_list_models_vision(mock_get):
    """Test listing models for vision_base."""
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


@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get') # Target new location
def test_list_models_invalid_api_base_type(mock_get, openai_tool_instance): # Added instance
    # Arrange
    tool = openai_tool_instance

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid api_base_type"):
        tool.list_models(api_base_type="invalid_base")

@patch('fbpyutils_ai.tools.llm._introspection.requests.Session.get') # Target new location
def test_list_models_api_error(mock_get, openai_tool_instance): # Added instance
    # Arrange
    mock_get.side_effect = requests.exceptions.RequestException("API Error")
    tool = openai_tool_instance

    # Act & Assert
    with pytest.raises(requests.exceptions.RequestException):
        tool.list_models(api_base_type="base")


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
@patch('fbpyutils_ai.tools.llm._introspection.json.load', return_value=MOCK_SCHEMA) # Target new location
@patch('fbpyutils_ai.tools.llm._introspection._generate_completions_for_details') # Target the nested helper
@patch('fbpyutils_ai.tools.llm._introspection.validate') # Target new location
@patch('fbpyutils_ai.tools.llm._introspection.time.monotonic', side_effect=[100.0, 101.5]) # Target new location
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
@patch('fbpyutils_ai.tools.llm._introspection.json.load', return_value=MOCK_SCHEMA) # Target new location
@patch('fbpyutils_ai.tools.llm._introspection._generate_completions_for_details') # Target the nested helper
@patch('fbpyutils_ai.tools.llm._utils._sanitize_json_response') # Target new location
@patch('fbpyutils_ai.tools.llm._introspection.validate') # Target new location
@patch('fbpyutils_ai.tools.llm._introspection.time.monotonic', side_effect=[200.0, 202.0]) # Target new location
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
    mock_sanitize.assert_called_once_with(openai_tool_instance, raw_response) # Ensure self is passed
    # Validate should be called with the parsed sanitized response
    mock_validate.assert_called_once_with(instance=MOCK_VALID_CAPABILITIES, schema=MOCK_SCHEMA)
    assert details["extraction_ok"] is True
    assert details["extraction_error"] is None
    assert details["extraction_attempts"] == 1
    assert details["sanitization_required"] is True # Flag set correctly
    assert details["extraction_duration_seconds"] == 2.0
    assert details["model_name"] == MOCK_VALID_CAPABILITIES["model_name"]

@patch('builtins.open', new_callable=mock_open, read_data=json.dumps(MOCK_SCHEMA))
@patch('fbpyutils_ai.tools.llm._introspection.json.load', return_value=MOCK_SCHEMA) # Target new location
@patch('fbpyutils_ai.tools.llm._introspection._generate_completions_for_details') # Target the nested helper
@patch('fbpyutils_ai.tools.llm._introspection.validate', side_effect=ValidationError("Schema mismatch")) # Target new location
@patch('fbpyutils_ai.tools.llm._introspection.time.monotonic', side_effect=[300.0, 306.0]) # Target new location
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
@patch('fbpyutils_ai.tools.llm._introspection.json.load', return_value=MOCK_SCHEMA) # Target new location
@patch('fbpyutils_ai.tools.llm._introspection._generate_completions_for_details', side_effect=Exception("API Call Failed")) # Target the nested helper, keep original side effect
@patch('fbpyutils_ai.tools.llm._introspection.time.monotonic', side_effect=[400.0, 401.0]) # Target new location
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
@patch('fbpyutils_ai.tools.llm._introspection.json.load', side_effect=json.JSONDecodeError("Bad JSON", "", 0)) # Target new location
def test_get_model_details_failure_schema_decode_error(mock_json_load, openai_tool_instance):
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
