import pytest
import json
from unittest.mock import patch, mock_open

from fbpyutils_ai.tools.llm.utils import get_llm_resources

# Mock content for the resource files
MOCK_PROMPT_CONTENT = "This is a mock prompt."
MOCK_SCHEMA_CONTENT = json.dumps({
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "version": {"type": "string"}
    },
    "required": ["name"]
})
MOCK_PROVIDERS_CONTENT = """
| Provider | Model ID | API Base URL | Env API Key | Selected |
|---|---|---|---|---|
| openai | gpt-4 | https://api.openai.com/v1 | OPENAI_API_KEY | True |
| anthropic | claude-3 | https://api.anthropic.com/v1 | ANTHROPIC_API_KEY | False |
| google | gemini-pro | https://generativelanguage.googleapis.com/v1 | GOOGLE_API_KEY | True |
"""

@patch('builtins.open', new_callable=mock_open)
@patch('json.load')
@patch('os.path.join')
def test_get_llm_resources_success(mock_os_path_join, mock_json_load, mock_builtin_open):
    """
    Test successful retrieval and parsing of LLM resources.
    """
    # Configure mock_os_path_join to return predictable paths using forward slashes
    mock_os_path_join.side_effect = lambda *args: "/".join(args)

    # Configure mock_builtin_open to return different content based on the path
    def mock_open_side_effect(file_path, *args, **kwargs):
        if "llm_introspection_prompt.md" in file_path:
            return mock_open(read_data=MOCK_PROMPT_CONTENT).return_value
        elif "llm_introspection_validation_schema.json" in file_path:
            return mock_open(read_data=MOCK_SCHEMA_CONTENT).return_value
        elif "llm_providers.md" in file_path:
            return mock_open(read_data=MOCK_PROVIDERS_CONTENT).return_value
        else:
            # Fallback for unexpected file access
            return mock_open().return_value

    mock_builtin_open.side_effect = mock_open_side_effect

    # Configure mock_json_load for the schema file
    mock_json_load.return_value = json.loads(MOCK_SCHEMA_CONTENT)

    llm_providers, llm_common_params, llm_introspection_prompt, llm_introspection_validation_schema = get_llm_resources()

    # Assert that open was called for each resource file
    mock_builtin_open.assert_any_call("fbpyutils_ai/tools/llm/resources/llm_introspection_prompt.md", "r", encoding="utf-8")
    mock_builtin_open.assert_any_call("fbpyutils_ai/tools/llm/resources/llm_introspection_validation_schema.json", "r", encoding="utf-8")
    mock_builtin_open.assert_any_call("fbpyutils_ai/tools/llm/resources/llm_providers.md", "r", encoding="utf-8")

    # Assert the returned values are correct
    expected_providers = {
        "openai": {"provider": "openai", "model_id": "gpt-4", "api_base_url": "https://api.openai.com/v1", "env_api_key": "OPENAI_API_KEY", "selected": "True"},
        "google": {"provider": "google", "model_id": "gemini-pro", "api_base_url": "https://generativelanguage.googleapis.com/v1", "env_api_key": "GOOGLE_API_KEY", "selected": "True"},
    }
    assert llm_providers == expected_providers

    expected_common_params = [
        "temperature",
        "max_tokens",
        "top_p",
        "stream",
        "stream_options",
        "tool_choice",
    ]
    assert llm_common_params == expected_common_params
    assert llm_introspection_prompt == MOCK_PROMPT_CONTENT
    assert llm_introspection_validation_schema == json.loads(MOCK_SCHEMA_CONTENT)

@patch('builtins.open', new_callable=mock_open)
@patch('json.load')
@patch('os.path.join')
def test_get_llm_resources_empty_providers(mock_os_path_join, mock_json_load, mock_builtin_open):
    """
    Test retrieval when the providers file is empty or has no selected providers.
    """
    # Configure mock_os_path_join to return predictable paths using forward slashes
    mock_os_path_join.side_effect = lambda *args: "/".join(args)

    # Configure mock_builtin_open to return different content based on the path

    MOCK_EMPTY_PROVIDERS_CONTENT = """
| Provider | Model ID | API Base URL | Env API Key | Selected |
|---|---|---|---|---|
"""

    def mock_open_side_effect(file_path, *args, **kwargs):
        if "llm_introspection_prompt.md" in file_path:
            return mock_open(read_data=MOCK_PROMPT_CONTENT).return_value
        elif "llm_introspection_validation_schema.json" in file_path:
            return mock_open(read_data=MOCK_SCHEMA_CONTENT).return_value
        elif "llm_providers.md" in file_path:
            return mock_open(read_data=MOCK_EMPTY_PROVIDERS_CONTENT).return_value
        else:
            return mock_open().return_value

    mock_builtin_open.side_effect = mock_open_side_effect
    mock_json_load.return_value = json.loads(MOCK_SCHEMA_CONTENT)

    llm_providers, llm_common_params, llm_introspection_prompt, llm_introspection_validation_schema = get_llm_resources()

    assert llm_providers == {} # Expect empty dictionary
    expected_common_params = [
        "temperature",
        "max_tokens",
        "top_p",
        "stream",
        "stream_options",
        "tool_choice",
    ]
    assert llm_common_params == expected_common_params
    assert llm_introspection_prompt == MOCK_PROMPT_CONTENT
    assert llm_introspection_validation_schema == json.loads(MOCK_SCHEMA_CONTENT)
