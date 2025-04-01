import os
import pytest
from typing import List, Dict, Any, Tuple

from fbpyutils_ai.tools.embedding import PgVectorDB

FBPY_VECTORDB_URL = os.getenv("FBPY_VECTORDB_URL")
COLLECTION_NAME = "mymoney_pg_integration_tests"

pytestmark = pytest.mark.integration

@pytest.fixture(scope="module") # Alterado para module
def pg_vector_db():
    """Fixture para criar e limpar a collection de testes."""
    if not FBPY_VECTORDB_URL:
        raise ValueError("A variável de ambiente FBPY_VECTORDB_URL não está definida.")
    db = PgVectorDB(conn_str=FBPY_VECTORDB_URL, collection_name=COLLECTION_NAME)
    db.reset_collection()
    yield db
    db.reset_collection()

def test_add_embeddings(pg_vector_db: PgVectorDB):
    """Testa a adição de embeddings ao banco de dados."""
    ids = ["doc1", "doc2"]
    embeddings = [[0.1] * 1536, [0.9] * 1536]
    metadatas = [{"source": "source1"}, {"source": "source2"}]
    pg_vector_db.add_embeddings(ids, embeddings, metadatas)
    assert pg_vector_db.count() == 2

def test_search_embeddings_l2(pg_vector_db: PgVectorDB):
    """Testa a busca de embeddings similares usando distância L2."""
    pg_vector_db.reset_collection()
    ids = ["doc1", "doc2", "doc3"]
    embeddings = [[0.1] * 1536, [0.9] * 1536, [0.5] * 1536]
    metadatas = [{"source": "source1"}, {"source": "source2"}, {"source": "source3"}]
    pg_vector_db.add_embeddings(ids, embeddings, metadatas)

    query_embedding = [0.15] * 1536
    results: List[Tuple[str, float]] = pg_vector_db.search_embeddings(
        query_embedding,
        n_results=2
    )
    assert len(results) == 2
    assert results[0][0] == "doc1"  # doc1 deve ser o mais próximo usando L2

def test_search_embeddings_cosine(pg_vector_db: PgVectorDB):
    """Testa a busca de embeddings similares usando distância de cosseno."""
    # Cria nova instância com distância de cosseno
    cosine_db = PgVectorDB(
        conn_str=FBPY_VECTORDB_URL,
        collection_name=COLLECTION_NAME,
        distance_function='cosine'
    )
    cosine_db.reset_collection()

    # Criando vetores com diferentes direções para testar similaridade do cosseno
    # doc1: vetor com valores pequenos mas mesma direção do query
    # doc2: vetor com valores grandes mas direção diferente
    # doc3: vetor com valores médios e direção intermediária
    ids = ["doc1", "doc2", "doc3"]
    embeddings = [
        [0.1] + [0.0] * 1535,  # doc1: mesma direção do query, magnitude pequena
        [0.0] + [0.9] * 1535,  # doc2: direção diferente
        [0.1] + [0.5] * 1535,  # doc3: direção intermediária
    ]
    metadatas = [{"source": "source1"}, {"source": "source2"}, {"source": "source3"}]
    cosine_db.add_embeddings(ids, embeddings, metadatas)

    # Query com mesma direção que doc1, mas magnitude diferente
    query_embedding = [1.0] + [0.0] * 1535
    results: List[Tuple[str, float]] = cosine_db.search_embeddings(
        query_embedding,
        n_results=2
    )
    assert len(results) == 2
    # doc1 deve ser o mais próximo usando cosine pois tem a mesma direção
    # mesmo tendo magnitude menor
    assert results[0][0] == "doc1"

def test_count(pg_vector_db: PgVectorDB):
    """Testa a contagem de embeddings no banco de dados."""
    pg_vector_db.reset_collection()
    ids = ["doc1", "doc2", "doc3"]
    embeddings = [[0.1] * 1536, [0.9] * 1536, [0.5] * 1536]
    metadatas = [{"source": "source1"}, {"source": "source2"}, {"source": "source3"}]
    pg_vector_db.add_embeddings(ids, embeddings, metadatas)
    assert pg_vector_db.count() == 3
    assert pg_vector_db.count(where={"source": "source1"}) == 1

def test_get_version(pg_vector_db: PgVectorDB):
    """Testa a obtenção da versão do PostgreSQL."""
    version = pg_vector_db.get_version()
    assert isinstance(version, str)  # A versão é retornada como uma string

def test_reset_collection(pg_vector_db: PgVectorDB):
    """Testa o reset da collection."""
    pg_vector_db.reset_collection() # Garante estado limpo no início do teste
    ids = ["doc1", "doc2"]
    embeddings = [[0.1] * 1536, [0.9] * 1536]
    metadatas = [{"source": "source1"}, {"source": "source2"}]
    pg_vector_db.add_embeddings(ids, embeddings, metadatas)
    assert pg_vector_db.count() == 2
    pg_vector_db.reset_collection()
    assert pg_vector_db.count() == 0
