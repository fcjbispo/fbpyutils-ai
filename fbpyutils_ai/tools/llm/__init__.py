import os
import json
import base64
import requests
import threading
from typing import List, Optional, Dict, Any, Union, Generator
from tenacity import retry, wait_random_exponential, stop_after_attempt
from jsonschema import validate, ValidationError

import tiktoken  

from fbpyutils_ai import logging
from fbpyutils_ai.tools import LLMService, LLMServiceModel
from fbpyutils_ai.tools.http import RequestsManager, basic_header

from ._utils import get_llm_resources

import litellm
from litellm import get_supported_openai_params

litellm.logging = logging
litellm.drop_params = True

os.environ["LITELLM_LOG"] = os.environ.get("FBPY_LOG_LEVEL", "DEBUG").lower()

(
    LLM_PROVIDERS, 
    LLM_ENDPOINTS, 
    LLM_COMMON_PARAMS, 
    LLM_INTROSPECTION_PROMPT, 
    LLM_INTROSPECTION_VALIDATION_SCHEMA
) = get_llm_resources()


class LLMServiceTool(LLMService):
    _request_semaphore = threading.Semaphore(
        os.environ.get("FBPY_SEMAPHORES", 4)
    )

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
        try:
            if not input or len(input) == 0:
                raise ValueError("Input cannot be empty.")

            base_type = 'embed'
            kwargs['timeout'] = kwargs.get('timeout', self.timeout)
            kwargs['encoding_format'] = kwargs.get('encoding_format', 'float')
            response = litellm.embedding(
                api_base=self.model_map[base_type].api_base_url,
                api_key=self.model_map[base_type].api_key,
                model=self._resolve_model(base_type),
                input=input,
                **kwargs
            )
            if response and type(response) == dict:
                if response.get('data', [{}])[0].get('embedding', []):
                    return response['data'][0]['embedding']
                else:
                    raise ValueError(f"Invalid model response: {response}.")
            else:
                raise ValueError(f"Invalid model response format: {type(response)}.")
        except Exception as e:
            logging.error(f"Invalid model provider response: {e} - {response}")
            return None

    def _generate_text(
        self,
        prompt: str,
        base_type: str = "base",
        **kwargs,
    ) -> str:
        """
        Generates text from a prompt using the OpenAI API.

        Args:
            prompt (str): The prompt sent for text generation.
            base_type (str): The type of model to use.
            **kwargs: Additional parameters for the request.

        Returns:
            str: Text generated by the API.
        """
        try:
            if not prompt or len(prompt) == 0:
                raise ValueError("Prompt cannot be empty.")

            base_type = base_type or 'base'
            kwargs['timeout'] = kwargs.get('timeout', self.timeout)
            kwargs['stream'] = kwargs.get('stream', False)

            response = litellm.text_completion(
                api_base=self.model_map[base_type].api_base_url,
                api_key=self.model_map[base_type].api_key,
                model=self._resolve_model(base_type),
                prompt=[prompt],
                **kwargs
            )

            if response and type(response) == dict:
                if response.get('choices', [{}])[0].get('text', None):
                    return response['choices'][0]['text']
                else:
                    raise ValueError(f"Invalid model response: {response}.")
            else:
                raise ValueError(f"Invalid model response format: {type(response)}.")
        except Exception as e:
            logging.error(f"Invalid model provider response: {e} - {response}")
            return None
        

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
        return self._generate_text(prompt, **kwargs)
    

    def generate_completions(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> str:
        """
        Generates a chat response from a list of messages using the OpenAI API.

        Args:
            messages (List[Dict[str, str]]): List of messages that make up the conversation.
            **kwargs: Additional parameters for the request.

        Returns:
            str: Response generated by the API.
        """
        try:
            if not messages or len(messages) == 0:
                raise ValueError("Messages cannot be empty.")

            base_type = 'base'
            kwargs['timeout'] = kwargs.get('timeout', self.timeout)
            kwargs['stream'] = kwargs.get('stream', False)

            response = litellm.text_completion(
                api_base=self.model_map[base_type].api_base_url,
                api_key=self.model_map[base_type].api_key,
                model=self._resolve_model(base_type),
                messages=[messages],
                **kwargs
            )

            if response and type(response) == dict:
                if response.get('choices', [{}])[0].get('message', {}):
                    return response['choices'][0]['message']
                else:
                    raise ValueError(f"Invalid model response: {response}.")
            else:
                raise ValueError(f"Invalid model response format: {type(response)}.")
        except Exception as e:
            logging.error(f"Invalid model provider response: {e} - {response}")
            return None

    def generate_tokens(self, text: str) -> List[int]:
        """
        Generates a list of tokens from a text using the tiktoken library,
        compatible with OpenAI models.

        Args:
            text (str): The text to be tokenized.

        Returns:
            List[int]: List of tokens generated from the text.
        """
        model_to_use = self.model_map["base"].model_id
        try:
            try:
                encoding = tiktoken.encoding_for_model(model_to_use)
            except Exception:
                encoding = tiktoken.get_encoding("cl100k_base")
            tokens = encoding.encode(text)
            return tokens
        except Exception as e:
            logging.error(f"Error parsing model provider response: {e}")
            return None

    def describe_image(
        self, image: str, prompt: str, **kwargs
    ) -> str:
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
        ## , max_tokens: int = 300, temperature: float = 0.4
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

        kwargs['max_tokens'] = kwargs.get('max_tokens', 300)
        kwargs['temperature'] = kwargs.get('temperature', 0.4)

        return self._generate_text(full_prompt, 'vision', **kwargs)
    

    @staticmethod
    def list_models(self, api_base_url: str, api_key: str) -> List[Dict[str, Any]]:
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
        if not all([api_base_url, api_key]):
            raise ValueError("api_base_ur and api_key must be provided.")

        url = f"{api_base_url}/models"

        headers = basic_header()
        headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        })

        if 'api.anthropic.com' in api_base_url.lower():
            headers["x-api-key"] = api_base_url
            headers["anthropic-version"] = "2023-06-01"

        response_data = {}
        try:
            response = self._make_request(url=url, headers=headers, method="GET", timeout=self.timeout)
            models_data = response.json()

            # Parse and structure the model metadata
            models = []
            if "data" in models_data:
                models_data = models_data.get("data", [])
            for model in models_data:
                models.append(model)

            return models

        except requests.exceptions.RequestException as e:
            logging.error(
                f"Failed to retrieve models: {e}. Response data: {response_data}"
            )
            raise

    def get_model_details(
        self, provider: str, api_base_ur: str, api_key: str, model_id: str
    ) -> Dict[str, Any]:
        if not all([provider, api_base_ur, api_key]):
            raise ValueError("provider, api_base_ur, and api_key must be provided.")
            
        response_data = {}
        try:
            messages = [
                {"role": "system", "content": LLM_INTROSPECTION_PROMPT},
                {"role": "user", "content": "Please list me ALL the details about this model."},
            ]

            api_provider = provider.lower()
            api_base = api_base_ur

            if api_provider == "lm_studio":
                response_format = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "llm_introspection_validation_schema",
                        "strict": "true",
                        "schema": LLM_INTROSPECTION_VALIDATION_SCHEMA,
                        "required": ["llm_introspection_validation_schema"]
                    }
                }
            else:
                response_format = {
                    "type": "json_schema",
                    "schema": LLM_INTROSPECTION_VALIDATION_SCHEMA,
                    "strict": True,
                }
            response_format = None

            try: 
                response = litellm.completion(
                    model=f"{api_provider}/{model_id}",
                    messages=messages,
                    api_base=api_base,
                    api_key=api_key,
                    timeout=3000,
                    max_retries=3,
                    top_p=1,
                    temperature=0.0,
                    stream=False,
                    response_format=response_format,
                )

                contents = response.get('choices',[{}])[0].get('message', {}).get('content')

                if contents:
                    llm_model_details = json.loads(contents.replace("```json", "").replace("```", ""))
                else:
                    print("No content found in the response.")
                    llm_model_details = {}

                try:
                    llm_model_details = json.loads(contents.replace("```json", "").replace("```", ""))
                    try:
                        validate(instance=llm_model_details, schema=LLM_INTROSPECTION_VALIDATION_SCHEMA)

                        supported_params = get_supported_openai_params(
                            model=model_id, custom_llm_provider=api_provider
                        ) or LLM_COMMON_PARAMS
                        llm_model_details['supported_ai_parameters'] = supported_params 

                        llm_model_details['model_id'] = model_id
                    except ValidationError as e:
                        raise Exception(f"JSON Validation error: {e}")
                except json.JSONDecodeError as e:
                    raise Exception(f"Error decoding JSON: {e}")
            except Exception as e:
                llm_model_details = {
                    "error": str(e),
                    "message": "An error occurred while fetching model details.",
                }

            return llm_model_details
        except Exception as e:
            logging.error(
                f"Failed to retrieve model details: {e}. Response data: {response_data}"
            )
            raise
