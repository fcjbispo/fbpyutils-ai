# Standard library imports
import json
import os
import hashlib
from typing import List, Dict, Any, Tuple, Optional

# Third-party imports
import chromadb
import psycopg
from pgvector.psycopg import register_vector
from pinecone import Pinecone, ServerlessSpec

from fbpyutils_ai import logging
from fbpyutils_ai.tools import LLMServices, VectorDatabase


# Implementation for ChromaDB
class ChromaDB(VectorDatabase):
    def __init__(
        self,
        distance_function: str = "l2",
        persist_directory: str = "./chroma_db",
        collection_name: str = "default",
        host: str = None,
        port: int = None,
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
                metadata={
                    "hnsw:space": (
                        "cosine" if self.distance_function == "cosine" else "l2"
                    )
                },
            )
        except Exception:
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={
                    "hnsw:space": (
                        "cosine" if self.distance_function == "cosine" else "l2"
                    )
                },
            )

    def add_embeddings(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
    ):
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
        self.collection.upsert(
            ids=ids, embeddings=embeddings, metadatas=enhanced_metadatas
        )

    def search_embeddings(
        self, embedding: List[float], n_results: int = 10
    ) -> List[Tuple[str, float]]:
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
            include=["metadatas", "distances"],
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
                include=["documents"],  # Minimal include to optimize performance
            )
            return len(results["ids"])
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
            print(
                "Error: 'get_version' method not found. Please ensure you are using chromadb version 0.4.15 or higher."
            )
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
            print(
                f"Deleted {len(doc_ids)} documents from the collection '{self.collection}'."
            )
        else:
            print("No documents found in the collection.")


# Implementation for PgVectorDB
class PgVectorDB(VectorDatabase):
    def __init__(
        self,
        distance_function: str = "l2",
        collection_name: str = "default",
        host: str = None,
        port: int = None,
        db_name: str = None,
        user: str = None,
        password: str = None,
        conn_str: str = None,
    ):
        """
        Initializes the PgVectorDB with the given connection parameters.

        Args:
            distance_function (str, optional): The distance function to use for similarity search.
                Valid values are 'l2' (Euclidean distance) or 'cosine' (Cosine similarity). Defaults to 'l2'.
            collection_name (str): The name of the collection (table). Defaults to 'default'.
            host (str, optional): The host address of the database server. Defaults to None.
            port (int, optional): The port number of the database server. Defaults to None.
            db_name (str, optional): The name of the database. Defaults to None.
            user (str, optional): The username for database authentication. Defaults to None.
            password (str, optional): The password for database authentication. Defaults to None.
            conn_str (str, optional): A connection string in the format "postgresql://{user}:{password}@{host}:{port}/{db_name}". Defaults to None.
        """
        super().__init__(distance_function=distance_function)

        if conn_str is not None:
            self.conn_str = conn_str
        else:
            db_url = (
                f"{host}:{port}" if host and port else "localhost:5432"
            )  # Default to localhost:5432 if not provided
            self.conn_str = f"postgresql://{user}:{password}@{db_url}/{db_name}"

        self.collection_name = collection_name
        try:
            self.conn = psycopg.connect(self.conn_str, autocommit=True)
            self.conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            register_vector(self.conn)
            # Cria a tabela se não existir
            self.conn.execute(
                f"""CREATE TABLE IF NOT EXISTS {self.collection_name} (
                        id TEXT PRIMARY KEY,
                        embedding vector(1536),
                        metadata JSONB
                    )"""
            )
            # Cria o índice vetorial apropriado se não existir
            index_name = f"{self.collection_name}_embedding_idx"
            if self.distance_function == "cosine":
                op_class = "vector_cosine_ops"
            else: # Default to l2
                op_class = "vector_l2_ops"
            self.conn.execute(
                f"""CREATE INDEX IF NOT EXISTS {index_name}
                    ON {self.collection_name}
                    USING hnsw (embedding {op_class})"""
            )
        except psycopg.Error as e:
            print(f"Error connecting to PostgreSQL or creating table: {e}")
            raise

    def add_embeddings(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
    ):
        """
        Adds embeddings to the PgVectorDB table.

        Args:
            ids (List[str]): The IDs of the embeddings.
            embeddings (List[List[float]]): The embeddings to add.
            metadatas (List[Dict[str, Any]]): The metadata for the embeddings.
        """
        # Prepara os dados para inserção em lote
        data_to_insert = [
            (id, embedding, json.dumps(metadata))
            for id, embedding, metadata in zip(ids, embeddings, metadatas)
        ]

        if not data_to_insert:
            return # Não faz nada se não houver dados

        try:
            with self.conn.cursor() as cur:
                # Usa executemany para inserção/atualização em lote
                cur.executemany(
                    f"""INSERT INTO {self.collection_name} (id, embedding, metadata) VALUES (%s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding, metadata = EXCLUDED.metadata""",
                    data_to_insert
                )
        except psycopg.Error as e:
            print(f"Error adding embeddings in batch to PostgreSQL: {e}")
            raise

    def search_embeddings(
        self, embedding: List[float], n_results: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Searches for similar embeddings in the PgVectorDB table.

        Args:
            embedding (List[float]): The embedding to search for.
            n_results (int, optional): The number of results to return. Defaults to 10.

        Returns:
            List[Tuple[str, float]]: A list of tuples containing the ID and distance of the similar embeddings.
        """
        if self.distance_function == "cosine":
            operator = "<=>"
        elif self.distance_function == "l2":
            operator = "<->"
        else:
            raise ValueError(f"Invalid distance function: {self.distance_function}.")

        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    f"SELECT id, embedding {operator} %s::vector AS distance FROM {self.collection_name} ORDER BY distance LIMIT %s",
                    (embedding, n_results),
                )
                results = cur.fetchall()
                return [(result[0], result[1]) for result in results]
        except psycopg.Error as e:
            print(f"Error searching embeddings in PostgreSQL: {e}")
            return []

    def count(self, where: Optional[Dict[str, Any]] = None) -> int:
        """
        Counts the number of embeddings in the PgVectorDB table.

        Args:
            where (Optional[Dict[str, Any]], optional): A dictionary specifying the filter criteria. Defaults to None.

        Returns:
            int: The number of embeddings in the table.
        """
        try:
            with self.conn.cursor() as cur:
                query = f"SELECT COUNT(*) FROM {self.collection_name}"
                if where:
                    conditions = []
                    params = []
                    for key, value in where.items():
                        conditions.append(f"metadata->>'{key}' = %s")
                        params.append(str(value))
                    query += f' WHERE {" AND ".join(conditions)}'
                    cur.execute(query, params)
                else:
                    cur.execute(query)
                result = cur.fetchone()
                return result[0]
        except psycopg.Error as e:
            print(f"Error counting embeddings in PostgreSQL: {e}")
            return 0

    def get_version(self) -> str:
        """
        Gets the version of the PostgreSQL database server.
        Returns:
            str: The version of the PostgreSQL database server.
        """
        try:
            return str(self.conn.info.server_version)
        except psycopg.Error as e:
            print(f"Error getting PostgreSQL version: {e}")
            return ""

    def list_collections(self) -> List[str]:
        """
        Lists all tables in the PgVectorDB database.
        Returns:
            List[str]: A list of table names.
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
                )
                results = cur.fetchall()
                return [result[0] for result in results]
        except psycopg.Error as e:
            print(f"Error listing collections in PostgreSQL: {e}")
            return []

    def reset_collection(self):
        """
        Resets the current collection (table) by erasing all documents.
        """
        try:
            with self.conn.cursor() as cur:
                # Usa TRUNCATE para limpeza rápida, assumindo que a tabela e índice já existem (fixture de módulo)
                cur.execute(f"TRUNCATE TABLE {self.collection_name}")
                print(f"Truncated table '{self.collection_name}'.")
        except psycopg.Error as e:
            print(f"Error truncating collection in PostgreSQL: {e}")
            # Considera se deve relançar a exceção dependendo da criticidade
            # raise # Descomente se a falha no truncate deve parar os testes


class PineconeDB(VectorDatabase):
    def __init__(
        self,
        api_key: Optional[str] = None,
        distance_function: str = "l2",
        collection_name: str = "default",
        region: str = "us-east-1",
        vector_dimension: int = 1536,
    ):
        """
        Inicializa uma instância do PineconeDB.

        Args:
            api_key (Optional[str]): Chave de API do Pinecone. Se não fornecida, será obtida da variável de ambiente PINECONE_API_KEY.
            distance_function (str): Função de distância a ser usada ('l2' ou 'cosine'). Padrão: 'l2'.
            collection_name (str): Nome da coleção/índice a ser usado. Padrão: "default".
            region (str): Regão AWS onde o índice será criado. Padrão: 'us-east-1'.
            vector_dimension (int): Dimensão dos vetores a serem armazenados. Deve ser maior que 0. Padrão: 1536.

        Raises:
            ValueError: Se a API key não for fornecida e a variável de ambiente PINECONE_API_KEY não estiver configurada.
            ValueError: Se vector_dimension for menor ou igual a 0.
        """
        super().__init__(distance_function)
        self.api_key = api_key or os.environ.get("PINECONE_API_KEY")
        self.collection_name = collection_name or "default"
        self.region = region or "us-east-1"

        if not self.api_key or not self.collection_name:
            raise ValueError(
                "API key não fornecida e variável de ambiente PINECONE_API_KEY não configurada."
            )

        if vector_dimension <= 0:
            raise ValueError("vector_dimension deve ser maior que 0")
        self.vector_dimension = vector_dimension
        self.namespace = collection_name

        self.client = Pinecone(api_key=self.api_key)

        # Verifica se o índice já existe
        existing_indexes = self.client.list_indexes()
        index_names = [index["name"] for index in existing_indexes]

        if self.collection_name not in index_names:
            # Cria o índice com a função de distância especificada
            metric = "euclidean" if distance_function == "l2" else "cosine"
            try:
                self.client.create_index(
                    name=self.collection_name,
                    dimension=self.vector_dimension,
                    metric=metric,
                    deletion_protection="disabled",
                    spec=ServerlessSpec(region=self.region, cloud="aws"),
                )
            except Exception as e:
                if "already exists" not in str(e):
                    raise

        self.index = self.client.Index(self.collection_name)

    def add_embeddings(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
    ):
        """
        Adiciona embeddings ao banco de dados.

        Args:
            ids (List[str]): Lista de IDs únicos para cada embedding.
            embeddings (List[List[float]]): Lista de vetores de embeddings.
            metadatas (List[Dict[str, Any]]): Lista de dicionários contendo metadados associados a cada embedding.
        """
        vectors = [
            {"id": id, "values": embedding, "metadata": metadata}
            for id, embedding, metadata in zip(ids, embeddings, metadatas)
        ]

        self.index.upsert(vectors=vectors, namespace=self.namespace)

    def search_embeddings(
        self, embedding: List[float], n_results: int = 10, similarity_by: str = None
    ) -> List[Tuple[str, float]]:
        """
        Busca embeddings similares ao vetor fornecido.

        Args:
            embedding (List[float]): Vetor de embedding para busca de similaridade.
            n_results (int): Número máximo de resultados a retornar. Padrão: 10.
            similarity_by (string): Função de distância usada para calcular a similaridade. Ignorada.

        Returns:
            List[Tuple[str, float]]: Lista de tuplas contendo o ID do embedding e o score de similaridade,
                ordenados por similaridade decrescente.
        """
        try:
            query_response = self.index.query(
                vector=embedding,
                top_k=n_results,
                namespace=self.namespace,
                include_metadata=True,
            )
            return [(match.id, match.score) for match in query_response.matches]
        except Exception as e:
            if "Namespace not found" in str(e):
                return []
            raise

    def get_version(self) -> str:
        """
        Obtém a versão do índice no Pinecone.

        Returns:
            str: Versão do índice ou 'unknown' se não for possível determinar.
        """
        index_description = self.client.describe_index(self.collection_name)
        return index_description.get("version", "unknown")

    def count(self, where: Optional[Dict[str, Any]] = None) -> int:
        """
        Conta o número de vetores no namespace, opcionalmente filtrando por metadados.

        Args:
            where (Optional[Dict[str, Any]]): Filtro de metadados no formato Pinecone.
                Exemplo: {"genre": {"$eq": "documentary"}}

        Returns:
            int: Número de vetores que correspondem ao filtro
        """
        stats = self.index.describe_index_stats()
        if self.namespace in stats.namespaces:
            return stats.namespaces[self.namespace].vector_count
        return 0

    def list_collections(self) -> List[str]:
        """
        Lista todos os índices disponíveis no Pinecone.

        Returns:
            List[str]: Lista de nomes dos índices.
        """
        # No Pinecone, collections são chamadas de indexes.
        indexes = self.client.list_indexes()
        return [index["name"] for index in indexes]

    def reset_collection(self):
        """Remove todos os vetores do namespace atual."""
        try:
            # First check if namespace exists
            stats = self.index.describe_index_stats()
            if self.namespace in stats.namespaces:
                self.index.delete(delete_all=True, namespace=self.namespace)
        except Exception as e:
            if "not found" not in str(e).lower():
                raise


# Main class to manage embeddings
class EmbeddingManager:
    def __init__(self, llm_service: LLMServices, vector_database: VectorDatabase):
        """
        Initializes the EmbeddingManager with the given LLM service and vector database.

        Args:
            llm_service (LLMServices): The LLM service to use for generating embeddings.
            vector_database (VectorDatabase): The vector database to use for storing embeddings.
        """
        self.llm_service = llm_service
        self.vector_database = vector_database

    def add_document(
        self, text: str, id: str = None, meta: Optional[Dict[str, Any]] = None
    ):
        """
        Adds a single document to the database.

        Args:
            text (str): The text of the document.
            id (str, optional): The ID of the document. If None, it will be generated from the text. Defaults to None.
            meta (Optional[Dict[str, Any]], optional): The metadata for the document. Defaults to None.
        """
        document_id = id if id is not None else self.generate_id_from_text(text)
        embedding = self.llm_service.generate_embedding(text)
        if embedding:
            self.vector_database.add_embeddings(
                [document_id], [embedding], [meta or {}]
            )

    def add_documents(
        self,
        documents: List[Tuple[str, str, Optional[Dict[str, Any]]]],
        parallel: bool = True,
    ):
        """
        Adds multiple documents to the database.

        Args:
            documents (List[Tuple[str, str, Optional[Dict[str, Any]]]]): A list of tuples, where each tuple contains:
                - text: The text of the document.
                - id: Optional id of the document. If None, it will be generated from the text.
                - meta: Optional metadata for the document.
            parallel (bool, optional): Whether to process the documents in parallel. Defaults to True.
        """
        params = [(text, id, meta) for text, id, meta in documents]
        processor = Process(process=self._process_document, parallelize=parallel)
        results = processor.run(params=params)

        ids = [result[0] for result in results if result]
        embeddings = [result[1] for result in results if result]
        metadatas = [result[2] for result in results if result]

        if ids and embeddings and metadatas:
            self.vector_database.add_embeddings(ids, embeddings, metadatas)

    def _process_document(
        self, text: str, id: str = None, meta: Optional[Dict[str, Any]] = None
    ) -> Optional[Tuple[str, List[float], Dict[str, Any]]]:
        """
        Processes a single document, generating embedding and preparing data for database insertion.

        Args:
            text (str): The text of the document.
            id (str, optional): The ID of the document. If None, it will be generated from the text. Defaults to None.
            meta (Optional[Dict[str, Any]], optional): The metadata for the document. Defaults to None.

        Returns:
            Optional[Tuple[str, List[float], Dict[str, Any]]]: A tuple containing the document ID, embedding, and metadata, or None if the embedding could not be generated.
        """
        document_id = id if id is not None else self.generate_id_from_text(text)
        embedding = self.llm_service.generate_embedding(text)
        if embedding:
            return document_id, embedding, meta or {}
        else:
            return None

    def generate_id_from_text(self, text: str) -> str:
        """
        Generates a unique ID based on the hash of the text.

        Args:
            text (str): The text to generate the ID from.

        Returns:
            str: The generated ID.
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def search_documents(
        self, text: str, n_results: int = 10, similarity_by: str = "cosine"
    ) -> List[Tuple[str, float]]:
        """
        Searches for similar documents in the database based on the given text.

        Args:
            text (str): The text to search for.
            n_results (int, optional): The number of results to return. Defaults to 10.
            similarity_by (str, optional): The similarity metric to use for searching. Defaults to 'cosine'.

        Returns:
            List[Tuple[str, float]]: A list of tuples containing the ID and distance of the similar documents.
        """
        embedding = self.llm_service.generate_embedding(text)
        if embedding:
            return self.vector_database.search_embeddings(
                embedding, n_results, similarity_by
            )
        return []
