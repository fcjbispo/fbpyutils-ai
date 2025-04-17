# fbpyutils_ai/tools/llm/litellm/constants.py
import json
import requests
from collections import defaultdict
from typing import Dict, Any, List
from pydantic import BaseModel

from fbpyutils_ai import logging


class ModelPricesAndContextWindow(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        __model_prices_url = "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"

        def download_model_prices() -> Dict[str, Any]:
            """
            Downloads model prices and context window information from the LiteLLM repository.

            Attempts to fetch the JSON data from the MODEL_PRICES_URL. If the download
            or JSON parsing fails, it logs an error and returns an empty dictionary.

            Returns:
                Dict[str, Any]: A dictionary containing the model prices and context window
                                information, or an empty dictionary if an error occurred.
            """
            url = __model_prices_url
            try:
                logging.debug(f"Attempting to download model prices from: {url}")
                response = requests.get(url, timeout=10)  # Added timeout
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
                model_prices = response.json()
                return model_prices
            except requests.exceptions.RequestException as e:
                logging.error(f"Error downloading model prices from {url}: {e}")
                return {}
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from {url}: {e}")
                return {}
            except Exception as e: # Catch any other unexpected errors
                logging.error(f"An unexpected error occurred while downloading model prices: {e}")
                return {}

        self.__prices_and_context_window = download_model_prices()

    def get_model_prices_and_context_window(self) -> Dict[str, Any]:
        return self.__prices_and_context_window
    
    def get_providers(self) -> List[str]:
        providers: List[str] = []
        if self.__prices_and_context_window: # Check if download was successful
            providers = list(set(
                data['litellm_provider']
                for key, data in self.__prices_and_context_window.items()
                if key != "sample_spec" and 'litellm_provider' in data # Ensure provider key exists
            ))
        return providers

    def get_model_prices_and_context_window_by_provider(self, provider: str) -> Dict[str, Dict[str, Any]]:
        if not provider:
            raise ValueError("Provider must be provided.")
        model_prices_and_context_window_by_provider: Dict[str, Dict[str, Any]] = defaultdict(dict)
        if self.__prices_and_context_window: # Check if download was successful
            for model_name, model_data in self.__prices_and_context_window.items():
                model_provider = model_data.get('litellm_provider')
                if model_name == "sample_spec" or model_provider != provider:
                    continue
                if model_provider: # Check if provider exists for the model
                    model_prices_and_context_window_by_provider[model_name] = model_data
        return model_prices_and_context_window_by_provider
