# -*- coding: utf-8 -*-
"""Testes unitários para as ferramentas de busca."""
import os
import pytest
from fbpyutils_ai.tools.search import SearXNGTool
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def searxng_tool():
    """Fixture para a ferramenta SearXNGTool."""
    # Usar variável de ambiente TOOL_SEARCH_API_BASE_URL para testes, usar HTTP
    # base_url = "https://searx.bar/search" # Comentado para usar variável de ambiente
    base_url = os.getenv("TOOL_SEARCH_API_BASE_URL").replace("https://", "http://") # Usar HTTP
    if not base_url:
        pytest.skip("Variável de ambiente TOOL_SEARCH_API_BASE_URL não definida")
    return SearXNGTool(base_url=base_url)

def test_searxng_tool_initialization(searxng_tool):
    """Testa a inicialização da SearXNGTool."""
    assert searxng_tool is not None
    assert searxng_tool.base_url is not None

def test_searxng_tool_search_success(searxng_tool):
    """Testa uma busca bem-sucedida no SearXNG."""
    results = searxng_tool.search("OpenAI", params={"category_general": "1"})
    assert isinstance(results, list)
    assert len(results) > 0  # Adicionado: Valida que a lista não está vazia


def test_searxng_tool_search_error(searxng_tool):
    """Testa o tratamento de erro na busca do SearXNG."""
    # Forçar um erro na requisição (URL inválida)
    invalid_tool = SearXNGTool(base_url="https://invalid-url")
    results = invalid_tool.search("OpenAI", params={"category_general": "1"})
    assert isinstance(results, list)
    assert not results
