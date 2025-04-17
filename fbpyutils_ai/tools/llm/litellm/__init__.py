import os
import threading
from typing import Dict, Any, List, Optional

from fbpyutils_ai import logging
import litellm

from fbpyutils_ai.tools import LLMServiceModel
from fbpyutils_ai.tools.llm import LLMServiceTool

# Import constants from the new file
from .embeddings import generate_embeddings
from .text import generate_text
from .completions import generate_completions
from .tokens import generate_tokens
from .image import describe_image
from .model import (
    list_models as list_models,
    get_model_details as get_model_details
)

litellm.logging = logging
litellm.drop_params = True
os.environ["LITELLM_LOG"] = os.environ.get("FBPY_LOG_LEVEL", "DEBUG").lower()
class LiteLLMServiceTool(LLMServiceTool):
    _request_semaphore = threading.Semaphore(int(os.environ.get("FBPY_SEMAPHORES", 4)))

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

    def generate_embeddings(self, input: List[str], **kwargs) -> Optional[List[float]]:
        return generate_embeddings(self, input, **kwargs)

    def generate_text(
        self,
        prompt: str,
        **kwargs,
    ) -> str:
        return generate_text(self, prompt, **kwargs)

    def generate_completions(self, messages: List[Dict[str, str]], **kwargs) -> str:
        return generate_completions(self, messages, **kwargs)

    def generate_tokens(self, text: str) -> List[int]:
        return generate_tokens(self, text)

    def describe_image(self, image: str, prompt: str, **kwargs) -> str:
        return describe_image(self, image, prompt, **kwargs)

    @staticmethod
    def list_models(api_base_url: str, api_key: str) -> List[Dict[str, Any]]:
        return list_models(api_base_url, api_key)

    @staticmethod
    def get_model_details(
        provider: str,
        api_base_url: str,
        api_key: str,
        model_id: str,
        introspection: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return get_model_details(
            provider, 
            api_base_url, 
            api_key, 
            model_id, 
            introspection,
            **kwargs,
        )
