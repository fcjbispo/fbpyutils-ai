import chromadb
from typing import List, Dict, Any, Tuple, Optional


# Implementation for ChromaDB
class ChromaDB():
    def __init__(
            self,
            distance_function: str = 'l2', 
            persist_directory: str = "./chroma_db", 
            collection_name: str = "default", 
            host: str = None, 
            port: int = None
        ):
        """
        Initializes the ChromaDB with the given persist directory and collection name.

        Args:
            distance_function (str, optional): The distance function to use for similarity search. 
                Valid values are 'l2' (Euclidean distance) or 'cosine' (Cosine similarity). Defaults to 'l2'.
            persist_directory (str, optional): The directory to persist the database. Defaults to "./chroma_db".
            collection_name (str, optional): The name of the collection. Defaults to "default".
            host (str, optional): The host address of the ChromaDB server. Defaults to None.
            port (int, optional): The port number of the ChromaDB server. Defaults to None.
        """
        super().__init__(distance_function=distance_function)

        if host and port:
            self.client = chromadb.HttpClient(host=host, port=port)
        else:
            self.client = chromadb.PersistentClient(path=persist_directory)

        try:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine" if self.distance_function == "cosine" else "l2"}
            )
        except Exception:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine" if self.distance_function == "cosine" else "l2"}
            )

    def add_embeddings(self, ids: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]]):
        """
        Adds embeddings to the ChromaDB collection.

        Args:
            ids (List[str]): The IDs of the embeddings.
            embeddings (List[List[float]]): The embeddings to add.
            metadatas (List[Dict[str, Any]]): The metadata for the embeddings.
        """
        enhanced_metadatas = []
        for id, metadata in zip(ids, metadatas):
            enhanced_metadata = metadata.copy()
            enhanced_metadata["id"] = id
            enhanced_metadatas.append(enhanced_metadata)
        self.collection.upsert(ids=ids, embeddings=embeddings, metadatas=enhanced_metadatas)

    def search_embeddings(self, embedding: List[float], n_results: int = 10) -> List[Tuple[str, float]]:
        """
        Searches for similar embeddings in the ChromaDB collection.

        Args:
            embedding (List[float]): The embedding to search for.
            n_results (int, optional): The number of results to return. Defaults to 10.

        Returns:
            List[Tuple[str, float]]: A list of tuples containing the ID and distance of the similar embeddings.
        """
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            include=["metadatas", "distances"]
        )
        doc_ids = [meta.get("id") for meta in results["metadatas"][0]]
        return list(zip(doc_ids, results["distances"][0]))

    def count(self, where: Optional[Dict[str, Any]] = None) -> int:
        """
        Counts the number of embeddings in the ChromaDB collection.
        Args:
            where (Optional[Dict[str, Any]], optional): A dictionary specifying the filter criteria. Defaults to None.
        Returns:
            int: The number of embeddings in the collection.
        """
        if where:
            # Use get() with where filter and count the results
            results = self.collection.get(
                where=where,
                include=["documents"]  # Minimal include to optimize performance
            )
            return len(results['ids'])
        else:
            # For total count, use count() method
            return self.collection.count()
    
    def get_version(self) -> str:
        """
        Gets the version of the ChromaDB server.

        Returns:
            str: The version of the ChromaDB server, or "unknown" if an error occurred or if using a persistent client.
        """
        try:
            return self.client.get_version()
        except AttributeError:
            print("Error: 'get_version' method not found. Please ensure you are using chromadb version 0.4.15 or higher.")
            return "unknown"
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return "unknown"

    def list_collections(self) -> List[str]:
        """
        Lists all collections in the ChromaDB.
        Returns:
            List[str]: A list of collection names.
        """
        return self.client.list_collections()

    def reset_collection(self):
        """
        Resets the current collection by erasing all documents.
        """
        # Retrieve all document IDs
        doc_ids = self.collection.get()["ids"]

        # Check if there are any documents to delete
        if doc_ids:
            # Delete all documents by their IDs
            self.collection.delete(ids=doc_ids)
            print(f"Deleted {len(doc_ids)} documents from the collection '{self.collection}'.")
        else:
            print("No documents found in the collection.")