# fbpyutils_ai/tools/llm/_base.py
import os
import requests
import threading
from requests.adapters import HTTPAdapter
from tenacity import retry, wait_random_exponential, stop_after_attempt
from typing import Dict, Any, Union, Generator

from fbpyutils_ai import logging
from fbpyutils_ai.tools.http import RequestsManager
# Note: We need OpenAITool for the semaphore, but that creates a circular import.
# We'll access the semaphore via `self.__class__._request_semaphore` inside _make_request.

@retry(
    wait=wait_random_exponential(multiplier=1, max=30), stop=stop_after_attempt(3)
)
def _make_request(
    self, url: str, headers: Dict[str, str], json_data: Dict[str, Any], stream: bool = False
) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
    """
    Wrapper around RequestsManager.make_request that applies the class semaphore for rate limiting.

    Args:
        self: The instance of OpenAITool.
        url: The URL to make the request to.
        headers: The headers to include in the request.
        json_data: The JSON data to include in the request body.
        stream: Whether to stream the response.

    Returns:
        If stream=False, returns the JSON response as a dictionary.
        If stream=True, returns a generator yielding parsed JSON objects from the streaming response.
    """
    # Access semaphore via self.__class__ to avoid circular import
    semaphore = self.__class__._request_semaphore
    logging.debug(f"Attempting to acquire request semaphore. Available: {semaphore._value}")
    with semaphore:
        logging.debug(f"Semaphore acquired. Making request to {url}. Stream={stream}")
        try:
            response = RequestsManager.make_request(
                session=self.session,
                url=url,
                headers=headers,
                json_data=json_data,
                timeout=self.timeout,
                method="POST",  # Assume POST for most LLM API calls
                stream=stream
            )
            logging.debug(f"Request to {url} successful.")
            return response
        except Exception as e:
            logging.error(f"Request to {url} failed after retries: {e}", exc_info=True)
            raise # Re-raise the exception after logging
        finally:
            logging.debug("Semaphore released.")


def _init_logic(
    self,
    model_id: str,
    api_key: str = None,
    api_base: str = None,
    embed_model: str = None,
    api_embed_base: str = None,
    api_embed_key: str = None,
    api_vision_base: str = None,
    api_vision_key: str = None,
    vision_model: str = None,
    timeout: int = 300,
    session_retries: int = 3,
):
    """
    Initializes the OpenAITool instance with models, API keys, and session settings.
    This function is intended to be assigned as the __init__ method of the OpenAITool class.

    Args:
        self: The instance of OpenAITool being initialized.
        model_id (str): The primary model ID for text generation/chat.
        api_key (Optional[str]): API key. Reads from FBPY_OPENAI_API_KEY if None.
        api_base (Optional[str]): Base URL. Reads from FBPY_OPENAI_API_BASE or defaults to OpenAI.
        embed_model (Optional[str]): Model for embeddings. Defaults to model_id.
        api_embed_base (Optional[str]): Base URL for embeddings. Defaults to api_base.
        api_embed_key (Optional[str]): API key for embeddings. Defaults to api_key.
        api_vision_base (Optional[str]): Base URL for vision. Defaults to api_base.
        api_vision_key (Optional[str]): API key for vision. Defaults to api_key.
        vision_model (Optional[str]): Model for vision. Defaults to model_id.
        timeout (int): Request timeout in seconds.
        session_retries (int): Number of retries for session requests.

    Raises:
        ValueError: If API key is missing.
        ValueError: If model_id is missing.
    """
    # Verify and assign the API key
    if not api_key:
        api_key = os.environ.get("FBPY_OPENAI_API_KEY")
        if not api_key:
            logging.error("API key is required but was not provided via argument or environment variable FBPY_OPENAI_API_KEY.")
            raise ValueError("API key is required and was not provided!")
        else:
            logging.info("API key retrieved from environment variable FBPY_OPENAI_API_KEY.")
    else:
        logging.info("API key provided via argument.")
    self.api_key = api_key

    # Configure the model and endpoints
    if not model_id:
        logging.error("Model name is required but was not provided.")
        raise ValueError("Model ID is required and was not provided!")
    self.model_id = model_id
    logging.info(f"Using primary model ID: {self.model_id}")

    self.api_base = api_base or os.environ.get("FBPY_OPENAI_API_BASE") or "https://api.openai.com"
    logging.info(f"API base URL set to: {self.api_base}")

    # Embedding configuration
    self.embed_model = embed_model or self.model_id
    logging.info(f"Using embedding model: {self.embed_model}")
    self.api_embed_base = api_embed_base or self.api_base
    logging.info(f"Embedding API base URL set to: {self.api_embed_base}")
    self.api_embed_key = api_embed_key or self.api_key
    if self.api_embed_key != self.api_key:
        logging.info("Using a separate API key for embeddings.")
    else:
        logging.info("Using the main API key for embeddings.")

    # Vision configuration
    self.vision_model = vision_model or self.model_id
    logging.info(f"Using vision model: {self.vision_model}")
    self.api_vision_base = api_vision_base or self.api_base
    logging.info(f"Vision API base URL set to: {self.api_vision_base}")
    self.api_vision_key = api_vision_key or self.api_key
    if self.api_vision_key != self.api_key:
        logging.info("Using a separate API key for vision.")
    else:
        logging.info("Using the main API key for vision.")

    # Common Headers (may be adjusted per request type if keys differ)
    # Start with embed key, adjust later if needed for vision/base calls
    self.api_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.api_embed_key}", # Default to embed key
    }

    # Add specific headers if needed (e.g., Anthropic)
    if 'api.anthropic.com' in self.api_base.lower():
        # Use the primary api_key for Anthropic header
        self.api_headers["x-api-key"] = self.api_key
        self.api_headers["anthropic-version"] = "2023-06-01"
        # Remove Authorization header if using x-api-key for Anthropic
        if "Authorization" in self.api_headers:
             del self.api_headers["Authorization"]
        logging.info("Added Anthropic specific headers and adjusted auth.")
    # Note: Authorization header might need adjustment in specific methods
    # if vision_key or api_key differs from embed_key and the provider isn't Anthropic.

    # Session configuration
    self.timeout = timeout or 300
    self.retries = session_retries or 3
    logging.info(f"Request timeout set to {self.timeout} seconds.")
    logging.info(f"Session retries set to {self.retries}.")

    _adapter = HTTPAdapter(max_retries=self.retries)
    self.session = requests.Session()
    self.session.mount("http://", _adapter)
    self.session.mount("https://", _adapter)

    # Map for easy access in introspection methods
    self.api_base_map = {
        "base": (self.api_base, self.model_id),
        "embed_base": (self.api_embed_base, self.embed_model),
        "vision_base": (self.api_vision_base, self.vision_model),
    }
