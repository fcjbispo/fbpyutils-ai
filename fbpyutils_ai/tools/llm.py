import os
import json
import base64
import requests
import threading
from jsonschema import validate
from typing import List, Optional, Dict, Any, Union, Generator
from requests.adapters import HTTPAdapter
from tenacity import retry, wait_random_exponential, stop_after_attempt
import tiktoken  # Library for tokenization compatible with OpenAI models

from fbpyutils_ai import logging
from fbpyutils_ai.tools import LLMServices
from fbpyutils_ai.tools.http import RequestsManager


class OpenAITool(LLMServices):
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
        session_retries: int = 3,
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
                logging.error("API key is required but was not provided via argument or environment variable FBPY_OPENAI_API_KEY.")
                raise ValueError("API key is required and was not provided!")
            else:
                logging.info("API key retrieved from environment variable FBPY_OPENAI_API_KEY.")
        else:
            logging.info("API key provided via argument.")
        self.api_key = api_key

        # Configure the model and endpoints
        if not model or model is None:
            logging.error("Model name is required but was not provided.")
            raise ValueError("Model is required and was not provided!")
        self.model = model
        logging.info(f"Using model: {self.model}")
        self.embed_model = embed_model or self.model
        self.api_base = api_base or os.environ.get("FBPY_OPENAI_API_BASE") or "https://api.openai.com"
        logging.info(f"API base URL set to: {self.api_base}")
        self.embed_model = embed_model or self.model
        logging.info(f"Using embedding model: {self.embed_model}")
        self.api_embed_base = api_embed_base or self.api_base
        logging.info(f"Embedding API base URL set to: {self.api_embed_base}")
        self.api_embed_key = api_embed_key or self.api_key
        # Log the embed key carefully, maybe just indicate if it's different from the main key
        if self.api_embed_key != self.api_key:
            logging.info("Using a separate API key for embeddings.")
        else:
            logging.info("Using the main API key for embeddings.")

        self.api_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_embed_key}",
        }

        if 'api.anthropic.com' in self.api_base.lower():
            self.api_headers["x-api-key"] = self.api_key
            self.api_headers["anthropic-version"] = "2023-06-01"
            logging.info("Added Anthropic specific headers.")

        # Configure parameters for the vision API
        self.api_vision_base = api_vision_base or self.api_base
        logging.info(f"Vision API base URL set to: {self.api_vision_base}")
        self.api_vision_key = api_vision_key or self.api_key
        if self.api_vision_key != self.api_key:
            logging.info("Using a separate API key for vision.")
        else:
            logging.info("Using the main API key for vision.")
        self.vision_model = vision_model or self.model
        logging.info(f"Using vision model: {self.vision_model}")

        _adapter = HTTPAdapter(max_retries=session_retries)
        self.session = requests.Session()
        self.timeout = timeout or 300
        self.retries = session_retries or 3
        logging.info(f"Request timeout set to {self.timeout} seconds.")
        logging.info(f"Session retries set to {self.retries}.")
        self.session.mount("http://", _adapter)
        self.session.mount("https://", _adapter)

    @retry(
        wait=wait_random_exponential(multiplier=1, max=30), stop=stop_after_attempt(3)
    )
    def _make_request(
        self, url: str, headers: Dict[str, str], json_data: Dict[str, Any], stream: bool = False
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Wrapper around RequestsManager.make_request that applies the semaphore for rate limiting.
        
        Args:
            url: The URL to make the request to
            headers: The headers to include in the request
            json_data: The JSON data to include in the request body
            stream: Whether to stream the response
            
        Returns:
            If stream=False, returns the JSON response as a dictionary.
            If stream=True, returns a generator yielding parsed JSON objects from the streaming response.
        """
        logging.debug(f"Attempting to acquire request semaphore. Available: {OpenAITool._request_semaphore._value}")
        with OpenAITool._request_semaphore:
            logging.debug(f"Semaphore acquired. Making request to {url}. Stream={stream}")
            try:
                response = RequestsManager.make_request(
                    session=self.session,
                    url=url,
                    headers=headers,
                    json_data=json_data,
                    timeout=self.timeout,
                    method="POST",  # OpenAI API always uses POST method
                    stream=stream
                )
                logging.debug(f"Request to {url} successful.")
                return response
            except Exception as e:
                logging.error(f"Request to {url} failed after retries: {e}", exc_info=True)
                raise # Re-raise the exception after logging
            finally:
                logging.debug("Semaphore released.")

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generates an embedding for a given text using the OpenAI API.

        Args:
            text (str): Text for which the embedding will be generated.

        Returns:
            Optional[List[float]]: List of floats representing the embedding or None in case of an error.
        """
        logging.info(f"Generating embedding for text (length: {len(text)}) using model {self.embed_model}.")
        headers = self.api_headers
        data = {"model": self.embed_model, "input": text}
        try:
            result = self._make_request(
                f"{self.api_embed_base}/embeddings", headers, data
            )
            embedding = result["data"][0]["embedding"]
            logging.info(f"Successfully generated embedding of dimension {len(embedding)}.")
            return embedding
        except (KeyError, IndexError, TypeError) as e:
            logging.error(f"Error parsing OpenAI embedding response: {e}. Response: {result}", exc_info=True)
            return None
        except Exception as e:
            logging.error(f"Failed to generate embedding: {e}", exc_info=True)
            return None

    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 300,
        temperature: float = 0.8,
        vision: bool = False,
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
        api_base = self.api_vision_base if vision else self.api_base
        api_key = self.api_vision_key if vision else self.api_key # Note: api_key is set but not directly used in headers here, inherited via self.api_headers potentially modified by vision settings
        model = self.vision_model if vision else self.model
        logging.info(f"Generating text using model {model} at {api_base}. Vision mode: {vision}.")

        tokens = max_tokens or 300
        headers = self.api_headers.copy() # Use copy to avoid modifying class headers if vision key differs
        if vision and self.api_vision_key != self.api_key:
             headers["Authorization"] = f"Bearer {self.api_vision_key}"

        data = {
            "model": model,
            "prompt": prompt, # Be cautious logging full prompts if they contain sensitive data
            "max_tokens": tokens,
            "temperature": temperature,
        }
        logging.debug(f"Request data (prompt omitted for brevity): { {k: v for k, v in data.items() if k != 'prompt'} }")
        try:
            result = self._make_request(f"{api_base}/completions", headers, data)
            generated_text = result["choices"][0]["text"].strip()
            logging.info(f"Successfully generated text (length: {len(generated_text)}).")
            return generated_text
        except (KeyError, IndexError, TypeError) as e:
            logging.error(f"Error parsing OpenAI text completion response: {e}. Response: {result}", exc_info=True)
            return ""
        except Exception as e:
            logging.error(f"Failed to generate text completion: {e}", exc_info=True)
            return ""

    def generate_completions(
        self, messages: List[Dict[str, str]], model: str = None, **kwargs
    ) -> str:
        """
        Generates a chat response from a list of messages using the OpenAI API.

        Args:
            messages (List[Dict[str, str]]): List of messages that make up the conversation.
            model (str, optional): Model to be used. If not provided, uses the default value.
            **kwargs: Additional parameters for the request.

        Returns:
            str: Response generated by the API.
        """
        logging.info(f"Generating chat completion using model {model or self.model}.")
        headers = self.api_headers
        data = {"model": model or self.model, "messages": messages, **kwargs}
        logging.debug(f"Request data (messages omitted for brevity): { {k: v for k, v in data.items() if k != 'messages'} }")
        try:
            result = self._make_request(
                f"{self.api_base}/chat/completions", headers, data
            )
            logging.debug(f"Raw chat completion response: {result}")
            if (
                result["choices"]
                and len(result["choices"]) > 0
                and "message" in result["choices"][0]
                and "content" in result["choices"][0]["message"]
            ):
                content = result["choices"][0]["message"]["content"].strip()
                logging.info(f"Successfully generated chat completion (length: {len(content)}).")
                return content
            else:
                logging.warning(f"Could not extract content from OpenAI chat response. Response: {result}")
                return ""
        except (KeyError, IndexError, TypeError) as e:
            logging.error(f"Error parsing OpenAI chat completion response: {e}. Response: {result}", exc_info=True)
            return ""
        except Exception as e:
            logging.error(f"Failed to generate chat completion: {e}", exc_info=True)
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
        logging.debug(f"Generating tokens for text (length: {len(text)}) using base model {self.model} for encoding lookup.")
        model_to_use = self.model
        try:
            encoding = tiktoken.encoding_for_model(model_to_use)
            logging.debug(f"Using tiktoken encoding for model: {model_to_use}")
        except Exception as e:
            # If the model is not recognized, use a default encoding
            logging.warning(f"Model '{model_to_use}' not found by tiktoken, using default 'cl100k_base' encoding. Error: {e}")
            encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        logging.info(f"Generated {len(tokens)} tokens.")
        return tokens

    def describe_image(
        self, image: str, prompt: str, max_tokens: int = 300, temperature: float = 0.4
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
        logging.info(f"Describing image: {image}")
        # Check if the image is a local file
        if os.path.exists(image):
            logging.debug(f"Image identified as local file path: {image}")
            try:
                with open(image, "rb") as img_file:
                    image_bytes = img_file.read()
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                logging.debug(f"Successfully read and encoded local image file.")
            except Exception as e:
                logging.error(f"Error reading local image file {image}: {e}", exc_info=True)
                return ""
        # If the image is a remote URL
        elif image.startswith("http://") or image.startswith("https://"):
            logging.debug(f"Image identified as URL: {image}")
            try:
                response = requests.get(image, timeout=self.timeout)
                response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
                image_bytes = response.content
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                logging.debug(f"Successfully downloaded and encoded image from URL.")
            except requests.exceptions.RequestException as e:
                logging.error(f"Error downloading the image from {image}: {e}", exc_info=True)
                return ""
        else:
            # Assume the content is already in base64
            logging.debug("Image assumed to be base64 encoded string.")
            image_base64 = image
            # Basic check for base64 validity could be added here if needed

        # Construct the prompt including the base64 encoded image information
        # Construct the prompt including the base64 encoded image information
        # Avoid logging the full base64 string which can be very large
        full_prompt_template = (
            f"{prompt}\n\n"
            "Below is the image encoded in base64:\n"
            "{image_base64_placeholder}\n\n" # Placeholder used for logging
            "Provide a detailed description of the image."
        )
        logging.debug(f"Constructed vision prompt (base64 image omitted): {full_prompt_template.format(image_base64_placeholder='[BASE64_IMAGE_DATA]')}")

        full_prompt_with_image = (
             f"{prompt}\n\n"
             "Below is the image encoded in base64:\n"
             f"{image_base64}\n\n"
             "Provide a detailed description of the image."
         )

        # Use the generate_text method to obtain the image description
        logging.info(f"Calling generate_text in vision mode for image description.")
        description = self.generate_text(
            full_prompt_with_image, max_tokens=max_tokens, temperature=temperature, vision=True
        )
        if description:
            logging.info(f"Successfully generated image description (length: {len(description)}).")
        else:
            logging.warning("Image description generation returned empty.")
        return description

    def list_models(self, api_base_type: str = "base") -> List[Dict[str, Any]]:
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
        api_base_map = {
            "base": self.api_base,
            "embed_base": self.api_embed_base,
            "vision_base": self.api_vision_base,
        }

        logging.info(f"Listing models for API type: {api_base_type}")
        if api_base_type not in api_base_map:
            logging.error(f"Invalid api_base_type specified: {api_base_type}")
            raise ValueError(
                "Invalid api_base_type. Must be 'base', 'embed_base', or 'vision_base'."
            )

        url = f"{api_base_map[api_base_type]}/models"
        headers = self.api_headers

        response_data = {}
        try:
            logging.debug(f"Requesting models list from {url}")
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
            models_data = response.json()
            logging.debug(f"Received models list response.")

            # Parse and structure the model metadata
            models = []
            if "data" in models_data:
                models_data = models_data.get("data", [])
            for model in models_data:
                models.append(model)

            logging.info(f"Successfully retrieved {len(models)} models for API type {api_base_type}.")
            return models

        except requests.exceptions.RequestException as e:
            # The existing logging.error is good, just ensure response_data is defined even on connection errors
            # It might be better to log the exception directly using exc_info=True
            logging.error(f"Failed to retrieve models from {url}: {e}", exc_info=True)
            raise

    def get_model_details(
        self, model_id: str, max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Retrieves a detailed and structured list of all available LLM provider models.

        Args:
            model_id (str): The ID of the model to retrieve details for.
            max_retries (int, optional): The maximum number of retry attempts for the request. Defaults to 3.
        Returns:
            Dict[str, Any]: A dictionary containing detailed metadata for the specified model ID.
        """
        logging.info(f"Getting detailed capabilities for model: {model_id}")
        llm = self

        with open(
            os.path.sep.join([os.path.dirname(__file__), "resources", "llm_introspection_prompt.md"]), "r", encoding="utf-8",
        ) as f:
            llm_introspection_prompt = f.read()

        with open(
            os.path.sep.join([os.path.dirname(__file__), "resources", "llm_introspection_validation_schema.json"]), "r", encoding="utf-8",
        ) as f:
            llm_introspection_validation_schema = json.load(f)

        messages = [
            {"role": "system", "content": llm_introspection_prompt},
            {
                "role": "user",
                "content": "Please provide your capabilities, strengths, and limitations.",
            },
        ]

        llm_model_capabilities = {
            "model_id": model_id,
            "extraction_ok": False,
            "extraction_error": None,
        }
        tries = 0
        while tries < max_retries: # Use max_retries parameter
            logging.debug(f"Attempt {tries + 1} of {max_retries} to get model details for {model_id}.")
            try:
                json_model_capabilities = llm.generate_completions(
                    messages, model=model_id, temperature=0.0, max_tokens=4096
                )
                model_capabilities = json.loads(json_model_capabilities)

                # Validate the structure of the response
                validate(instance=model_capabilities, schema=llm_introspection_validation_schema)
                logging.info(f"Successfully validated model capabilities JSON schema for {model_id}.")
                llm_model_capabilities.update(model_capabilities)
                llm_model_capabilities["extraction_ok"] = True
                llm_model_capabilities["extraction_error"] = None
                break
                # The 'else' block is removed as jsonschema.validate raises an exception on failure,
                # which will be caught by the 'except Exception' block below.
            except json.JSONDecodeError as e:
                error_msg = f"Failed to decode JSON response: {e}. Response text: {json_model_capabilities}"
                logging.warning(error_msg)
                llm_model_capabilities["extraction_ok"] = False
                llm_model_capabilities["extraction_error"] = error_msg
                messages.append({"role": "assistant", "content": json_model_capabilities}) # Append raw response
                messages.append(
                    {
                        "role": "user",
                        "content": "Invalid JSON format returned. Please provide a valid JSON object.",
                    }
                )
            except Exception as e: # Catch validation errors and other issues
                error_msg = f"Error during model details extraction or validation for {model_id}: {e}"
                logging.error(error_msg, exc_info=True)
            # This duplicate except block is removed.
            # The logic was already incorporated into the main 'except Exception as e' block above.
            tries += 1
            if tries < max_retries:
                 logging.info(f"Retrying model details extraction for {model_id}.")
            else:
                 logging.error(f"Failed to get model details for {model_id} after {max_retries} attempts.")

        return llm_model_capabilities
