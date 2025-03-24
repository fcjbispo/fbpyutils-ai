from typing import Any, Optional, Dict, List, Tuple
import httpx
import logging
from time import perf_counter
from abc import ABC, abstractmethod


# Interface for the vector database
class VectorDatabase(ABC):
    def __init__(self, distance_function: str = "l2"):
        distance_function = distance_function or "l2"
        if distance_function not in ("cosine", "l2"):
            raise ValueError(
                f"Invalid distance function {f}. Valid values are: cosine|l2."
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


# Interface for the LLM service
class LLMServices(ABC):
    @abstractmethod
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generates an embedding for the given text."""
        pass

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generates text from a prompt."""
        pass

    @abstractmethod
    def generate_completions(
        self, messages: List[Dict[str, str]], model: str = None, **kwargs
    ) -> str:
        """Generates text from a chat completion."""
        pass

    @abstractmethod
    def generate_tokens(self, text: str) -> List[int]:
        """Generates tokens from a text."""
        pass

    @abstractmethod
    def describe_image(
        self, image: str, prompt: str, max_tokens: int = 300, temperature: int = 0.4
    ) -> str:
        """Describes an image."""
        pass

    @abstractmethod
    def list_models(self, api_base_type: str = "base") -> List[Dict[str, Any]]:
        """Lists the available models."""
        pass

    @abstractmethod
    def get_model_details(
        self, model_id: str, api_base_type: str = "base"
    ) -> List[Dict[str, Any]]:
        """Gets the details of a model."""
        pass
