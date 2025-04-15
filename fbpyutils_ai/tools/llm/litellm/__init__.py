import os
import requests
import json
from typing import Dict, Any

from fbpyutils_ai import logging
import litellm


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
