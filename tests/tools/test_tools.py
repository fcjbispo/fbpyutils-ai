import os
import pytest
import pandas as pd
import httpx
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Importa as classes que serão testadas.
# Ajuste o caminho conforme a estrutura do seu projeto.
from fbpyutils_ai.tools.search import SearXNGUtils, SearXNGTool


def test_simplify_results():
    """Testa se o método simplify_results simplifica corretamente os resultados."""
    raw_results = [
        {
            "url": "https://example.com",
            "title": "Example",
            "content": "Example content",
            "extra": "info"
        },
        {
            "url": "https://example.org",
            "title": "Example Org",
            "content": "Content here",
            "extra": "data"
        }
    ]
    simplified = SearXNGUtils.simplify_results(raw_results)
    assert isinstance(simplified, list)
    assert len(simplified) == len(raw_results)
    for result in simplified:
        # Verifica se as chaves principais estão presentes
        assert "url" in result
        assert "title" in result
        assert "content" in result
        # A chave 'other_info' deve conter os demais dados (neste caso, 'extra')
        assert "other_info" in result
        assert "extra" in result["other_info"]


def test_convert_to_dataframe():
    """Testa se a conversão dos resultados para DataFrame funciona corretamente."""
    raw_results = [
        {
            "url": "https://example.com",
            "title": "Example",
            "content": "Example content",
            "extra": "info"
        },
        {
            "url": "https://example.org",
            "title": "Example Org",
            "content": "Content here",
            "extra": "data"
        }
    ]
    df = SearXNGUtils.convert_to_dataframe(raw_results)
    assert isinstance(df, pd.DataFrame)
    # O DataFrame deve ter as colunas definidas
    for col in ["url", "title", "content", "other_info"]:
        assert col in df.columns
    # O número de linhas deve corresponder ao número de resultados
    assert len(df) == len(raw_results)


@pytest.fixture
def searxng_tool():
    """
    Fixture que instancia SearXNGTool utilizando a variável de ambiente FBPY_SEARXNG_BASE_URL.
    Caso a variável não esteja definida, o teste é ignorado.
    """
    base_url = os.getenv("FBPY_SEARXNG_BASE_URL")
    if not base_url:
        pytest.skip("FBPY_SEARXNG_BASE_URL não está definido no arquivo .env")
    return SearXNGTool(base_url=base_url)


def test_sync_search(searxng_tool, caplog):
    """
    Testa a busca síncrona.
    Executa uma busca (por exemplo, com o termo "python") e verifica se
    o retorno é uma lista e se os resultados possuem as chaves esperadas.
    """
    try:
        results = searxng_tool.search("python", language="en", safesearch=SearXNGTool.SAFESEARCH_NONE)
    except httpx.HTTPError as e:
        pytest.skip(f"Erro HTTP durante a busca síncrona: {e}")
    assert isinstance(results, list)
    # Caso haja resultados, verifica se o primeiro possui as chaves mínimas
    if results:
        first = results[0]
        assert "url" in first
        assert "title" in first
    # Verifica se os logs informam a conclusão da busca
    assert "Busca síncrona no SearXNG" in caplog.text


@pytest.mark.asyncio
async def test_async_search(searxng_tool, caplog):
    """
    Testa a busca assíncrona.
    Executa uma busca (por exemplo, com o termo "python") e verifica se
    o retorno é uma lista e se os resultados possuem as chaves esperadas.
    """
    try:
        results = await searxng_tool.async_search("python", language="en", safesearch=SearXNGTool.SAFESEARCH_NONE)
    except httpx.HTTPError as e:
        pytest.skip(f"Erro HTTP durante a busca assíncrona: {e}")
    assert isinstance(results, list)
    if results:
        first = results[0]
        assert "url" in first
        assert "title" in first
    assert "Busca assíncrona no SearXNG" in caplog.text
