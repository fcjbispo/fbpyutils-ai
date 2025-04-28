import pytest
from unittest.mock import MagicMock, patch
from fbpyutils_ai.tools.crawl import FireCrawlTool
from fbpyutils_ai.tools.http import HTTPClient
import httpx

# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("FBPY_FIRECRAWL_BASE_URL", "http://localhost:3005/v1")
    monkeypatch.setenv("FBPY_FIRECRAWL_API_KEY", "test_token")

# Test cases for map
@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_map_success_basic_params(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_response_data = {"success": True, "links": ["http://example.com/page1", "http://example.com/page2"]}
    mock_client_instance.sync_request.return_value = mock_response_data
    tool = FireCrawlTool()
    url = "http://example.com"

    # Act
    result = tool.map(url)

    # Assert
    expected_payload = {
        "url": url,
        "ignoreSitemap": True, # Default
        "sitemapOnly": False, # Default
        "includeSubdomains": False, # Default
        "limit": 5000, # Default
    }
    mock_client_instance.sync_request.assert_called_once_with(
        "POST",
        "map",
        json=expected_payload
    )
    assert result == mock_response_data

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_map_success_optional_params(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_response_data = {"success": True, "links": ["http://example.com/products/item1"]}
    mock_client_instance.sync_request.return_value = mock_response_data
    tool = FireCrawlTool()
    url = "http://example.com"
    optional_params = {
        "search": "products",
        "ignoreSitemap": False,
        "sitemapOnly": True,
        "includeSubdomains": True,
        "limit": 100,
        "timeout": 10000,
        "extra_param": "extra_value" # Test kwargs
    }

    # Act
    result = tool.map(url, **optional_params)

    # Assert
    expected_payload = {
        "url": url,
        "search": optional_params["search"],
        "ignoreSitemap": optional_params["ignoreSitemap"],
        "sitemapOnly": optional_params["sitemapOnly"],
        "includeSubdomains": optional_params["includeSubdomains"],
        "limit": optional_params["limit"],
        "timeout": optional_params["timeout"],
        "extra_param": optional_params["extra_param"]
    }
    mock_client_instance.sync_request.assert_called_once_with(
        "POST",
        "map",
        json=expected_payload
    )
    assert result == mock_response_data

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_map_api_error(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_client_instance.sync_request.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=httpx.Request("POST", "map"), response=httpx.Response(400)
    )
    tool = FireCrawlTool()
    url = "http://example.com"

    # Act & Assert
    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        tool.map(url)

    assert excinfo.value.response.status_code == 400

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_map_connection_error(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_client_instance.sync_request.side_effect = httpx.RequestError("Connection failed", request=httpx.Request("POST", "map"))
    tool = FireCrawlTool()
    url = "http://example.com"

    # Act & Assert
    with pytest.raises(httpx.RequestError) as excinfo:
        tool.map(url)

    assert "Connection failed" in str(excinfo.value)
