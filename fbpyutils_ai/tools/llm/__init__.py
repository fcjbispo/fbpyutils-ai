from abc import abstractmethod
import base64
import json
import os
import threading
from typing import List, Optional, Dict, Any, Tuple, Union, Generator
from jsonschema import ValidationError, validate
import requests
from tenacity import wait_random_exponential, stop_after_attempt
import tiktoken

from fbpyutils_ai.tools import LLMService, LLMServiceModel
from fbpyutils_ai.tools.http import RequestsManager, basic_header
from fbpyutils_ai.tools.llm.utils import (
    get_api_model_response, 
    get_llm_resources, 
    sanitize_model_details
)
from fbpyutils_ai import logging


(
    LLM_PROVIDERS,
    LLM_COMMON_PARAMS,
    LLM_INTROSPECTION_PROMPT,
    LLM_INTROSPECTION_VALIDATION_SCHEMA,
) = get_llm_resources()


class OpenAILLMService(LLMService):
    _request_semaphore = threading.Semaphore(int(os.environ.get("FBPY_SEMAPHORES", 4)))

    def __init__(
        self,
        base_model: LLMServiceModel,
        embed_model: Optional[LLMServiceModel] = None,
        vision_model: Optional[LLMServiceModel] = None,
        timeout: int = 300,
        retries: int = 3,
    ):
        super().__init__(base_model, embed_model, vision_model, timeout, retries)
        self.session = RequestsManager.create_session()
        self.session.headers.update(basic_header())

    def _resolve_model(self, model_type: str = "base") -> LLMServiceModel:
        try:
            model = self.model_map[model_type]
            return f"{model.provider}/{model.model_id}"
        except KeyError:
            return self._resolve_model()
        
    def _resolve_headers(self, model: LLMServiceModel) -> Dict[str, str]:
        headers = self.session.headers.copy()
        headers["Content-Type"] = "application/json"
        headers['Authorization'] = f"Bearer {model.api_key}"
        if model.provider == "anthropic":
            headers["x-api-key"] = model.api_key
            headers["anthropic-version"] = "2023-06-01"
        return headers

    # Removed local retry decorator, relying on RequestsManager retry
    def _make_request(
        self,
        url: str,
        headers: Dict[str, str],
        json_data: Dict[str, Any],
        timeout: int,
        stream: bool = False,
        method: str = "POST",
    ) -> requests.Response:
        """
        Wrapper around RequestsManager.make_request that applies the semaphore for rate limiting.

        Args:
            url: The URL to make the request to
            headers: The headers to include in the request
            json_data: The JSON data to include in the request body
            stream: Whether to stream the response
            method: The HTTP method to use for the request

        Returns:
            requests.Response: The raw requests.Response object. The caller is responsible
                               for processing the response (e.g., calling response.json()
                               for non-streaming or iterating over response.iter_lines()
                               for streaming).
        """
        headers = headers or self.session.headers.copy()

        json_data = json_data or {}
        method = (method or "POST").upper()
        if method not in ["GET", "POST", "PUT", "DELETE"]:
             raise ValueError(f"Unsupported HTTP method: {method}")
        with OpenAILLMService._request_semaphore:
            response = RequestsManager.make_request(
                session=self.session,
                url=url,
                headers=headers,
                json_data=json_data,
                timeout=timeout or self.timeout,
                method=method,
                stream=stream,
            )
            # Return the raw response object. Caller is responsible for parsing.
            return response

    def generate_embeddings(self, input: List[str]) -> Optional[List[float]]:
        """
        Generates an embedding for a given text using the OpenAI API.

        Args:
            text (str): Text for which the embedding will be generated.

        Returns:
            Optional[List[float]]: List of floats representing the embedding or None in case of an error.
        """
        model = self.model_map["embed"]
        headers = self._resolve_headers(model)
        url = f"{model.api_base_url}/embeddings"
        data = {
            "model": model.model_id, 
            "input": input
        }
        try:
            response = self._make_request(
                url, headers, data, timeout=self.timeout, stream=False
            )
            result = response.json()
            return result["data"][0]["embedding"]
        except (KeyError, IndexError) as e:
            print(f"Error parsing OpenAI response: {e}")
            return None

    def generate_text(
        self,
        prompt: str,
        vision: bool = False,
        **kwargs
    ) -> str:
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
        model_type = "vision" if vision else "base"
        model = self.model_map[model_type]
        headers = self._resolve_headers(model)
        timeout = kwargs.get("timeout", self.timeout)
        stream = kwargs.get("stream", False)
        url = f"{model.api_base_url}/completions"
        data = {
            "model": model.model_id,
            "prompt": prompt,
            **kwargs,
        }
        try:
            response = self._make_request(url, headers, data, timeout=timeout, stream=stream)
            result = response.json()
            return result["choices"][0]["text"].strip()
        except (KeyError, IndexError) as e:
            print(f"Error parsing OpenAI response: {e}")
            return ""

    def generate_completions(
        self, messages: List[Dict[str, str]], stream: bool = False, **kwargs
    ) -> Union[str, Generator[Dict[str, Any], None, None]]:
        """
        Generates a chat response from a list of messages using the OpenAI API.

        Args:
            messages (List[Dict[str, str]]): List of messages that make up the conversation.
            model (str, optional): Model to be used. If not provided, uses the default value.
            **kwargs: Additional parameters for the request.

        Returns:
            Union[str, Generator[Dict[str, Any], None, None]]: Response generated by the API.
            If stream=False, returns the text response as a string.
            If stream=True, returns a generator yielding parsed JSON objects from the streaming response.
        """
        model = self.model_map["base"]
        headers = self._resolve_headers(model)
        timeout = kwargs.pop("timeout", self.timeout)
        url = f"{model.api_base_url}/chat/completions"
        data = {
            "model": model.model_id, 
            "messages": messages, 
            **kwargs
        }
        try:
            response = self._make_request(url, headers, data, stream=stream, timeout=timeout)

            if stream:
                # Handle streaming response
                def generate_stream():
                    for line in response.iter_lines():
                        if line:
                            line = line.decode('utf-8')
                            if line.startswith('data:') and not 'data: [DONE]' in line:
                                json_str = line[5:].strip()
                                if json_str:
                                    try:
                                        yield json.loads(json_str)
                                    except json.JSONDecodeError as e:
                                        logging.error(f"Error decoding JSON stream chunk: {e}, line: {json_str}")
                return generate_stream()
            else:
                # Handle non-streaming response
                result = response.json()
                if (
                    result.get("choices")
                    and len(result["choices"]) > 0
                    and "message" in result["choices"][0]
                    and "content" in result["choices"][0]["message"]
                ):
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    logging.error(f"Error parsing OpenAI response: {result}")
                    return ""
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logging.error(f"Error processing OpenAI response: {e}")
            return ""
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error during OpenAI completion: {e}")
            raise # Re-raise the exception after logging

    def generate_tokens(self, text: str) -> List[int]:
        """
        Generates a list of tokens from a text using the tiktoken library,
        compatible with OpenAI models.

        Args:
            text (str): The text to be tokenized.

        Returns:
            List[int]: List of tokens generated from the text.
        """
        model = self.model_map['base']
        try:
            encoding = tiktoken.encoding_for_model(model.model_id)
        except Exception:
            # If the model is not recognized, use a default encoding
            encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return tokens

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
            image (str): Path to the local file, remote HTTP URL, or base64 content of the image.
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
        description = self.generate_text(
            full_prompt, vision=True, **kwargs
        )
        return description

    def get_model_details(
        self,
        model_type: str = 'base',
        introspection: bool = False,
    ) -> Dict[str, Any]:
        """Gets the details of a model."""
        model = self.model_map[model_type]
        timeout= self.timeout
        retries= self.retries
        provider, model_id, api_base_url, api_key = (
            model.provider, 
            model.model_id,
            model.api_base_url, # Corrected attribute name
            model.api_key
        )

        # Remove local retries, rely on HTTPClient retry
        response_data = {}
        try:
            url = f"{api_base_url}/models/{model_id}"
            if provider == "openrouter":
                url += "/endpoints"

            logging.info(f"Fetching model details from: {url}")
            # Assuming get_api_model_response uses HTTPClient or RequestsManager internally
            # and will benefit from the centralized retry logic.
            response = get_api_model_response(url, api_key, timeout=timeout)
            try:
                response_data = response.json()
                logging.info(f"Model basic details fetched successfully: {response_data}")
            except Exception as e:
                logging.error(f"Error parsing model basic details response: {e}")
                raise e

            if introspection:
                def _parse_response(
                        response: Any, 
                        introspection_report: Dict[str, Any]
                ) -> Tuple[Dict[str, Any], str | None, Dict[str, Any]]:
                    if isinstance(response, requests.Response):
                        contents = (
                            response.get("choices", [{}])[0]
                            .get("message", {})
                            .get("content")
                        )
                    elif isinstance(response, dict):
                        contents = json.dumps(response, ensure_ascii=False, default=str)
                    else:
                        contents = str(response)

                    parse_error = None
                    model_details = {}
                    if contents:
                        try:
                            model_details = json.loads(
                                contents.replace("```json", "").replace("```", "")
                            )
                            validate(
                                instance=model_details,
                                schema=LLM_INTROSPECTION_VALIDATION_SCHEMA,
                            )
                            introspection_report["generation_ok"] = True
                        except ValidationError as e:
                            parse_error = f"JSON Validation error: {e}. JSON: {model_details}"
                        except json.JSONDecodeError as e:
                            parse_error = f"Error decoding JSON: {e}. JSON: {model_details}"
                        if parse_error is not None:
                            logging.info(parse_error)
                            introspection_report["decode_error"] = True
                    else:
                        parse_error = "No content found in the response."
                        logging.warning(parse_error)
                    
                    return introspection_report, parse_error, model_details

                response_format = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "llm_introspection_validation_schema",
                        "strict": True,
                        "schema": LLM_INTROSPECTION_VALIDATION_SCHEMA,
                        "required": ["llm_introspection_validation_schema"],
                    },
                }

                llm_model_details = {}
                introspection_report = {
                    "attempts": 0, 
                    "generation_ok": False,
                    "decode_error": False,
                    "validation_error": False,
                    "sanitized": False,
                    "sanitize_changes": {},
                }

                messages = [
                    {"role": "system", "content": LLM_INTROSPECTION_PROMPT},
                    {
                        "role": "user",
                        "content": "Please list me ALL the details about this model.",
                    },
                ]

                while (
                    (introspection_report["attempts"] < retries) and (not introspection_report["generation_ok"])
                ):
                    attempt_no = introspection_report["attempts"]
                    logging.info(f"Performing model introspection for: {model_id}. Attempt #{attempt_no+1}.")

                    try:
                        response = self.generate_completions(
                            messages=messages,
                            stream=False,
                            timeout=timeout,
                            top_p=1,
                            temperature=0.0,
                            response_format=response_format,
                        )
                        (
                            introspection_report, 
                            parse_error, 
                            llm_model_details
                        ) = _parse_response(response, introspection_report)
                    except Exception as e:
                        parse_error = f"An error occurred while fetching model details from the LLM: {e.message}."
                        response = f"Attempt #{attempt_no+1} failed with error: {parse_error}."
                        logging.info(parse_error)

                    if parse_error is not None:
                        introspection_report["attempts"] += 1
                        for m in [
                            {
                                "role": "assistant",
                                "content": response,
                            },
                            {
                                "role": "user",
                                "content": f"This is the attempt {attempt_no+1}/{retries}. The expected JSON format was not returned. Please try again and ensure the output is a valid JSON object an defined on the provided schema. The error was: {parse_error}",
                            }
                        ]:
                            messages.append(m)
                        
                if not introspection_report["generation_ok"]:
                    sanitized_details, sanitize_changes = sanitize_model_details(
                        llm_model_details, LLM_INTROSPECTION_VALIDATION_SCHEMA
                    )
                    llm_model_details = sanitized_details  # Update with sanitized version
                    introspection_report["sanitized"] = True
                    introspection_report["sanitize_changes"] = (
                        sanitize_changes  # Store changes
                    )
                    logging.info(f"Sanitization applied. Changes: {sanitize_changes}")

                response_data["introspection"] = llm_model_details
                response_data["introspection"]["report"] = introspection_report

            return response_data
        except Exception as e:
            logging.error(
                f"Failed to retrieve model details: {e}. Response data: {response_data}"
            )
            raise


    @staticmethod
    def get_providers() -> List[Dict[str, Any]]:
        """Lists the available providers."""
        return LLM_PROVIDERS

    @staticmethod
    def list_models(
        api_base_url: str, api_key: str, **kwargs: Any
    ) -> List[Dict[str, Any]]:
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
        response = get_api_model_response(url, api_key, **kwargs)
        # get_api_model_response already returns the JSON data, no need to call .json() again
        models_data = response.json() if isinstance(response, requests.Response) else {}

        # Parse and structure the model metadata
        models = []
        if "data" in models_data:
            models_data = models_data.get("data", [])
        for model in models_data:
            models.append(model)

        return models
