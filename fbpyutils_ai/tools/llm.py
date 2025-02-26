import os
import base64
import requests
import threading
from typing import List, Optional, Dict, Any
from requests.adapters import HTTPAdapter
from tenacity import retry, wait_random_exponential, stop_after_attempt
import tiktoken  # Library for tokenization compatible with OpenAI models

from fbpyutils_ai import logging


class OpenAITool():
    _request_semaphore = threading.Semaphore(4)

    def __init__(
        self, 
        model: str, 
        api_key: str = None, 
        api_base: str = None, 
        embed_model: str = None, 
        api_embed_base: str = None, 
        api_embed_key: str = None,
        api_vision_base: str = None,
        api_vision_key: str = None,
        vision_model: str = None,
        timeout: int = 300, 
        session_retries: int = 3
    ):
        """
        Initializes the OpenAITool with models and API keys for various functionalities.

        Args:
            model (str): The model to be used for text generation.
            api_key (Optional[str], optional): The API key for authentication. If not provided, 
                attempts to retrieve it from the environment variable "FBPY_OPENAI_API_KEY". If still not found, 
                an exception is raised.
            api_base (str, optional): The base URL for the API. If not provided, uses the value from the environment 
                variable "FBPY_OPENAI_API_BASE" or "https://api.openai.com" as default.
            embed_model (str, optional): The model to be used for generating embeddings. Defaults to the value of `model`.
            api_embed_base (str, optional): The base URL for the embeddings API. Defaults to the value of `api_base`.
            api_embed_key (str, optional): The API key for the embeddings model. Defaults to the value of `api_key`.
            api_vision_base (str, optional): The base URL for the vision API. If not provided, uses the value of `api_base`.
            api_vision_key (str, optional): The API key for the vision API. If not provided, uses the value of `api_key`.
            vision_model (str, optional): The model to be used for the vision API. If not provided, uses the value of `model`.
            timeout (int, optional): Timeout for requests. Default is 300.
            session_retries (int, optional): Number of retries for the session. Default is 3.

        Raises:
            ValueError: If the API key is not provided nor found in the environment variable.
        """
        # Verify and assign the API key
        if not api_key:
            api_key = os.environ.get("FBPY_OPENAI_API_KEY")
            if not api_key:
                raise ValueError("API key is required and was not provided!")
        self.api_key = api_key

        # Configure the model and endpoints
        if not model or model is None:
            raise ValueError("Model is required and was not provided!")
        self.model = model
        self.embed_model = embed_model or self.model
        self.api_base = api_base or os.environ.get("FBPY_OPENAI_API_BASE") or "https://api.openai.com"
        self.api_embed_base = api_embed_base or self.api_base
        self.api_embed_key = api_embed_key or self.api_key

        # Configure parameters for the vision API
        self.api_vision_base = api_vision_base or self.api_base
        self.api_vision_key = api_vision_key or self.api_key
        self.vision_model = vision_model or self.model

        _adapter = HTTPAdapter(max_retries=session_retries)
        self.session = requests.Session()
        self.timeout = timeout or 300
        self.retries = session_retries or 3
        self.session.mount("http://", _adapter)
        self.session.mount("https://", _adapter)

    @retry(wait=wait_random_exponential(multiplier=1, max=30), stop=stop_after_attempt(3))
    def _make_request(self, url: str, headers: Dict[str, str], json_data: Dict[str, Any]) -> Any:
        """
        Makes a POST request to the API with error handling and retries.

        Args:
            url (str): The URL to which the request will be sent.
            headers (Dict[str, str]): HTTP headers for the request.
            json_data (Dict[str, Any]): JSON data to be sent.

        Returns:
            Any: API response in JSON format.
        """
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
        """
        Generates an embedding for a given text using the OpenAI API.

        Args:
            text (str): Text for which the embedding will be generated.

        Returns:
            Optional[List[float]]: List of floats representing the embedding or None in case of an error.
        """
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

    def generate_text(self, prompt: str, max_tokens: int = 300, temperature: int = 0.8, vision: bool = False) -> str:
        """
        Generates text from a prompt using the OpenAI API.

        Args:
            prompt (str): The prompt sent for text generation.
            max_tokens (int, optional): Maximum number of tokens to be generated. Default is 300.
            temperature (int, optional): Temperature of text generation. Default is 0.8.
            vision (bool, optional): If True, uses the vision API. Default is False.

        Returns:
            str: Text generated by the API.
        """        
        api_base = self.api_vision_base if vision else self.api_base
        api_key = self.api_vision_key if vision else self.api_key
        model = self.vision_model if vision else self.model

        tokens = max_tokens or 300
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        data = {"model": model, "prompt": prompt, "max_tokens": tokens, "temperature": temperature}
        try:
            result = self._make_request(f"{api_base}/completions", headers, data)
            return result["choices"][0]["text"].strip()
        except (KeyError, IndexError) as e:
            print(f"Error parsing OpenAI response: {e}")
            return ""

    def generate_completions(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> str:
        """
        Generates a chat response from a list of messages using the OpenAI API.

        Args:
            messages (List[Dict[str, str]]): List of messages that make up the conversation.
            model (str, optional): Model to be used. If not provided, uses the default value.
            **kwargs: Additional parameters for the request.

        Returns:
            str: Response generated by the API.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {"model": model or self.model, "messages": messages, **kwargs}
        try:
            result = self._make_request(f"{self.api_base}/chat/completions", headers, data)
            if (result["choices"] and len(result["choices"]) > 0 and 
                "message" in result["choices"][0] and "content" in result["choices"][0]["message"]):
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"Error parsing OpenAI response: {result}")
                return ""
        except (KeyError, IndexError) as e:
            print(f"Error parsing OpenAI response: {e}")
            return ""

    def generate_tokens(self, text: str) -> List[int]:
        """
        Generates a list of tokens from a text using the tiktoken library,
        compatible with OpenAI models.

        Args:
            text (str): The text to be tokenized.

        Returns:
            List[int]: List of tokens generated from the text.
        """
        model_to_use = self.model
        try:
            encoding = tiktoken.encoding_for_model(model_to_use)
        except Exception:
            # If the model is not recognized, use a default encoding
            encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return tokens

    def describe_image(self, image: str, prompt: str, max_tokens: int = 300, temperature: int = 0.4) -> str:
        """
        Describes an image using the OpenAI API, combining a prompt with the image content.
        The image can be provided as:
            - Path to a local file,
            - Remote URL,
            - or a string already encoded in base64.

        The method converts the image to base64 (when necessary) and adds this information to the prompt,
        which is sent to the configured model to generate a description.

        Args:
            image (str): Path to the local file, remote URL, or base64 content of the image.
            prompt (str): Prompt that guides the image description.
            max_tokens (int, optional): Maximum number of tokens to be generated. Default is 300.
            temperature (int, optional): Temperature of text generation. Default is 0.4.

        Returns:
            str: Description generated by the OpenAI API for the image.
        """
        # Check if the image is a local file
        if os.path.exists(image):
            with open(image, "rb") as img_file:
                image_bytes = img_file.read()
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        # If the image is a remote URL
        elif image.startswith("http://") or image.startswith("https://"):
            try:
                response = requests.get(image, timeout=self.timeout)
                response.raise_for_status()
                image_bytes = response.content
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            except Exception as e:
                print(f"Error downloading the image: {e}")
                return ""
        else:
            # Assume the content is already in base64
            image_base64 = image

        # Construct the prompt including the base64 encoded image information
        full_prompt = (
            f"{prompt}\n\n"
            "Below is the image encoded in base64:\n"
            f"{image_base64}\n\n"
            "Provide a detailed description of the image."
        )

        # Use the generate_text method to obtain the image description
        description = self.generate_text(full_prompt, max_tokens=max_tokens, temperature=temperature, vision=True)
        return description

    def get_models(self, api_base_type: str = "base") -> List[Dict[str, Any]]:
        """
        Retrieves a structured list of all available LLM provider models.

        Args:
            api_base_type (str, optional): Specifies the API endpoint type. Options are "base", "embed_base", or "vision_base".
                Defaults to "base".

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing model metadata such as name, id, version, capabilities, 
            is_tool, is_vision_enabled, is_embedding_model, has_reasoning_capability, context_length, parameter_count, 
            deprecation_status, and availability.

        Raises:
            requests.exceptions.RequestException: If there is an error communicating with the API.

        Usage Examples:
            >>> tool = OpenAITool(model="text-davinci-003", api_key="your_api_key")
            >>> models = tool.get_models(api_base_type="base")
            >>> print(models)

            >>> models = tool.get_models(api_base_type="embed_base")
            >>> print(models)

            >>> models = tool.get_models(api_base_type="vision_base")
            >>> print(models)
        """
        api_base_map = {
            "base": self.api_base,
            "embed_base": self.api_embed_base,
            "vision_base": self.api_vision_base
        }

        if api_base_type not in api_base_map:
            raise ValueError("Invalid api_base_type. Must be 'base', 'embed_base', or 'vision_base'.")

        url = f"{api_base_map[api_base_type]}/models"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            models_data = response.json()

            # Parse and structure the model metadata
            models = []
            for model in models_data.get("models", []):
                models.append({
                    "name": model.get("name"),
                    "id": model.get("id"),
                    "version": model.get("version"),
                    "capabilities": model.get("capabilities", []),
                    "is_tool": model.get("is_tool", False),
                    "is_vision_enabled": model.get("is_vision_enabled", False),
                    "is_embedding_model": model.get("is_embedding_model", False),
                    "has_reasoning_capability": model.get("has_reasoning_capability", False),
                    "context_length": model.get("context_length", 0),
                    "parameter_count": model.get("parameter_count", 0),
                    "deprecation_status": model.get("deprecation_status", False),
                    "availability": model.get("availability", "unknown")
                })

            return models

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to retrieve models: {e}")
            raise
