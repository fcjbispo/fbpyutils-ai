from typing import List

import tiktoken
from fbpyutils_ai import logging
import litellm

litellm.logging = logging
litellm.drop_params = True


def generate_tokens(self, text: str) -> List[int]:
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
