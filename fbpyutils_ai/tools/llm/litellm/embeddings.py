
import os
import litellm
from fbpyutils_ai import logging

litellm.logging = logging
litellm.drop_params = True


from typing import List, Optional


def generate_embeddings(self, input: List[str], **kwargs) -> Optional[List[float]]:
    try:
        if not input or len(input) == 0:
            raise ValueError("Input cannot be empty.")
        
        base_type = "embed"
        kwargs["timeout"] = kwargs.get("timeout", self.timeout)
        kwargs["encoding_format"] = kwargs.get("encoding_format", "float")

        provider = self.model_map[base_type].provider
        os.environ[f"{provider.upper()}_API_BASE"] = self.model_map[base_type].api_base_url
        os.environ[f"{provider.upper()}_API_KEY"] = self.model_map[base_type].api_key
        response = litellm.embedding(
            model=self._resolve_model(base_type),
            input=input,
            **kwargs,
        )
        if response:
            if response.get("data", [{}])[0].get("embedding", []):
                return response["data"][0]["embedding"]
            else:
                raise ValueError(f"Invalid model response: {response}.")
        else:
            raise ValueError(f"Invalid model response format: {type(response)}.")
    except Exception as e:
        logging.error(f"Invalid model provider response: {e} - {response}")
        return None
