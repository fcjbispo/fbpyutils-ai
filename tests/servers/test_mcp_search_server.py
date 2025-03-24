import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from fbpyutils_ai.tools.search import SearXNGTool, SearXNGUtils
import pandas as pd
import httpx


@pytest.fixture
def mock_http_client():
    return MagicMock()


async def test_searxng_tool_search_success(mock_http_client):
    """Tests a successful synchronous search in SearXNGTool."""
    tool = SearXNGTool(base_url="http://test_url")
    tool.http_client = mock_http_client
    mock_http_client.sync_request.return_value = {
        "results": [{"title": "Test Result", "url": "http://example.com"}]
    }
    results = tool.search(query="test query")
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["title"] == "Test Result"


@pytest.mark.asyncio
async def test_searxng_tool_async_search_success(mock_http_client):
    """Tests a successful asynchronous search in SearXNGTool."""
    tool = SearXNGTool(base_url="http://test_url")
    tool.http_client = mock_http_client
    tool = SearXNGTool(base_url="http://test_url")
    tool.http_client = mock_http_client

    async def mock_async_request(*args, **kwargs):
        return {"results": [{"title": "Test Result", "url": "http://example.com"}]}

    mock_http_client.async_request.side_effect = mock_async_request
    results = await tool.async_search(query="test query")
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["title"] == "Test Result"


async def test_searxng_tool_search_http_error(mock_http_client):
    """Tests SearXNGTool search handling of HTTP errors."""
    tool = SearXNGTool(base_url="http://test_url")
    tool.http_client = mock_http_client
    mock_http_client.sync_request.side_effect = httpx.HTTPError("HTTP Error")
    results = tool.search(query="test query")
    assert isinstance(results, list)
    assert not results


@pytest.mark.asyncio
async def test_searxng_tool_async_search_http_error(mock_http_client):
    """Tests SearXNGTool async search handling of HTTP errors."""
    tool = SearXNGTool(base_url="http://test_url")
    tool.http_client = mock_http_client

    async def async_side_effect(*args, **kwargs):
        raise httpx.HTTPError("HTTP Error")

    mock_http_client.async_request.side_effect = async_side_effect
    results = await tool.async_search(query="test query")
    assert isinstance(results, list)
    assert not results


def test_searxng_utils_simplify_results():
    """Tests SearXNGUtils.simplify_results function."""
    results = [
        {
            "url": "http://example.com",
            "title": "Test Result",
            "content": "Test content",
            "score": 0.5,
            "publishedDate": "2024-01-01",
            "other": "extra",
        }
    ]
    simplified_results = SearXNGUtils.simplify_results(results)
    assert isinstance(simplified_results, list)
    assert len(simplified_results) == 1
    assert simplified_results[0]["url"] == "http://example.com"
    assert simplified_results[0]["other_info"] == {"other": "extra"}


def test_searxng_utils_convert_to_dataframe():
    """Tests SearXNGUtils.convert_to_dataframe function."""
    import pandas as pd

    results = [
        {
            "url": "http://example.com",
            "title": "Test Result",
            "content": "Test content",
            "score": 0.5,
            "publishedDate": "2024-01-01",
            "other_info": {"extra": "info"},
        }
    ]
    df = SearXNGUtils.convert_to_dataframe(results)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "url" in df.columns
    assert "other_info" in df.columns
