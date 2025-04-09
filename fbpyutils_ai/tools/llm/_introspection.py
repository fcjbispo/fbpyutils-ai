# fbpyutils_ai/tools/llm/_introspection.py
import os
import re
import time
import json
import datetime
import requests
from jsonschema import validate, ValidationError
from typing import List, Dict, Any, Optional

from fbpyutils_ai import logging

# Note: These functions assume they will be bound to an instance of OpenAITool
# and will have access to `self.session`, `self.api_headers`, `self.timeout`,
# `self.api_base_map`, `self._generate_completions`, `self._sanitize_json_response`, etc.

def list_models(self, api_base_type: str = "base") -> List[Dict[str, Any]]:
    """
    Retrieves a structured list of available models from the specified API endpoint type.

    Args:
        self: The instance of OpenAITool.
        api_base_type (str): Specifies the API endpoint type ("base", "embed_base", "vision_base").

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing model metadata.

    Raises:
        ValueError: If api_base_type is invalid.
        requests.exceptions.RequestException: If the API request fails.
    """
    logging.info(f"Listing models for API type: {api_base_type}")
    api_base_type = api_base_type or "base"
    if api_base_type not in self.api_base_map:
        logging.error(f"Invalid api_base_type specified: {api_base_type}")
        raise ValueError(
            "Invalid api_base_type. Must be 'base', 'embed_base', or 'vision_base'."
        )
    api_base, _ = self.api_base_map[api_base_type]

    # Determine the correct endpoint path
    endpoint_path = "/models" # Standard OpenAI path
    url = f"{api_base.rstrip('/')}{endpoint_path}"
    # Adjust if /v1 is needed and not already present
    if "/v1" not in api_base and "/models" not in api_base: # Avoid double /v1/models
         url = f"{api_base.rstrip('/')}/v1{endpoint_path}"
    logging.debug(f"Requesting models list from {url}")


    headers = self.api_headers.copy()
    # Adjust auth header if needed for the specific base type's key
    key_for_base = self.api_key # Default for 'base'
    if api_base_type == "embed_base":
        key_for_base = self.api_embed_key
    elif api_base_type == "vision_base":
        key_for_base = self.api_vision_key

    is_anthropic = 'api.anthropic.com' in api_base.lower()
    if not is_anthropic:
        headers["Authorization"] = f"Bearer {key_for_base}"
    elif "x-api-key" in headers: # Ensure correct key for Anthropic
        headers["x-api-key"] = key_for_base

    try:
        response = self.session.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status() # Raises HTTPError for bad responses
        models_data = response.json()
        logging.debug(f"Received models list response.")

        # Parse and structure the model metadata (handle variations)
        models = []
        if isinstance(models_data, dict) and "data" in models_data:
            # OpenAI-like structure
            models_list = models_data.get("data", [])
        elif isinstance(models_data, list):
             # Direct list structure (some providers might return this)
             models_list = models_data
        elif isinstance(models_data, dict) and "models" in models_data:
             # Ollama-like structure
             models_list = models_data.get("models", [])
        else:
             logging.warning(f"Unrecognized format for models list response: {type(models_data)}")
             models_list = []

        # Extract relevant info (adjust based on common fields)
        for model_info in models_list:
            if isinstance(model_info, dict):
                 # Only append if the model has an 'id' field
                 if model_info.get("id"):
                     models.append(model_info)
                 else:
                     logging.warning(f"Skipping model entry without 'id': {model_info.get('name', 'N/A')}")
            elif isinstance(model_info, str):
                 models.append({"id": model_info}) # Handle simple list of names

        logging.info(f"Successfully retrieved {len(models)} models for API type {api_base_type}.")
        return models

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve models from {url}: {e}", exc_info=True)
        raise
    except json.JSONDecodeError as e:
         logging.error(f"Failed to decode JSON response from {url}: {e}", exc_info=True)
         # Attempt to get raw text if possible
         raw_text = "N/A"
         if 'response' in locals() and hasattr(response, 'text'):
             raw_text = response.text[:500] # Log first 500 chars
         logging.debug(f"Raw response text (preview): {raw_text}")
         raise # Re-raise as JSONDecodeError is a valid failure


def _log_introspection_attempt(
    self,
    log_info: str,
    attempt: int,
    message: str,
    data: Optional[Any] = None
):
    """
    Helper function to write introspection attempt details to a log file.
    (Bound to the OpenAITool instance)

    Args:
        self: The instance of OpenAITool.
        log_info (str): The log info to log on.
        attempt (int): The current attempt number.
        message (str): The log message.
        data (Optional[Any]): Additional data to log (e.g., raw response, error details).
    """
    try:
        # Try pretty printing if it's JSON-like, otherwise just write string
        data = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    except TypeError:
        data = str(data) + "\n"
    logging.debug(f'{log_info}, Attempt #{attempt}, Response: {message}, Data:\n{data}')


def get_model_details(
    self, model_id: str = None, api_base_type: str = "base", max_retries: int = 3
) -> Dict[str, Any]:
    """
    Retrieves detailed capabilities for a specified LLM model ID using introspection.
    Logs raw responses and errors to a debug file in the current directory, prefixed with '.sandbox.'.
    (Bound to the OpenAITool instance)

    Args:
        self: The instance of OpenAITool.
        model_id (str, Optional): The ID of the model to retrieve details for. Defaults to the model defined for the api_base_type.
        api_base_type (str): Specifies the API endpoint type ("base", "embed_base", "vision_base").
        max_retries (int): Maximum number of retry attempts for the request.

    Returns:
        Dict[str, Any]: A dictionary containing detailed metadata for the specified model ID,
                        including extraction status and attempts.
    """
    # Nested helper function specific to get_model_details context
    def _generate_completions_for_details(
        llm_instance: Any, # Type hint as Any to avoid circular dependency if OpenAITool is needed
        target_api_base: str,
        target_model_id: str,
        messages_list: List[Dict[str, str]],
        **kwargs
    ) -> str:
        # Temporarily override api_base and model_id for the specific call within the instance
        original_api_base = llm_instance.api_base
        original_model_id = llm_instance.model_id
        llm_instance.api_base = target_api_base
        llm_instance.model_id = target_model_id
        try:
            # Call the bound generate_completions method of the instance
            response = llm_instance.generate_completions(messages_list, **kwargs)
        finally:
            # Restore original settings
            llm_instance.api_base = original_api_base
            llm_instance.model_id = original_model_id
        return response

    logging.info(f"Getting detailed capabilities for model: {model_id}")
    api_base_type = api_base_type or "base"
    if api_base_type not in self.api_base_map:
        logging.error(f"Invalid api_base_type specified: {api_base_type}")
        raise ValueError(
            "Invalid api_base_type. Must be 'base', 'embed_base', or 'vision_base'."
        )

    api_base, default_model_for_type = self.api_base_map[api_base_type]
    effective_model_id = model_id or default_model_for_type

    # Load resources relative to this file's location
    current_dir = os.path.dirname(__file__)
    prompt_path = os.path.join(current_dir, "resources", "llm_introspection_prompt.md")
    schema_path = os.path.join(current_dir, "resources", "llm_introspection_validation_schema.json")

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            llm_introspection_prompt = f.read()
        with open(schema_path, "r", encoding="utf-8") as f:
            llm_introspection_validation_schema = json.load(f)
    except FileNotFoundError as e:
        logging.error(f"Could not load introspection resources: {e}", exc_info=True)
        return {
            "model_id": effective_model_id, "extraction_ok": False,
            "extraction_error": f"Resource file not found: {e.filename}", "extraction_attempts": 0,
        }
    except json.JSONDecodeError as e:
        logging.error(f"Could not parse introspection validation schema: {e}", exc_info=True)
        return {
            "model_id": effective_model_id, "extraction_ok": False,
            "extraction_error": f"Invalid JSON in schema file: {schema_path}", "extraction_attempts": 0,
        }

    # --- Setup Debug Logging ---
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    sanitized_api_base = re.sub(r'[:/\\?*"<>|]+', '_', api_base.replace("http://", "").replace("https://", ""))
    sanitized_model_id = re.sub(r'[\\/*?:"<>|]+', "_", effective_model_id)
    debug_log_file = f".sandbox.{sanitized_api_base}_{sanitized_model_id}_{timestamp}.log"
    logging.info(f"Logging introspection attempts to: {debug_log_file}")
    # --- End Debug Logging Setup ---

    messages = [{"role": "user", "content": llm_introspection_prompt}]

    llm_model_capabilities = {
        "model_id": effective_model_id, "extraction_ok": False,
        "extraction_error": "Max retries reached without valid response.",
        "extraction_attempts": 0, "sanitization_required": False,
        "extraction_duration_seconds": 0.0,
    }
    tries = 0
    start_time = time.monotonic()
    raw_model_response = ""

    while tries < max_retries:
        tries += 1
        llm_model_capabilities["extraction_attempts"] = tries
        logging.debug(f"Attempt {tries} of {max_retries} to get model details for {effective_model_id}.")

        try:
            response_format_arg = {}
            # Use self.api_base here as it's the target for the _generate_completions_for_details call
            if "api.openai.com" in self.api_base or "/v1" in self.api_base:
                response_format_arg = {"response_format": {"type": "json_object"}}
                logging.debug("Requesting JSON object response format.")

            # Call the nested helper, passing the instance (self)
            raw_model_response = _generate_completions_for_details(
                self, # Pass the instance
                target_api_base=api_base,
                target_model_id=effective_model_id,
                messages_list=messages,
                temperature=0.0,
                max_tokens=4096,
                **response_format_arg
            )

            # Log raw response using the bound method
            self._log_introspection_attempt(debug_log_file, tries, "Raw LLM Response:", raw_model_response)

            # --- Direct JSON parsing ---
            try:
                logging.debug("Attempting direct JSON parsing.")
                model_capabilities = json.loads(raw_model_response)
                validate(instance=model_capabilities, schema=llm_introspection_validation_schema)
                logging.info(f"Successfully parsed and validated JSON directly for {effective_model_id} on attempt {tries}.")
                llm_model_capabilities.update(model_capabilities)
                llm_model_capabilities["extraction_ok"] = True
                llm_model_capabilities["extraction_error"] = None
                self._log_introspection_attempt(debug_log_file, tries, "Direct JSON parsing and validation successful.")
                break

            except json.JSONDecodeError as decode_error:
                log_msg = f"Direct JSON parsing failed: {decode_error}"
                logging.warning(f"{log_msg} on attempt {tries}. Raw response length: {len(raw_model_response)}")
                logging.debug(f"Raw response (first 500 chars): {raw_model_response[:500]}")
                self._log_introspection_attempt(debug_log_file, tries, log_msg, {"raw_response_preview": raw_model_response[:500]})
                llm_model_capabilities["extraction_error"] = log_msg

                # --- Sanitize and parse ---
                # Use the bound _sanitize_json_response method
                sanitized_response = self._sanitize_json_response(raw_model_response)
                if sanitized_response:
                    logging.info("Attempting to parse sanitized JSON.")
                    self._log_introspection_attempt(debug_log_file, tries, "Attempting sanitized JSON parsing.", {"sanitized_response": sanitized_response})
                    try:
                        model_capabilities = json.loads(sanitized_response)
                        validate(instance=model_capabilities, schema=llm_introspection_validation_schema)
                        logging.info(f"Successfully parsed and validated sanitized JSON for {effective_model_id} on attempt {tries}.")
                        llm_model_capabilities.update(model_capabilities)
                        llm_model_capabilities["extraction_ok"] = True
                        llm_model_capabilities["extraction_error"] = None
                        llm_model_capabilities["sanitization_required"] = True
                        self._log_introspection_attempt(debug_log_file, tries, "Sanitized JSON parsing and validation successful.")
                        break
                    except json.JSONDecodeError as sanitize_decode_error:
                        error_msg = f"Sanitized JSON parsing failed: {sanitize_decode_error}"
                        logging.warning(f"{error_msg} on attempt {tries}")
                        self._log_introspection_attempt(debug_log_file, tries, error_msg, {"sanitized_response": sanitized_response})
                        llm_model_capabilities["extraction_error"] = error_msg
                    except ValidationError as sanitize_validate_error:
                        error_msg = f"Sanitized JSON validation failed: {sanitize_validate_error.message} on path {list(sanitize_validate_error.path)}"
                        logging.warning(f"{error_msg} on attempt {tries}")
                        self._log_introspection_attempt(debug_log_file, tries, error_msg, {"instance": sanitize_validate_error.instance})
                        llm_model_capabilities["extraction_error"] = error_msg
                else:
                    error_msg = f"JSON sanitization failed to extract valid content on attempt {tries}."
                    logging.warning(error_msg)
                    self._log_introspection_attempt(debug_log_file, tries, error_msg)
                    llm_model_capabilities["extraction_error"] = error_msg

            except ValidationError as validate_error:
                error_msg = f"Direct JSON validation failed: {validate_error.message} on path {list(validate_error.path)}"
                logging.warning(f"{error_msg} on attempt {tries}")
                self._log_introspection_attempt(debug_log_file, tries, error_msg, {"instance": validate_error.instance})
                llm_model_capabilities["extraction_error"] = error_msg

        except Exception as api_error: # Catch errors from _generate_completions_for_details
            error_msg = f"API call failed on attempt {tries} for {effective_model_id}: {api_error}"
            logging.error(error_msg, exc_info=True)
            self._log_introspection_attempt(debug_log_file, tries, f"API call failed: {api_error}")
            llm_model_capabilities["extraction_error"] = error_msg

        # --- Prepare for next attempt ---
        if tries < max_retries and not llm_model_capabilities["extraction_ok"]:
            logging.info(f"Preparing for retry attempt {tries + 1} for {effective_model_id}.")
            max_error_response_len = 1000
            error_response_content = raw_model_response
            if len(error_response_content) > max_error_response_len:
                 error_response_content = error_response_content[:max_error_response_len] + "... (truncated)"
            messages.append({"role": "assistant", "content": error_response_content})
            messages.append({
                "role": "user",
                "content": f"The previous response was not valid JSON or did not match the schema. Error: {llm_model_capabilities['extraction_error']}. Please provide ONLY a valid JSON object strictly adhering to the schema, without any comments, markdown formatting, or extra text.",
            })
            self._log_introspection_attempt(debug_log_file, tries, "Preparing for retry.", {"next_user_message": messages[-1]["content"]})
        elif not llm_model_capabilities["extraction_ok"]:
            final_error_msg = f"Failed to get valid model details for {effective_model_id} after {max_retries} attempts. Last error: {llm_model_capabilities['extraction_error']}"
            logging.error(final_error_msg)
            self._log_introspection_attempt(debug_log_file, tries, final_error_msg)
            logging.debug(f"Final raw response for {effective_model_id} after all retries: {raw_model_response}")

    end_time = time.monotonic()
    llm_model_capabilities["extraction_duration_seconds"] = round(end_time - start_time, 2)
    log_final_status = f"Model details extraction for {effective_model_id} completed in {llm_model_capabilities['extraction_duration_seconds']:.2f} seconds. Success: {llm_model_capabilities['extraction_ok']}"
    logging.info(log_final_status)
    self._log_introspection_attempt(debug_log_file, tries, log_final_status, {"final_result": llm_model_capabilities})

    return llm_model_capabilities
