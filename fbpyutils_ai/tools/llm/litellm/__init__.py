import os
import threading
from typing import Dict, Any, List, Optional

from fbpyutils_ai import logging
import litellm

from fbpyutils_ai.tools import LLMServiceModel
from fbpyutils_ai.tools.llm import LLMServiceTool
from fbpyutils_ai.tools.llm.litellm.info import ModelPricesAndContextWindow

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
    _model_prices_and_context_window = ModelPricesAndContextWindow()

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
    def get_providers() -> List[Dict[str, Any]]:
        """Lists the available models."""
        providers = LLMServiceTool.get_providers()
        return [
            p for p in providers.values() 
            if p['provider'] in LiteLLMServiceTool._model_prices_and_context_window.get_providers()
            or p['is_local']
        ]

    @staticmethod
    def list_models(api_base_url: str, api_key: str) -> List[Dict[str, Any]]:

        llm_providers = [p for p in LiteLLMServiceTool.get_providers() if p['base_url'] == api_base_url]
        if len(llm_providers) > 0:
            llm_provider = llm_providers[0]
            provider, api_base_url, api_key, _, _ = llm_provider.values()

            models = LLMServiceTool.list_models(api_base_url, api_key)
            llm_models = LiteLLMServiceTool._model_prices_and_context_window.get_model_prices_and_context_window_by_provider(provider)

            def select_model(model, llm_models):
                model_id = model['id']
                if provider == 'ollama':
                    model_id.replace(':latest', '')

                llm_model = llm_models.get(model_id)
                if not llm_model:
                    model_id = f"{provider}/{model['id']}"
                    llm_model = llm_models.get(model_id)
                if llm_model:
                    model['id'] = model_id
                    model.update(llm_model)
                return model
            return [select_model(m, llm_models) for m in models]
        else:
            raise ValueError(f"Provider {provider} not found")

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
