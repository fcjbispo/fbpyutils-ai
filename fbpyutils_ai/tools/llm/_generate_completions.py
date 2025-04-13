from typing import Dict, List
from fbpyutils_ai import logging
import litellm

litellm.logging = logging
litellm.drop_params = True


def generate_completions(
    self, messages: List[Dict[str, str]], **kwargs
) -> str:
    try:
        if not messages or len(messages) == 0:
            raise ValueError("Messages cannot be empty.")

        base_type = 'base'
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        kwargs['stream'] = kwargs.get('stream', False)
        kwargs['prompt'] = messages

        response = litellm.text_completion(
            api_base=self.model_map[base_type].api_base_url,
            api_key=self.model_map[base_type].api_key,
            model=self._resolve_model(base_type),
            **kwargs
        )

        if response:
            if response.get('choices', [{}])[0].get('message', {}):
                return response['choices'][0]['message']
            else:
                raise ValueError(f"Invalid model response: {response}.")
        else:
            raise ValueError(f"Invalid model response format: {type(response)}.")
    except Exception as e:
        logging.error(f"Invalid model provider response: {e} - {response}")
        return None
