import os
import threading
from typing import List, Optional, Dict, Any, Union, Generator
from tenacity import retry, wait_random_exponential, stop_after_attempt

from fbpyutils_ai import logging
from fbpyutils_ai.tools import LLMService, LLMServiceModel
from fbpyutils_ai.tools.http import RequestsManager, basic_header

from ._utils import get_llm_resources
from ._generate_embeddings import generate_embeddings
from ._generate_text import generate_text
from ._generate_completions import generate_completions
from ._generate_tokens import generate_tokens
from ._describe_image import describe_image
from ._list_models import list_models
from ._get_model_details import get_model_details

import litellm


litellm.logging = logging
litellm.drop_params = True
os.environ["LITELLM_LOG"] = os.environ.get("FBPY_LOG_LEVEL", "DEBUG").lower()


class LLMServiceTool(LLMService):
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
        self.session = RequestsManager.create_session()
        self.session.headers.update(basic_header())

    def _resolve_model(self, map_type: str = "base") -> LLMServiceModel:
        try:
            model = self.model_map[map_type]
            return f"{model.provider.lower()}/{model.model_id}"
        except KeyError:
            return self._resolve_model()

    @retry(
        wait=wait_random_exponential(multiplier=1, max=30), stop=stop_after_attempt(3)
    )
    def _make_request(
        self,
        url: str,
        headers: Dict[str, str],
        json_data: Dict[str, Any],
        timeout: int,
        stream: bool = False,
        method: str = "POST",
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Wrapper around RequestsManager.make_request that applies the semaphore for rate limiting.

        Args:
            url: The URL to make the request to
            headers: The headers to include in the request
            json_data: The JSON data to include in the request body
            stream: Whether to stream the response
            method: The HTTP method to use for the request

        Returns:
            If stream=False, returns the JSON response as a dictionary.
            If stream=True, returns a generator yielding parsed JSON objects from the streaming response.
        """
        headers = headers or self.session.headers
        json_data = json_data or {}
        method = (method or "POST").upper()
        if method not in ["GET", "POST"]:
            raise ValueError(f"Unsupported HTTP method: {method}")
        with LLMServiceTool._request_semaphore:
            return RequestsManager.make_request(
                session=self.session,
                url=url,
                headers=headers,
                json_data=json_data,
                timeout=timeout or self.timeout,
                method=method,
                stream=stream,
            )

    def generate_embeddings(self, input: List[str], **kwargs) -> Optional[List[float]]:
        """
        Generates an embedding for a given text using the OpenAI API.

        Args:
            text (str): Text for which the embedding will be generated.
            **kwargs: Additional parameters for the request.

        Returns:
            Optional[List[float]]: List of floats representing the embedding or None in case of an error.
        """
        return generate_embeddings(self, input, **kwargs)

    def generate_text(
        self,
        prompt: str,
        **kwargs,
    ) -> str:
        """
        Generates text from a prompt using the OpenAI API.

        Args:
            prompt (str): The prompt sent for text generation.
            **kwargs: Additional parameters for the request.

        Returns:
            str: Text generated by the API.
        """
        return generate_text(self, prompt, **kwargs)

    def generate_completions(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Generates a chat response from a list of messages using the OpenAI API.

        Args:
            messages (List[Dict[str, str]]): List of messages that make up the conversation.
            **kwargs: Additional parameters for the request.

        Returns:
            str: Response generated by the API.
        """
        return generate_completions(self, messages, **kwargs)

    def generate_tokens(self, text: str) -> List[int]:
        """
        Generates a list of tokens from a text using the tiktoken library,
        compatible with OpenAI models.

        Args:
            text (str): The text to be tokenized.

        Returns:
            List[int]: List of tokens generated from the text.
        """
        return generate_tokens(self, text)

    def describe_image(self, image: str, prompt: str, **kwargs) -> str:
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
        return describe_image(self, image, prompt, **kwargs)

    @staticmethod
    def list_models(api_base_url: str, api_key: str) -> List[Dict[str, Any]]:
        """
        Retrieves a structured list of all available LLM provider models.

        Args:
            api_base_type (str, optional): Specifies the API endpoint type. Options are "base", "embed_base", or "vision_base".
                Defaults to "base".

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing model metadata.

        Raises:
            requests.exceptions.RequestException: If there is an error communicating with the API.

        Usage Examples:
            >>> tool = OpenAITool(model="text-davinci-003", api_key="your_api_key")
            >>> models = tool.list_models(api_base_type="base")
            >>> print(models)

            >>> models = tool.list_models(api_base_type="embed_base")
            >>> print(models)

            >>> models = tool.list_models(api_base_type="vision_base")
            >>> print(models)
        """
        return list_models(api_base_url, api_key)

    @staticmethod
    def get_model_details(
        provider: str,
        api_base_ur: str,
        api_key: str,
        model_id: str,
        introspection: bool = False,
    ) -> Dict[str, Any]:
        return get_model_details(provider, api_base_ur, api_key, model_id, introspection)
