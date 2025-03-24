import os
import pytest
from typing import List, Dict, Any, Tuple

from mymoney.core.services.pinecone import PineconeDB

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
COLLECTION_NAME = "mymoney-pinecone-integration-tests"

pytestmark = pytest.mark.integration

@pytest.fixture(scope="function")
def pinecone_db():
    """Fixture para criar e limpar a collection de testes."""
    if PINECONE_API_KEY is None:
        raise ValueError("A variável de ambiente PINECONE_API_KEY deve estar definida.")
    db = PineconeDB(collection_name=COLLECTION_NAME, api_key=PINECONE_API_KEY)
    db.reset_collection()
    yield db
    db.reset_collection()

def test_add_embeddings(pinecone_db: PineconeDB):
    """Testa a adição de embeddings ao banco de dados."""
    ids = ["doc1", "doc2"]
    embeddings = [
        [0.1] * pinecone_db.vector_dimension, 
        [0.9] * pinecone_db.vector_dimension
    ]
    metadatas = [{"source": "source1"}, {"source": "source2"}]
    pinecone_db.add_embeddings(ids, embeddings, metadatas)
    assert pinecone_db.count() == 2

def test_search_embeddings_l2(pinecone_db: PineconeDB):
    """Testa a busca de embeddings similares usando distância L2."""
    pinecone_db.reset_collection()
    ids = ["doc1", "doc2", "doc3"]
    embeddings = [
        [0.1] * pinecone_db.vector_dimension, 
        [0.9] * pinecone_db.vector_dimension, 
        [0.5] * pinecone_db.vector_dimension
    ]
    metadatas = [{"source": "source1"}, {"source": "source2"}, {"source": "source3"}]
    pinecone_db.add_embeddings(ids, embeddings, metadatas)

    query_embedding = [0.15] * pinecone_db.vector_dimension
    results: List[Tuple[str, float]] = pinecone_db.search_embeddings(
        query_embedding,
        n_results=2
    )
    assert len(results) == 2
    assert results[0][0] == "doc1"  # doc1 deve ser o mais próximo usando L2
    assert isinstance(results[0][1], float)  # Verifica se o score é um float

def test_search_embeddings_cosine(pinecone_db: PineconeDB):
    """Testa a busca de embeddings similares usando distância de cosseno."""
    # Cria nova instância com distância de cosseno
    cosine_db = PineconeDB(
        collection_name=COLLECTION_NAME,
        distance_function='cosine'
    )
    cosine_db.reset_collection()

    # Criando vetores com diferentes direções para testar similaridade do cosseno
    ids = ["doc1", "doc2", "doc3"]
    embeddings = [
        [0.1] + [0.0] * (cosine_db.vector_dimension - 1),  # doc1: mesma direção do query, magnitude pequena
        [0.0] + [0.9] * (cosine_db.vector_dimension - 1),  # doc2: direção diferente
        [0.1] + [0.5] * (cosine_db.vector_dimension - 1),  # doc3: direção intermediária
    ]
    metadatas = [{"source": "source1"}, {"source": "source2"}, {"source": "source3"}]
    cosine_db.add_embeddings(ids, embeddings, metadatas)

    # Query com mesma direção que doc1, mas magnitude diferente
    query_embedding = [1.0] + [0.0] * (cosine_db.vector_dimension - 1)
    results: List[Tuple[str, float]] = cosine_db.search_embeddings(
        query_embedding,
        n_results=2
    )
    assert len(results) == 2
    assert results[0][0] == "doc1"  # doc1 deve ser o mais próximo usando cosine pois tem a mesma direção

def test_count(pinecone_db: PineconeDB):
    """Testa a contagem de embeddings no banco de dados."""
    pinecone_db.reset_collection()
    ids = ["doc1", "doc2", "doc3"]
    embeddings = [
        [0.1] * pinecone_db.vector_dimension, 
        [0.9] * pinecone_db.vector_dimension, 
        [0.5] * pinecone_db.vector_dimension
    ]
    metadatas = [{"source": "source1"}, {"source": "source2"}, {"source": "source3"}]
    pinecone_db.add_embeddings(ids, embeddings, metadatas)
    
    # Testa contagem total
    assert pinecone_db.count() == 3
    
    # Testa contagem com filtro
    assert pinecone_db.count(where={"source": {"$eq": "source1"}}) == 1
    assert pinecone_db.count(where={"source": {"$in": ["source1", "source2"]}}) == 2

def test_list_collections(pinecone_db: PineconeDB):
    """Testa a listagem de collections."""
    collections = pinecone_db.list_collections()
    assert isinstance(collections, list)
    assert all(isinstance(c, str) for c in collections)  # Verifica se todos os itens são strings
    assert COLLECTION_NAME in collections  # Verifica se a collection de teste está na lista

def test_vector_dimension_validation():
    """Testa a validação da dimensão do vetor."""
    with pytest.raises(ValueError, match="vector_dimension deve ser maior que 0"):
        PineconeDB(vector_dimension=0)
    with pytest.raises(ValueError, match="vector_dimension deve ser maior que 0"):
        PineconeDB(vector_dimension=-100)

def test_custom_vector_dimension():
    """Testa a criação de um índice com dimensão personalizada."""
    custom_dim = 768
    db = PineconeDB(vector_dimension=custom_dim)
    assert db.vector_dimension == custom_dim
    
    # Testa adição de vetores com a dimensão correta
    ids = ["doc1", "doc2"]
    embeddings = [
        [0.1] * custom_dim,
        [0.9] * custom_dim
    ]
    metadatas = [{"source": "source1"}, {"source": "source2"}]
    db.add_embeddings(ids, embeddings, metadatas)
    assert db.count() == 2

def test_reset_collection(pinecone_db: PineconeDB):
    """Testa o reset da collection."""
    ids = ["doc1", "doc2"]
    embeddings = [
        [0.1] * pinecone_db.vector_dimension, 
        [0.9] * pinecone_db.vector_dimension
    ]
    metadatas = [{"source": "source1"}, {"source": "source2"}]
    pinecone_db.add_embeddings(ids, embeddings, metadatas)
    assert pinecone_db.count() == 2
    pinecone_db.reset_collection()
    assert pinecone_db.count() == 0
