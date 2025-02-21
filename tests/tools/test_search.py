import os
import pytest
from fbpyutils_ai.tools.search import SearXNGTool
from dotenv import load_dotenv

load_dotenv() # Carrega as variáveis de ambiente do .env

@pytest.fixture
def searxng_tool():
    """Fixture para a ferramenta SearXNGTool."""
    base_url = os.getenv("SEARXNG_API_BASE")
    if not base_url:
        pytest.skip("Variável de ambiente TOOL_SEARCH_API_BASE_URL não definida")
    return SearXNGTool(base_url=base_url)

def test_searxng_tool_initialization(searxng_tool):
    """Testa a inicialização da SearXNGTool."""
    assert searxng_tool is not None
    assert searxng_tool.base_url is not None

@pytest.mark.parametrize("category", [
    ['general'],
    ['images'],
    ['news'],
    ['general', 'images']
])
def test_searxng_tool_search_success_categories(searxng_tool, category):
    """Testa a busca bem-sucedida no SearXNG com diferentes categorias."""
    results = searxng_tool.search("OpenAI", categories=category)
    assert isinstance(results, list)
    assert len(results) > 0

@pytest.mark.parametrize("safesearch", [
    SearXNGTool.SAFESEARCH_NONE,
    SearXNGTool.SAFESEARCH_MODERATE,
    SearXNGTool.SAFESEARCH_STRICT,
])
def test_searxng_tool_search_success_safesearch(searxng_tool, safesearch):
    """Testa a busca bem-sucedida no SearXNG com diferentes níveis de safesearch."""
    results = searxng_tool.search("OpenAI", safesearch=safesearch)
    assert isinstance(results, list)
    assert len(results) > 0

def test_searxng_tool_search_error(searxng_tool):
    """Testa o tratamento de erro na busca do SearXNG."""
    # Forçar um erro na requisição (URL inválida)
    invalid_tool = SearXNGTool(base_url="https://invalid-url")
    results = invalid_tool.search("OpenAI")
    assert isinstance(results, list)
    assert not results
