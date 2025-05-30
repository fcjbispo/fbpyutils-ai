import os
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any, Optional, Dict, List, Tuple


# Interface for the vector database
class VectorDatabase(ABC):
    def __init__(self, distance_function: str = "l2"):
        distance_function = distance_function or "l2"
        if distance_function not in ("cosine", "l2"):
            raise ValueError(
                f"Invalid distance function {distance_function}. Valid values are: cosine|l2."
            )
        self.distance_function = distance_function

    @abstractmethod
    def add_embeddings(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
    ):
        """Adds embeddings to the database."""
        pass

    @abstractmethod
    def search_embeddings(
        self, embedding: List[float], n_results: int = 10
    ) -> List[Tuple[str, float]]:
        """Searches for similar embeddings in the database."""
        pass

    @abstractmethod
    def get_version(self) -> str:
        """Gets the version of the database server."""
        pass

    @abstractmethod
    def count(self, where: Optional[Dict[str, Any]] = None) -> int:
        """Counts the number of embeddings in the collection."""
        pass

    @abstractmethod
    def list_collections(self) -> List[str]:
        """Lists all collections in the database."""
        pass

    @abstractmethod
    def reset_collection(self):
        """Resets the current collection by erasing all documents."""
        pass


class LLMServiceModel(BaseModel):
    provider: str
    api_base_url: str
    api_key: str
    is_local: bool = False
    model_id: str

    @staticmethod
    def get_llm_service_model(
        model_id: str, provider: Dict[str, Any]
    ) -> "LLMServiceModel":
        return LLMServiceModel(
            provider=provider["provider"].lower(),
            api_base_url=provider["base_url"],
            api_key=os.environ.get(provider["env_api_key"]),
            is_local=provider.get("is_local", False),
            model_id=model_id,
        )

    # the __str__ method should hash the api_key in order to protect sensitive data
    def __str__(self) -> str:
        return f"LLMServiceModel(provider={self.provider}, api_base_url={self.api_base_url}, api_key=HASHED, model_id={self.model_id})"


# Interface for the LLM service
class LLMService(ABC):
    def __init__(
        self,
        base_model: LLMServiceModel,
        embed_model: Optional[LLMServiceModel] = None,
        vision_model: Optional[LLMServiceModel] = None,
        timeout: int = 300,
        session_retries: int = 3,
    ):
        self.model_map = {
            "base": base_model,
            "embed": embed_model or base_model,
            "vision": vision_model or base_model,
        }
        self.timeout = timeout or 300
        self.retries = session_retries or 3

    @abstractmethod
    def generate_embeddings(self, input: List[str]) -> Optional[List[float]]:
        """Generates an embedding for the given list of text."""
        pass

    @abstractmethod
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generates text from a prompt."""
        pass

    @abstractmethod
    def generate_completions(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generates text from a chat completion."""
        pass

    @abstractmethod
    def generate_tokens(self, text: str, **kwargs) -> List[int]:
        """Generates tokens from a text."""
        pass

    @abstractmethod
    def describe_image(self, image: str, prompt: str, **kwargs) -> str:
        """Describes an image."""
        pass

    @abstractmethod
    def get_model_details(
        self,
        model_type: str = "base",
        introspection: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Gets the details of a model."""
        pass

    @staticmethod
    @abstractmethod
    def get_providers() -> List[Dict[str, Any]]:
        """Lists the available providers."""
        pass

    @staticmethod
    @abstractmethod
    def list_models(**kwargs) -> List[Dict[str, Any]]:
        """Lists the available models."""
        pass
