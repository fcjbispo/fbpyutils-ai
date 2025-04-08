# fbpyutils_ai/tools/llm/_embedding.py
from typing import Optional, List

from fbpyutils_ai import logging

# Note: This function assumes it will be bound to an instance of OpenAITool
# and will have access to `self._make_request`, `self.api_embed_base`, `self.embed_model`, etc.

def generate_embedding(self, text: str) -> Optional[List[float]]:
    """
    Generates an embedding for a given text using the configured embedding endpoint.

    Args:
        self: The instance of OpenAITool.
        text (str): Text for which the embedding will be generated.

    Returns:
        Optional[List[float]]: List of floats representing the embedding, or None on error.
    """
    logging.info(f"Generating embedding for text (length: {len(text)}) using model {self.embed_model}.")

    headers = self.api_headers.copy()
    # Ensure the correct API key for embeddings is used in the header
    # This handles cases where the embed key might differ from the base/vision key
    is_anthropic = 'api.anthropic.com' in self.api_embed_base.lower()
    if not is_anthropic:
        headers["Authorization"] = f"Bearer {self.api_embed_key}"
        logging.debug("Set Authorization header for embedding request.")
    elif "x-api-key" in headers: # Ensure correct key for Anthropic if it was set differently in __init__
        headers["x-api-key"] = self.api_embed_key # Anthropic uses x-api-key
        logging.debug("Set x-api-key header for Anthropic embedding request.")
    # If neither, the default header from __init__ (using embed_key) should be correct.

    data = {"model": self.embed_model, "input": text}

    # Determine the correct endpoint path
    endpoint_path = "/embeddings" # Standard OpenAI path
    api_base = self.api_embed_base.rstrip('/')
    if "/v1" not in api_base: # Simple check, might need refinement
        api_base += "/v1"

    url = f"{api_base}{endpoint_path}"
    logging.debug(f"Embedding request URL: {url}")


    try:
        result = self._make_request(url, headers, data)
        # Standard OpenAI embedding response structure
        if result and "data" in result and result["data"] and "embedding" in result["data"][0]:
            embedding = result["data"][0]["embedding"]
            logging.info(f"Successfully generated embedding of dimension {len(embedding)}.")
            return embedding
        else:
            logging.warning(f"Could not extract embedding from response. Response: {result}")
            return None
    except (KeyError, IndexError, TypeError) as e:
        response_data = locals().get("result", "N/A")
        logging.error(f"Error parsing embedding response: {e}. Response: {response_data}", exc_info=True)
        return None
    except Exception as e:
        logging.error(f"Failed to generate embedding: {e}", exc_info=True)
        return None
