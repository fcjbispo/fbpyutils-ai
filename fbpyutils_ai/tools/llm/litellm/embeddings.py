from fbpyutils_ai import logging
import litellm

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
        response = litellm.embedding(
            api_base=self.model_map[base_type].api_base_url,
            api_key=self.model_map[base_type].api_key,
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
