import os
import requests
import threading
from typing import List, Optional, Dict, Any
from requests.adapters import HTTPAdapter
from tenacity import retry, wait_random_exponential, stop_after_attempt

from fbpyutils_ai import logging


class OpenAITool():
    _request_semaphore = threading.Semaphore(4)

    def __init__(
        self, 
        model: str, 
        api_key: str, 
        api_base: str = None, 
        embed_model: str = None, 
        api_embed_base: str = None, 
        api_embed_key: str = None,
        timeout: int = 300, 
        session_retries: int = 3
    ):
        """
        Initializes the OpenAITool with the given model, API key, and optional API base URLs.

        Args:
            model (str): The model to use for generating text.
            timeout (int, optional): The timeout for the requests. Defaults to 300.
            session_retries (int, optional): The number of retries for the session. Defaults to 2.
            api_key (str): The API key for authentication.
            api_base (str, optional): The base URL for the API. Defaults to None.
            embed_model (str, optional): The model to use for generating embeddings. Defaults to None.
            api_embed_base (str, optional): The base URL for the embedding API. Defaults to None.
            api_embed_key (str, optional): The API key for the embedding model. Defaults to None.
        """
        _adapter = HTTPAdapter(max_retries=session_retries)

        self.api_key = api_key
        self.model = model
        self.embed_model = embed_model or self.model
        self.session = requests.Session()
        self.timeout = timeout or 300
        self.retries = session_retries or 3
        self.session.mount("http://", _adapter)
        self.session.mount("https://", _adapter)
        self.api_base = api_base or os.environ.get("FBPY_OPENAI_API_BASE") or "https://api.openai.com"
        self.api_embed_base = api_embed_base or self.api_base
        self.api_embed_key = api_embed_key or api_key

    @retry(wait=wait_random_exponential(multiplier=1, max=30), stop=stop_after_attempt(3))
    def _make_request(self, url: str, headers: Dict[str, str], json_data: Dict[str, Any]) -> Any:
        with OpenAITool._request_semaphore:
            try:
                response = self.session.post(url, headers=headers, json=json_data, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout as e:
                print(f"Request timed out: {e}")
                raise
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                raise

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_embed_key}",
        }
        data = {"model": self.embed_model, "input": text}
        try:
            result = self._make_request(f"{self.api_embed_base}/embeddings", headers, data)
            return result["data"][0]["embedding"]
        except (KeyError, IndexError) as e:
            print(f"Error parsing OpenAI response: {e}")
            return None

    def generate_text(self, prompt: str, max_tokens: int = 300) -> str:
        tokens = max_tokens or 300
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {"model": self.model, "prompt": prompt, "max_tokens": tokens}
        try:
            result = self._make_request(f"{self.api_base}/completions", headers, data)
            return result["choices"][0]["text"].strip()
        except (KeyError, IndexError) as e:
            print(f"Error parsing OpenAI response: {e}")
            return ""

    def generate_completions(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {"model": model or self.model, "messages": messages, **kwargs}
        try:
            result = self._make_request(f"{self.api_base}/chat/completions", headers, data)
            if result["choices"] and len(result["choices"]) > 0 and "message" in result["choices"][0] and "content" in result["choices"][0]["message"]:
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"Error parsing OpenAI response: {result}")
                return ""
        except (KeyError, IndexError) as e:
            print(f"Error parsing OpenAI response: {e}")
            return ""
