# tests/tools/llm/introspection/common.py
import json
from typing import Dict, Any

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

MOCK_SCHEMA = {
    "type": "object",
    "properties": {
        "model_name": {"type": "string"}
    },
    "required": ["model_name"]
}

def create_mock_response(json_data: Dict[str, Any], status_code: int = 200):
    """Helper to create a mock requests response."""
    mock_response = MagicMock()
    mock_response.json.return_value = json_data
    mock_response.raise_for_status = MagicMock()
    mock_response.status_code = status_code
    return mock_response
