import json
import os

import pandas as pd
import requests

from typing import Any, Dict, List, Tuple
from fbpyutils_ai.tools import LLMServiceModel
from fbpyutils_ai.tools.http import RequestsManager, basic_header
from fbpyutils_ai import logging


def get_api_model_response(
    url: str, api_key: str, **kwargs: Any
) -> requests.Response:
    headers = basic_header()
    headers.update(
        {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
    )

    if "api.anthropic.com" in url.lower():
        headers["x-api-key"] = api_key
        headers["anthropic-version"] = "2023-06-01"

    kwargs["timeout"] = kwargs.get("timeout", 300)
    try:
        response = RequestsManager.make_request(
            session=RequestsManager.create_session(),
            url=url,
            headers=headers,
            json_data={},
            timeout=kwargs["timeout"],
            method="GET",
            stream=False,
        )
        return response
    except Exception as e:
        logging.error(f"Failed to retrieve models: {e}")
        raise


def get_llm_model(
    provider_id: str, model_id: str, llm_providers: list[dict]
) -> LLMServiceModel:
    llm_provider = [p for p in llm_providers if p["provider"] == provider_id]
    if llm_provider:
        llm_model = LLMServiceModel(
            provider=provider_id,
            api_base_url=os.environ.get(
                f"{provider_id.upper()}_API_BASE_URL", llm_provider[0]["api_base_url"]
            ),
            api_key=os.environ.get(llm_provider[0]["env_api_key"]),
            model_id=model_id,
        )
        return llm_model


def get_llm_resources():
    def _strip(x: str) -> str:
        while "  " in x:
            x = x.replace("  ", "")
        return x.strip()

    prompt_path = os.path.join(
        "fbpyutils_ai", "tools", "llm", "resources", "llm_introspection_prompt.md"
    )
    schema_path = os.path.join(
        "fbpyutils_ai",
        "tools",
        "llm",
        "resources",
        "llm_introspection_validation_schema.json",
    )
    endpoints_path = os.path.join(
        "fbpyutils_ai",
        "tools",
        "llm",
        "resources",
        "llm_providers.md",
    )

    with open(prompt_path, "r", encoding="utf-8") as f:
        llm_introspection_prompt = f.read()
    with open(schema_path, "r", encoding="utf-8") as f:
        llm_introspection_validation_schema = json.load(f)
    with open(endpoints_path, "r", encoding="utf-8") as f:
        llm_endpoints_raw = f.read()

    lines = llm_endpoints_raw.strip().split('\n')

    # Find header and separator lines
    header_line = None
    separator_line = None
    data_lines = []

    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line.startswith('|') and stripped_line.endswith('|'):
            if separator_line is None and all(c in ('-', '|', ':', ' ') for c in stripped_line):
                separator_line = stripped_line
            elif header_line is None:
                header_line = stripped_line
            elif separator_line is not None:
                data_lines.append(stripped_line)

    if not header_line or not separator_line:
        logging.error("Could not parse markdown table headers or separator.")
        return {}, [], "", {} # Return empty or default values if parsing fails

    # Extract and clean headers
    headers = [h.strip().lower().replace(" ", "_") for h in header_line.strip('|').split('|')]

    # Extract and clean data rows
    data_rows = []
    for data_line in data_lines:
        # Split by |, strip whitespace, and remove empty strings from leading/trailing pipes
        row_data = [d.strip() for d in data_line.strip('|').split('|')]
        if len(row_data) == len(headers):
             data_rows.append(row_data)
        else:
             logging.warning(f"Skipping malformed row in llm_providers.md: {data_line}")

    # Create list of dictionaries
    providers_list = [dict(zip(headers, row)) for row in data_rows]

    # Filter for selected providers and create the dictionary
    llm_providers = {
        p["provider"]: p for p in providers_list if p.get("selected", "").lower() == "true"
    }

    llm_common_params = [
        "temperature",
        "max_tokens",
        "top_p",
        "stream",
        "stream_options",
        "tool_choice",
    ]

    return (
        llm_providers,
        llm_common_params,
        llm_introspection_prompt,
        llm_introspection_validation_schema,
    )


def sanitize_model_details(
    model_details: Dict[str, Any],
    schema: Dict[str, Any],
    parent_key: str = "",  # Used for tracking nested changes
) -> Tuple[Dict[str, Any], Dict[str, List[str]]]:
    """
    Normalizes the model_details dictionary according to the provided JSON schema.

    Adds mandatory keys with None if missing, removes extra keys not in the schema,
    and processes nested objects recursively.

    Args:
        model_details: The dictionary to sanitize.
        schema: The JSON schema to normalize against.
        parent_key: Internal use for tracking nested key paths.

    Returns:
        A tuple containing:
            - The sanitized dictionary.
            - A dictionary detailing changes: {'added': [...], 'removed': [...]}.
                Keys are represented with dot notation for nested objects (e.g., 'parent.child.key').
    """
    sanitized_details = {}
    changes = {"added": [], "removed": []}
    schema_properties = schema.get("properties", {})
    required_properties = schema.get("required", [])
    original_keys = set(model_details.keys())
    schema_keys = set(schema_properties.keys())

    current_prefix = f"{parent_key}." if parent_key else ""

    # Add required properties with None if missing
    for prop_name in required_properties:
        if prop_name not in model_details and prop_name in schema_properties:
            sanitized_details[prop_name] = None
            changes["added"].append(f"{current_prefix}{prop_name}")

    # Process existing properties
    for prop_name, prop_value in model_details.items():
        if prop_name in schema_properties:
            prop_schema = schema_properties[prop_name]
            prop_type = prop_schema.get("type")

            if (
                prop_type == "object"
                and "properties" in prop_schema
                and isinstance(prop_value, dict)
            ):
                # Recursively sanitize nested objects
                nested_sanitized, nested_changes = sanitize_model_details(
                    prop_value,
                    prop_schema,
                    parent_key=f"{current_prefix}{prop_name}".strip(
                        "."
                    ),  # Pass down the nested key path
                )
                sanitized_details[prop_name] = nested_sanitized
                changes["added"].extend(nested_changes["added"])
                changes["removed"].extend(nested_changes["removed"])
            elif (
                prop_type == "array"
                and "items" in prop_schema
                and isinstance(prop_value, list)
            ):
                # Handle arrays of objects if needed
                item_schema = prop_schema.get("items", {})
                if item_schema.get("type") == "object" and "properties" in item_schema:
                    sanitized_array = []
                    for index, item in enumerate(prop_value):
                        if isinstance(item, dict):
                            nested_item_key = f"{current_prefix}{prop_name}[{index}]"
                            nested_sanitized_item, nested_item_changes = sanitize_model_details(
                                item, item_schema, parent_key=nested_item_key
                            )
                            sanitized_array.append(nested_sanitized_item)
                            changes["added"].extend(nested_item_changes["added"])
                            changes["removed"].extend(nested_item_changes["removed"])
                        else:
                            sanitized_array.append(item)  # Keep non-dict items as is
                    sanitized_details[prop_name] = sanitized_array
                else:
                    sanitized_details[prop_name] = (
                        prop_value  # Keep array as is if items are not objects or schema is simple
                    )
            else:
                # Copy other valid properties
                sanitized_details[prop_name] = prop_value
        # else: property not in schema, will be marked as removed later

    # Ensure required properties added earlier are not overwritten if they existed in model_details
    # This logic is implicitly handled by processing existing properties first.
    # If a required prop was missing, it's added. If present, it's processed (and kept).

    # Identify removed keys
    final_keys = set(sanitized_details.keys())
    # Keys removed are those in the original dict but not in the schema's properties
    removed_keys_current_level = original_keys - schema_keys
    for removed_key in removed_keys_current_level:
        changes["removed"].append(f"{current_prefix}{removed_key}")

    return sanitized_details, changes
