import os
import pytest
from typing import List, Dict, Any, Tuple

from fbpyutils_ai.tools.embedding import ChromaDB

FBPY_CHROMADB_HOST = os.getenv("FBPY_CHROMADB_HOST")
FBPY_CHROMADB_PORT = os.getenv("FBPY_CHROMADB_PORT")
COLLECTION_NAME = "mymoney_chroma_integration_tests"

pytestmark = pytest.mark.integration

@pytest.fixture(scope="function")
def chroma_db_fixture():
    """Fixture para criar e limpar a collection de testes. Retorna (ChromaDB, temp_dir|None)."""
    if not (FBPY_CHROMADB_HOST and FBPY_CHROMADB_PORT):
        # Modo local com persistência temporária
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        db = ChromaDB(
            persist_directory=temp_dir,
            collection_name=COLLECTION_NAME
        )
        db.reset_collection()
        yield db, temp_dir
        db.reset_collection()
        del db  # Tenta liberar recursos antes de remover o diretório
        # Adiciona uma pequena pausa e tentativas para shutil.rmtree em caso de erro de permissão
        import time
        attempts = 3
        for i in range(attempts):
            try:
                shutil.rmtree(temp_dir)
                break
            except PermissionError as e:
                if i < attempts - 1:
                    time.sleep(0.5) # Espera um pouco antes de tentar novamente
                else:
                    print(f"Erro ao remover diretório temporário após {attempts} tentativas: {e}")
                    # Opcional: raise e # Re-lança a exceção se todas as tentativas falharem
    else:
        # Modo remoto usando servidor ChromaDB
        db = ChromaDB(
            host=FBPY_CHROMADB_HOST,
            port=int(FBPY_CHROMADB_PORT),
            collection_name=COLLECTION_NAME
        )
        db.reset_collection()
        yield db, None # Nenhum temp_dir no modo remoto
        db.reset_collection()
        del db # Tenta liberar recursos

def test_add_embeddings(chroma_db_fixture: Tuple[ChromaDB, str | None]):
    """Testa a adição de embeddings ao banco de dados."""
    chroma_db, _ = chroma_db_fixture
    ids = ["doc1", "doc2"]
    embeddings = [[0.1] * 1536, [0.9] * 1536]
    metadatas = [{"source": "source1"}, {"source": "source2"}]
    chroma_db.add_embeddings(ids, embeddings, metadatas)
    assert chroma_db.count() == 2

def test_search_embeddings_l2(chroma_db_fixture: Tuple[ChromaDB, str | None]):
    """Testa a busca de embeddings similares usando distância L2."""
    chroma_db, _ = chroma_db_fixture
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

def test_search_embeddings_cosine(chroma_db_fixture: Tuple[ChromaDB, str | None]):
    """Testa a busca de embeddings similares usando distância de cosseno."""
    chroma_db, temp_dir = chroma_db_fixture
    # Cria nova instância com distância de cosseno
    if not (FBPY_CHROMADB_HOST and FBPY_CHROMADB_PORT):
        # Modo local
        # Verifica se estamos no modo local (temp_dir não é None)
        if temp_dir:
            cosine_db = ChromaDB(
                persist_directory=temp_dir, # Usa o temp_dir da fixture
                collection_name=f"{COLLECTION_NAME}_cosine",
                distance_function='cosine'
            )
        else:
            # Modo remoto (não deveria chegar aqui se FBPY_CHROMADB_HOST/PORT não estão definidos,
            # mas incluído por segurança)
            pytest.skip("Teste de cosseno local requer modo de persistência local.")
    else:
        # Modo remoto
        cosine_db = ChromaDB(
            host=FBPY_CHROMADB_HOST,
            port=int(FBPY_CHROMADB_PORT),
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

def test_count(chroma_db_fixture: Tuple[ChromaDB, str | None]):
    """Testa a contagem de embeddings no banco de dados."""
    chroma_db, _ = chroma_db_fixture
    chroma_db.reset_collection()
    ids = ["doc1", "doc2", "doc3"]
    embeddings = [[0.1] * 1536, [0.9] * 1536, [0.5] * 1536]
    metadatas = [{"source": "source1"}, {"source": "source2"}, {"source": "source3"}]
    chroma_db.add_embeddings(ids, embeddings, metadatas)
    assert chroma_db.count() == 3
    assert chroma_db.count(where={"source": "source1"}) == 1

def test_get_version(chroma_db_fixture: Tuple[ChromaDB, str | None]):
    """Testa a obtenção da versão do ChromaDB."""
    chroma_db, _ = chroma_db_fixture
    version = chroma_db.get_version()
    assert isinstance(version, str)  # A versão é retornada como uma string

def test_reset_collection(chroma_db_fixture: Tuple[ChromaDB, str | None]):
    """Testa o reset da collection."""
    chroma_db, _ = chroma_db_fixture
    ids = ["doc1", "doc2"]
    embeddings = [[0.1] * 1536, [0.9] * 1536]
    metadatas = [{"source": "source1"}, {"source": "source2"}]
    chroma_db.add_embeddings(ids, embeddings, metadatas)
    assert chroma_db.count() == 2
    chroma_db.reset_collection()
    assert chroma_db.count() == 0
