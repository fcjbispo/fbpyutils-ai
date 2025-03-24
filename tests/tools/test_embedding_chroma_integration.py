import os
import pytest
from typing import List, Dict, Any, Tuple

from mymoney.core.services.chroma import ChromaDB

MM_CHROMADB_HOST = os.getenv("MM_CHROMADB_HOST")
MM_CHROMADB_PORT = os.getenv("MM_CHROMADB_PORT")
COLLECTION_NAME = "mymoney_chroma_integration_tests"

pytestmark = pytest.mark.integration

@pytest.fixture(scope="function")
def chroma_db():
    """Fixture para criar e limpar a collection de testes."""
    if not (MM_CHROMADB_HOST and MM_CHROMADB_PORT):
        # Modo local com persistência temporária
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        db = ChromaDB(
            persist_directory=temp_dir,
            collection_name=COLLECTION_NAME
        )
        db.reset_collection()
        yield db
        db.reset_collection()
        shutil.rmtree(temp_dir)
    else:
        # Modo remoto usando servidor ChromaDB
        db = ChromaDB(
            host=MM_CHROMADB_HOST,
            port=int(MM_CHROMADB_PORT),
            collection_name=COLLECTION_NAME
        )
        db.reset_collection()
        yield db
        db.reset_collection()

def test_add_embeddings(chroma_db: ChromaDB):
    """Testa a adição de embeddings ao banco de dados."""
    ids = ["doc1", "doc2"]
    embeddings = [[0.1] * 1536, [0.9] * 1536]
    metadatas = [{"source": "source1"}, {"source": "source2"}]
    chroma_db.add_embeddings(ids, embeddings, metadatas)
    assert chroma_db.count() == 2

def test_search_embeddings_l2(chroma_db: ChromaDB):
    """Testa a busca de embeddings similares usando distância L2."""
    chroma_db.reset_collection()
    ids = ["doc1", "doc2", "doc3"]
    embeddings = [[0.1] * 1536, [0.9] * 1536, [0.5] * 1536]
    metadatas = [{"source": "source1"}, {"source": "source2"}, {"source": "source3"}]
    chroma_db.add_embeddings(ids, embeddings, metadatas)

    query_embedding = [0.15] * 1536
    results = chroma_db.search_embeddings(
        query_embedding, 
        n_results=2
    )
    assert len(results) == 2
    assert results[0][0] == "doc1"  # doc1 deve ser o mais próximo usando L2

def test_search_embeddings_cosine(chroma_db: ChromaDB):
    """Testa a busca de embeddings similares usando distância de cosseno."""
    # Cria nova instância com distância de cosseno
    if not (MM_CHROMADB_HOST and MM_CHROMADB_PORT):
        # Modo local
        cosine_db = ChromaDB(
            persist_directory=chroma_db.client.path,
            collection_name=f"{COLLECTION_NAME}_cosine",
            distance_function='cosine'
        )
    else:
        # Modo remoto
        cosine_db = ChromaDB(
            host=MM_CHROMADB_HOST,
            port=int(MM_CHROMADB_PORT),
            collection_name=f"{COLLECTION_NAME}_cosine",
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
    results = cosine_db.search_embeddings(
        query_embedding, 
        n_results=2
    )
    assert len(results) == 2
    # doc1 deve ser o mais próximo usando cosine pois tem a mesma direção
    # mesmo tendo magnitude menor
    assert results[0][0] == "doc1"

def test_count(chroma_db: ChromaDB):
    """Testa a contagem de embeddings no banco de dados."""
    chroma_db.reset_collection()
    ids = ["doc1", "doc2", "doc3"]
    embeddings = [[0.1] * 1536, [0.9] * 1536, [0.5] * 1536]
    metadatas = [{"source": "source1"}, {"source": "source2"}, {"source": "source3"}]
    chroma_db.add_embeddings(ids, embeddings, metadatas)
    assert chroma_db.count() == 3
    assert chroma_db.count(where={"source": "source1"}) == 1

def test_get_version(chroma_db: ChromaDB):
    """Testa a obtenção da versão do ChromaDB."""
    version = chroma_db.get_version()
    assert isinstance(version, str)  # A versão é retornada como uma string

def test_reset_collection(chroma_db: ChromaDB):
    """Testa o reset da collection."""
    ids = ["doc1", "doc2"]
    embeddings = [[0.1] * 1536, [0.9] * 1536]
    metadatas = [{"source": "source1"}, {"source": "source2"}]
    chroma_db.add_embeddings(ids, embeddings, metadatas)
    assert chroma_db.count() == 2
    chroma_db.reset_collection()
    assert chroma_db.count() == 0