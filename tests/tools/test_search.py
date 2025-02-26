import os
import httpx
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from fbpyutils_ai.tools.search import SearXNGTool


@pytest.fixture
def searxng_tool():
    """Fixture para a ferramenta SearXNGTool."""
    base_url = os.getenv("FBPY_SEARXNG_BASE_URL")
    if not base_url:
        pytest.skip("Variável de ambiente FBPY_SEARXNG_BASE_URL não definida")
    return SearXNGTool(base_url=base_url)


@pytest.fixture
def mock_http_client():
    """Fixture para mockar o HTTPClient."""
    with patch("fbpyutils_ai.tools.search.HTTPClient") as MockHTTPClient:
        mock_client_instance = MockHTTPClient.return_value

        sync_response_content = {
            "results": [
                {
                    "title": "Test Title",
                    "url": "https://testurl.com",
                    "content": "Test Content",
                    "publishedDate": "2024-11-29T00:00:00",
                    "score": 7.5,
                }
            ]
        }
        async_response_content = {
            "results": [
                {
                    "title": "Async Test Title",
                    "url": "https://test-async-url.com",
                    "content": "Async Test Content",
                    "publishedDate": "2024-11-29T00:00:00",
                    "score": 7.5,
                }
            ]
        }

        mock_client_instance.sync_request.return_value = sync_response_content

        async_future = asyncio.Future()
        async_future.set_result(async_response_content)
        mock_client_instance.async_request.return_value = async_future

        yield mock_client_instance


def test_searxng_tool_initialization(searxng_tool):
    """Testa a inicialização da SearXNGTool."""
    assert searxng_tool is not None
    assert searxng_tool.base_url is not None


@pytest.mark.parametrize(
    "category", [["general"], ["images"], ["news"], ["general", "images"]]
)
def test_searxng_tool_search_success_categories(
    mock_http_client, searxng_tool, category
):
    """Testa a busca síncrona bem-sucedida no SearXNG com diferentes categorias."""
    results = searxng_tool.search("OpenAI", categories=category)
    assert isinstance(results, list)
    assert len(results) > 0


@pytest.mark.parametrize(
    "safesearch",
    [
        SearXNGTool.SAFESEARCH_NONE,
        SearXNGTool.SAFESEARCH_MODERATE,
        SearXNGTool.SAFESEARCH_STRICT,
    ],
)
def test_searxng_tool_search_success_safesearch(
    mock_http_client, searxng_tool, safesearch
):
    """Testa a busca síncrona bem-sucedida no SearXNG com diferentes níveis de safesearch."""
    results = searxng_tool.search("OpenAI", safesearch=safesearch)
    assert isinstance(results, list)
    assert len(results) > 0


def test_searxng_tool_search_error(mock_http_client, searxng_tool):
    """Testa o tratamento de erro na busca síncrona do SearXNG."""
    mock_http_client.sync_request.side_effect = httpx.HTTPError(
        "Request Error"
    )  # mudar exception para httpx.HTTPError
    results = searxng_tool.search("OpenAI")
    assert isinstance(results, list)
    assert not results


# Testes para async_search
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "category", [["general"], ["images"], ["news"], ["general", "images"]]
)
async def test_searxng_tool_async_search_success_categories(
    mock_http_client, searxng_tool, category
):
    """Testa a busca assíncrona bem-sucedida no SearXNG com diferentes categorias."""
    results = await searxng_tool.async_search("OpenAI", categories=category)
    assert isinstance(results, list)
    assert len(results) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "safesearch",
    [
        SearXNGTool.SAFESEARCH_NONE,
        SearXNGTool.SAFESEARCH_MODERATE,
        SearXNGTool.SAFESEARCH_STRICT,
    ],
)
async def test_searxng_tool_async_search_success_safesearch(
    mock_http_client, searxng_tool, safesearch
):
    """Testa a busca assíncrona bem-sucedida no SearXNG com diferentes níveis de safesearch."""
    results = await searxng_tool.async_search("OpenAI", safesearch=safesearch)
    assert isinstance(results, list)
    assert len(results) > 0


@pytest.mark.asyncio
async def test_searxng_tool_async_search_error(mock_http_client, searxng_tool):
    """Testa o tratamento de erro na busca assíncrona do SearXNG."""
    mock_http_client.async_request.side_effect = httpx.HTTPError("HTTPError")
    results = await searxng_tool.async_search("OpenAI")
    assert isinstance(results, list)
    assert not results
