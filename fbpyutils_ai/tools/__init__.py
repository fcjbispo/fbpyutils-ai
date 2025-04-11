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
    model_id: str

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
            'base': base_model,
            'embed': embed_model or base_model,
            'vision': vision_model or base_model,
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
    @staticmethod
    def list_models(**kwargs) -> List[Dict[str, Any]]:
        """Lists the available models."""
        pass

    @abstractmethod
    @staticmethod
    def get_model_details(**kwargs) -> Dict[str, Any]:
        """Gets the details of a model."""
        pass
