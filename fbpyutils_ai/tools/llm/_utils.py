# fbpyutils_ai/tools/llm/_utils.py
import re
import tiktoken
from typing import List

from fbpyutils_ai import logging

# Note: These functions assume they will be bound to an instance of OpenAITool
# and `generate_tokens` will have access to `self.model_id`.

def _sanitize_json_response(self, raw_response: str) -> str:
    """
    Attempts to extract JSON content enclosed within ```json ... ``` markers,
    or returns the raw response if it looks like JSON already.
    (Bound to the OpenAITool instance)

    Args:
        self: The instance of OpenAITool.
        raw_response (str): The raw string response from the LLM.

    Returns:
        str: The extracted JSON string, or an empty string if not found or invalid.
    """
    logging.debug("Attempting to sanitize JSON response.")
    # Regex to find content between ```json and ```, handling potential leading/trailing whitespace
    match = re.search(r"```json\s*([\s\S]*?)\s*```", raw_response, re.IGNORECASE)
    if match:
        extracted_json = match.group(1).strip()
        logging.info(f"Extracted potential JSON content from markers. Length: {len(extracted_json)}")
        # Basic validation: check if it starts with { and ends with }
        if extracted_json.startswith("{") and extracted_json.endswith("}"):
            logging.debug("Sanitized content seems like a valid JSON object structure.")
            return extracted_json
        else:
            logging.warning("Content extracted from markers does not appear to be a valid JSON object.")
            # Return empty string as the markers were present but content invalid
            return ""
    else:
        logging.debug("Could not find JSON content enclosed in ```json ... ``` markers.")
        # If no ```json``` block, check if the whole response might be JSON
        stripped_response = raw_response.strip()
        if stripped_response.startswith("{") and stripped_response.endswith("}"):
             logging.debug("No ```json``` markers found, but response looks like JSON. Returning raw response.")
             return stripped_response
        else:
             logging.warning("Raw response does not appear to be JSON either.")
             return ""


def generate_tokens(self, text: str) -> List[int]:
    """
    Generates a list of tokens from text using tiktoken, compatible with OpenAI models.
    (Bound to the OpenAITool instance)

    Args:
        self: The instance of OpenAITool.
        text (str): The text to be tokenized.

    Returns:
        List[int]: List of tokens generated from the text.
    """
    logging.debug(f"Generating tokens for text (length: {len(text)}) using base model ID {self.model_id} for encoding lookup.")
    model_to_use = self.model_id
    try:
        # Attempt to get the encoding for the specific model
        encoding = tiktoken.encoding_for_model(model_to_use)
        logging.debug(f"Using tiktoken encoding for model: {model_to_use}")
    except KeyError:
        # If the specific model encoding isn't found, fall back to a common default
        logging.warning(f"Model '{model_to_use}' not found by tiktoken, using default 'cl100k_base' encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    except Exception as e:
         # Catch other potential errors during encoding lookup
         logging.error(f"Unexpected error getting tiktoken encoding for model '{model_to_use}': {e}", exc_info=True)
         logging.warning("Falling back to default 'cl100k_base' encoding due to error.")
         encoding = tiktoken.get_encoding("cl100k_base")

    tokens = encoding.encode(text)
    logging.info(f"Generated {len(tokens)} tokens.")
    return tokens
