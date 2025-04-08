# fbpyutils_ai/tools/llm/__init__.py
import os
import re
import time
import json
import base64
import requests
import threading
import datetime
from jsonschema import validate, ValidationError
from typing import List, Optional, Dict, Any, Union, Generator
from requests.adapters import HTTPAdapter
from tenacity import retry, wait_random_exponential, stop_after_attempt
import tiktoken

from fbpyutils_ai import logging
from fbpyutils_ai.tools import LLMServices
from fbpyutils_ai.tools.http import RequestsManager

# Import implementations from submodules
from ._base import _init_logic, _make_request
from ._completion import generate_text, generate_completions
from ._embedding import generate_embedding
from ._vision import describe_image
from ._introspection import list_models, get_model_details, _log_introspection_attempt
from ._utils import _sanitize_json_response, generate_tokens


class OpenAITool(LLMServices):
    """
    Client for interacting with OpenAI compatible APIs (including OpenAI, Anthropic, Ollama, etc.).

    Provides methods for text generation, chat completions, embeddings, vision tasks,
    and model introspection. Handles API key management, endpoint configuration,
    request retries, and rate limiting.
    """
    _request_semaphore = threading.Semaphore(4) # Class level semaphore for rate limiting

    # Assign methods from imported modules
    __init__ = _init_logic
    _make_request = _make_request
    generate_text = generate_text
    generate_completions = generate_completions
    generate_embedding = generate_embedding
    describe_image = describe_image
    list_models = list_models
    get_model_details = get_model_details
    _log_introspection_attempt = _log_introspection_attempt # Keep helper accessible if needed
    _sanitize_json_response = _sanitize_json_response
    generate_tokens = generate_tokens

    # Add alias for consistency if needed, or keep separate
    # chat = generate_completions

    def __repr__(self):
        return f"OpenAITool(model_id='{self.model_id}', api_base='{self.api_base}')"
