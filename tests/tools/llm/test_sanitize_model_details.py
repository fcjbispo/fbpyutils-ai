import pytest

from fbpyutils_ai.tools.llm.utils import sanitize_model_details

def test_sanitize_model_details_basic_sanitization():
    """
    Test basic sanitization: adding missing required keys and removing extra keys.
    """
    model_details = {
        "name": "model-a",
        "version": "1.0",
        "extra_key": "should_be_removed"
    }
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "version": {"type": "string"},
            "description": {"type": "string"}
        },
        "required": ["name", "description"]
    }

    sanitized, changes = sanitize_model_details(model_details, schema)

    assert sanitized == {
        "name": "model-a",
        "version": "1.0",
        "description": None
    }
    assert changes == {
        "added": ["description"],
        "removed": ["extra_key"]
    }

def test_sanitize_model_details_nested_object():
    """
    Test sanitization with a nested object.
    """
    model_details = {
        "name": "model-b",
        "config": {
            "param1": 10,
            "extra_param": "remove_me"
        }
    }
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "config": {
                "type": "object",
                "properties": {
                    "param1": {"type": "integer"},
                    "param2": {"type": "string"}
                },
                "required": ["param2"]
            }
        },
        "required": ["name", "config"]
    }

    sanitized, changes = sanitize_model_details(model_details, schema)

    assert sanitized == {
        "name": "model-b",
        "config": {
            "param1": 10,
            "param2": None
        }
    }
    assert changes == {
        "added": ["config.param2"],
        "removed": ["config.extra_param"]
    }

def test_sanitize_model_details_array_of_objects():
    """
    Test sanitization with an array containing objects.
    """
    model_details = {
        "name": "model-c",
        "features": [
            {"id": 1, "enabled": True, "extra": "remove"},
            {"id": 2, "name": "feature-b"}
        ]
    }
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "features": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "enabled": {"type": "boolean"}
                    },
                    "required": ["id", "name"]
                }
            }
        },
        "required": ["name", "features"]
    }

    sanitized, changes = sanitize_model_details(model_details, schema)

    # Helper function to sort keys in nested dictionaries and lists of dictionaries
    def sort_nested_dict_keys(data):
        if isinstance(data, dict):
            return {k: sort_nested_dict_keys(v) for k, v in sorted(data.items())}
        elif isinstance(data, list):
            return [sort_nested_dict_keys(item) for item in data]
        else:
            return data

    assert sort_nested_dict_keys(sanitized) == sort_nested_dict_keys({
        "name": "model-c",
        "features": [
            {"id": 1, "name": None, "enabled": True}, # 'name' is required and missing, 'enabled' is not required
            {"id": 2, "name": "feature-b"} # 'id' and 'name' are present, 'enabled' is not required and missing
        ]
    })
    assert changes == {
        "added": ["features[0].name"], # Only 'name' was added to the first item
        "removed": ["features[0].extra"]
    }

def test_sanitize_model_details_empty_inputs():
    """
    Test sanitization with empty model_details and schema.
    """
    model_details = {}
    schema = {}

    sanitized, changes = sanitize_model_details(model_details, schema)

    assert sanitized == {}
    assert changes == {
        "added": [],
        "removed": []
    }

def test_sanitize_model_details_missing_required_in_nested_object():
    """
    Test adding missing required keys in a nested object.
    """
    model_details = {
        "name": "model-d",
        "config": {
            "param1": 10
        }
    }
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "config": {
                "type": "object",
                "properties": {
                    "param1": {"type": "integer"},
                    "param2": {"type": "string"}
                },
                "required": ["param1", "param2"]
            }
        },
        "required": ["name", "config"]
    }

    sanitized, changes = sanitize_model_details(model_details, schema)

    assert sanitized == {
        "name": "model-d",
        "config": {
            "param1": 10,
            "param2": None
        }
    }
    assert changes == {
        "added": ["config.param2"],
        "removed": []
    }

def test_sanitize_model_details_extra_keys_in_nested_object():
    """
    Test removing extra keys in a nested object.
    """
    model_details = {
        "name": "model-e",
        "config": {
            "param1": 10,
            "extra_param": "remove_me"
        }
    }
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "config": {
                "type": "object",
                "properties": {
                    "param1": {"type": "integer"}
                },
                "required": ["param1"]
            }
        },
        "required": ["name", "config"]
    }

    sanitized, changes = sanitize_model_details(model_details, schema)

    assert sanitized == {
        "name": "model-e",
        "config": {
            "param1": 10
        }
    }
    assert changes == {
        "added": [],
        "removed": ["config.extra_param"]
    }

def test_sanitize_model_details_array_of_non_objects():
    """
    Test sanitization with an array containing non-object items.
    """
    model_details = {
        "name": "model-f",
        "tags": ["tag1", "tag2", "tag3"]
    }
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["name", "tags"]
    }

    sanitized, changes = sanitize_model_details(model_details, schema)

    assert sanitized == {
        "name": "model-f",
        "tags": ["tag1", "tag2", "tag3"]
    }
    assert changes == {
        "added": [],
        "removed": []
    }
