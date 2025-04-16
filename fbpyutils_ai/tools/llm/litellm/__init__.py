import os
import threading
import requests
import json
from typing import Dict, Any, List, Optional
from collections import defaultdict # Added import

from fbpyutils_ai import logging
import litellm

from fbpyutils_ai.tools import LLMServiceModel
from fbpyutils_ai.tools.llm import LLMServiceTool

from .embeddings import generate_embeddings
from .text import generate_text
from .completions import generate_completions
from .tokens import generate_tokens
from .image import describe_image
from .model import (
    list_models as list_models,
    get_model_details as get_model_details
)

litellm.logging = logging
litellm.drop_params = True
os.environ["LITELLM_LOG"] = os.environ.get("FBPY_LOG_LEVEL", "DEBUG").lower()

# Constants
MODEL_PRICES_URL = "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"


def __download_model_prices() -> Dict[str, Any]:
    """
    Downloads model prices and context window information from the LiteLLM repository.

    Attempts to fetch the JSON data from the MODEL_PRICES_URL. If the download
    or JSON parsing fails, it logs an error and returns an empty dictionary.

    Returns:
        Dict[str, Any]: A dictionary containing the model prices and context window
                        information, or an empty dictionary if an error occurred.
    """
    try:
        logging.debug(f"Attempting to download model prices from: {MODEL_PRICES_URL}")
        response = requests.get(MODEL_PRICES_URL, timeout=10)  # Added timeout
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        model_prices = response.json()
        logging.info("Successfully downloaded and parsed model prices.")
        return model_prices
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading model prices from {MODEL_PRICES_URL}: {e}")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from {MODEL_PRICES_URL}: {e}")
        return {}
    except Exception as e: # Catch any other unexpected errors
        logging.error(f"An unexpected error occurred while downloading model prices: {e}")
        return {}


MODEL_PRICES_AND_CONTEXT_WINDOW = __download_model_prices()

PROVIDERS = []
if MODEL_PRICES_AND_CONTEXT_WINDOW: # Check if download was successful
    PROVIDERS = list(set(
        data['provider']
        for key, data in MODEL_PRICES_AND_CONTEXT_WINDOW.items()
        if key != "sample_spec" and 'provider' in data # Ensure provider key exists
    ))
    logging.debug(f"Extracted providers: {PROVIDERS}")

MODEL_PRICES_AND_CONTEXT_WINDOW_BY_PROVIDER: Dict[str, Dict[str, Any]] = defaultdict(dict)
if MODEL_PRICES_AND_CONTEXT_WINDOW: # Check if download was successful
    logging.debug("Grouping models by provider...")
    for model_name, model_data in MODEL_PRICES_AND_CONTEXT_WINDOW.items():
        if model_name == "sample_spec":
            continue
        provider = model_data.get('provider')
        if provider: # Check if provider exists for the model
            MODEL_PRICES_AND_CONTEXT_WINDOW_BY_PROVIDER[provider][model_name] = model_data
        else:
            logging.warning(f"Model '{model_name}' is missing 'provider' key. Skipping.")
    logging.info("Finished grouping models by provider.")



class LiteLLMServiceTool(LLMServiceTool):
    _request_semaphore = threading.Semaphore(int(os.environ.get("FBPY_SEMAPHORES", 4)))

    def __init__(
        self,
        base_model: LLMServiceModel,
        embed_model: Optional[LLMServiceModel] = None,
        vision_model: Optional[LLMServiceModel] = None,
        timeout: int = 300,
        session_retries: int = 3,
    ):
        super().__init__(
            base_model, embed_model, vision_model, timeout, session_retries
        )

    def generate_embeddings(self, input: List[str], **kwargs) -> Optional[List[float]]:
        return generate_embeddings(self, input, **kwargs)

    def generate_text(
        self,
        prompt: str,
        **kwargs,
    ) -> str:
        return generate_text(self, prompt, **kwargs)

    def generate_completions(self, messages: List[Dict[str, str]], **kwargs) -> str:
        return generate_completions(self, messages, **kwargs)

    def generate_tokens(self, text: str) -> List[int]:
        return generate_tokens(self, text)

    def describe_image(self, image: str, prompt: str, **kwargs) -> str:
        return describe_image(self, image, prompt, **kwargs)

    @staticmethod
    def list_models(api_base_url: str, api_key: str) -> List[Dict[str, Any]]:
        return list_models(api_base_url, api_key)

    @staticmethod
    def get_model_details(
        provider: str,
        api_base_url: str,
        api_key: str,
        model_id: str,
        introspection: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return get_model_details(
            provider, 
            api_base_url, 
            api_key, 
            model_id, 
            introspection,
            **kwargs,
        )
