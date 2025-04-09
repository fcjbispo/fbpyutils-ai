# tests/tools/llm/introspection/test_get_model_details.py
import pytest
import json
from unittest.mock import patch, MagicMock, mock_open, ANY # Import ANY
from jsonschema import ValidationError
from fbpyutils_ai.tools.llm import OpenAITool
from tests.tools.llm.introspection.common import MOCK_VALID_CAPABILITIES, MOCK_SCHEMA

@patch('builtins.open', new_callable=mock_open, read_data=json.dumps(MOCK_SCHEMA))
@patch('fbpyutils_ai.tools.llm._introspection.json.load', return_value=MOCK_SCHEMA)
@patch('fbpyutils_ai.tools.llm.OpenAITool.generate_completions')
@patch('fbpyutils_ai.tools.llm._introspection.validate')
@patch('fbpyutils_ai.tools.llm._introspection.time.monotonic', side_effect=[100.0, 101.5])
def test_get_model_details_success_direct_json(
    mock_time: MagicMock, mock_validate: MagicMock, mock_gen_comp: MagicMock, mock_json_load: MagicMock, mock_file_open: MagicMock,
    openai_tool_instance
):
    """Test get_model_details success with direct valid JSON response."""
    model_id = "test-model-id"
    mock_gen_comp.return_value = json.dumps(MOCK_VALID_CAPABILITIES)
    
    details = openai_tool_instance.get_model_details(model_id)
    
    mock_gen_comp.assert_called_once_with(
        ANY,
        temperature=0.0,
        max_tokens=4096,
        response_format={'type': 'json_object'}
    )
    mock_validate.assert_called_once_with(
        instance=MOCK_VALID_CAPABILITIES, 
        schema=MOCK_SCHEMA
    )
    assert details["model_id"] == model_id
    assert details["extraction_ok"] is True
    assert details["extraction_duration_seconds"] == 1.5

@patch('builtins.open', new_callable=mock_open, read_data=json.dumps(MOCK_SCHEMA))
@patch('fbpyutils_ai.tools.llm._introspection.json.load', return_value=MOCK_SCHEMA)
@patch('fbpyutils_ai.tools.llm.OpenAITool.generate_completions')
@patch('fbpyutils_ai.tools.llm.OpenAITool._sanitize_json_response')
@patch('fbpyutils_ai.tools.llm._introspection.validate')
@patch('fbpyutils_ai.tools.llm._introspection.time.monotonic', side_effect=[200.0, 202.0])
def test_get_model_details_success_sanitized_json(
    mock_time: MagicMock, mock_validate: MagicMock, mock_sanitize: MagicMock, mock_gen_comp: MagicMock,
    mock_json_load, mock_file_open, openai_tool_instance
):
    """Test get_model_details success after sanitization."""
    model_id = "test-model-id"
    raw_response = f"Some text ```json\n{json.dumps(MOCK_VALID_CAPABILITIES)}\n``` more text."
    mock_gen_comp.return_value = raw_response
    mock_sanitize.return_value = json.dumps(MOCK_VALID_CAPABILITIES)
    
    details = openai_tool_instance.get_model_details(model_id)
    
    mock_sanitize.assert_called_once_with(raw_response)
    mock_validate.assert_called_once_with(
        instance=MOCK_VALID_CAPABILITIES, 
        schema=MOCK_SCHEMA
    )
    assert details["extraction_ok"] is True
    assert details["sanitization_required"] is True

# Additional test cases would follow the same pattern...
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
    assert details["extraction_ok"] is False
    assert "Resource file not found" in details["extraction_error"]
    assert details["extraction_attempts"] == 0 # Fails before API call

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
    assert details["sanitization_required"] is False # Direct JSON worked on second try
    assert details["extraction_duration_seconds"] == 1.0 # Match logged duration (601.0 - 600.0)

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

# --- End New Test Case ---

# --- New Test Case for Schema File Not Found ---
import os
import fbpyutils_ai.tools.llm._introspection # Import for path calculation

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
             try:
                 # Attempt to delegate to the original open for non-mocked paths
                 return mock_open().return_value
             except Exception:
                 raise FileNotFoundError(f"Unexpected file open in test: {file}")


    mock_file_open.side_effect = open_side_effect

    # Act
    details = openai_tool_instance.get_model_details(model_id)

    # Assert
    assert details["extraction_ok"] is False
    assert "Resource file not found" in details["extraction_error"]
    # Check exact error message returned by the function's exception handler
    assert details["extraction_error"] == "Resource file not found: None"
    assert details["extraction_attempts"] == 0 # Fails before API call

# --- End New Test Case ---

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
        if file == prompt_path and mode == 'r':
            return mock_open(read_data="prompt content").return_value
        elif file == schema_path and mode == 'r':
            # This mock handle will cause json.load to raise the mocked JSONDecodeError
            return mock_open(read_data="invalid json").return_value
        else:
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
# - get_model_details_failure_schema_not_found
# - get_model_details_failure_schema_decode_error

# Note: For brevity, I'm showing the pattern with 2 tests. The full file would include all get_model_details tests
# from the original file following this same structure.
