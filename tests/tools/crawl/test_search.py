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

# Test cases for search
@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_search_success_basic_params(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_response_data = {
        "success": True,
        "data": [
            {"title": "Result 1", "url": "http://example.com/r1", "description": "..."}
        ],
        "warning": None
    }
    # Create a mock response object with a .json() method
    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_client_instance.sync_request.return_value = mock_response
    tool = FireCrawlTool()
    query = "test search"

    # Act
    result = tool.search(query)

    # Assert
    expected_payload = {
        "query": query,
        "limit": 5,
        "lang": "en",
        "country": "us",
        "timeout": 60000,
    }
    mock_client_instance.sync_request.assert_called_once_with(
        "POST",
        "search",
        json=expected_payload
    )
    assert result == mock_response_data

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_search_success_optional_params(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_response_data = {
        "success": True,
        "data": [
            {"title": "Result 1", "url": "http://example.com/r1", "description": "...", "markdown": "..."}
        ],
        "warning": None
    }
    # Create a mock response object with a .json() method
    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_client_instance.sync_request.return_value = mock_response
    tool = FireCrawlTool()
    query = "test search with options"
    optional_params = {
        "limit": 10,
        "tbs": "qdr:d",
        "lang": "es",
        "country": "mx",
        "timeout": 30000,
        "scrapeOptions": {
            "formats": ["markdown"],
            "onlyMainContent": True,
            "waitFor": 1000,
            "timeout": 45000,
            "removeBase64Images": True,
            "blockAds": True,
            "includeTags": ["article"],
            "excludeTags": ["aside"],
            "headers": {"X-Test": "search_scrape"},
            "jsonOptions": {"schema": {"title": "string"}},
            "extra_scrape_param": "extra" # Test kwargs in scrapeOptions
        },
        "extra_search_param": "extra" # Test kwargs in search
    }

    # Act
    result = tool.search(query, **optional_params)

    # Assert
    expected_scrape_options = {
        "formats": optional_params["scrapeOptions"]["formats"],
        "onlyMainContent": optional_params["scrapeOptions"]["onlyMainContent"],
        "waitFor": optional_params["scrapeOptions"]["waitFor"],
        "timeout": optional_params["scrapeOptions"]["timeout"],
        "removeBase64Images": optional_params["scrapeOptions"]["removeBase64Images"],
        "blockAds": optional_params["scrapeOptions"]["blockAds"],
        "includeTags": optional_params["scrapeOptions"]["includeTags"],
        "excludeTags": optional_params["scrapeOptions"]["excludeTags"],
        "headers": optional_params["scrapeOptions"]["headers"],
        "jsonOptions": optional_params["scrapeOptions"]["jsonOptions"],
        "extra_scrape_param": optional_params["scrapeOptions"]["extra_scrape_param"]
    }

    expected_payload = {
        "query": query,
        "limit": optional_params["limit"],
        "tbs": optional_params["tbs"],
        "lang": optional_params["lang"],
        "country": optional_params["country"],
        "timeout": optional_params["timeout"],
        "scrapeOptions": expected_scrape_options,
        "extra_search_param": optional_params["extra_search_param"]
    }
    mock_client_instance.sync_request.assert_called_once_with(
        "POST",
        "search",
        json=expected_payload
    )
    assert result == mock_response_data

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_search_ignore_unsupported_params(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_response_data = {
        "success": True,
        "data": [
            {"title": "Result 1", "url": "http://example.com/r1", "description": "..."}
        ],
        "warning": None
    }
    # Create a mock response object with a .json() method
    mock_response = MagicMock()
    mock_response.json.return_value = mock_response_data
    mock_client_instance.sync_request.return_value = mock_response
    tool = FireCrawlTool()
    query = "test search unsupported"
    unsupported_params = {
        "query": query,
        "location": "JP", # Unsupported
        "scrapeOptions": {
            "formats": ["markdown"], # Supported
            "onlyMainContent": True, # Supported
            "mobile": True, # Unsupported
            "skipTlsVerification": True, # Unsupported
            "actions": [{"type": "click", "selector": "#btn"}], # Unsupported
            "location": {"country": "JP"}, # Unsupported
            "proxy": "stealth", # Unsupported
            "changeTrackingOptions": {"mode": "git-diff"}, # Unsupported
        },
    }

    # Act
    result = tool.search(**unsupported_params)

    # Assert
    expected_scrape_options = {
        "formats": unsupported_params["scrapeOptions"]["formats"],
        "onlyMainContent": unsupported_params["scrapeOptions"]["onlyMainContent"],
    }

    expected_payload = {
        "query": query,
        "limit": 5,
        "lang": "en",
        "country": "us",
        "timeout": 60000,
        "scrapeOptions": {
            "formats": ["markdown"],
            "onlyMainContent": True,
            "mobile": True,
            "skipTlsVerification": True,
            "actions": [{"type": "click", "selector": "#btn"}],
            "location": {"country": "JP"},
            "proxy": "stealth",
            "changeTrackingOptions": {"mode": "git-diff"},
        },
        "location": "JP",
    }

    mock_client_instance.sync_request.assert_called_once_with(
        "POST",
        "search",
        json=expected_payload
    )
    assert result == mock_response_data

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_search_api_error(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_client_instance.sync_request.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=httpx.Request("POST", "url"), response=httpx.Response(400)
    )
    tool = FireCrawlTool()
    query = "test search"

    # Act & Assert
    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        tool.search(query)

    assert excinfo.value.response.status_code == 400

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_search_connection_error(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_client_instance.sync_request.side_effect = httpx.RequestError("Connection failed", request=httpx.Request("POST", "url"))
    tool = FireCrawlTool()
    query = "test search"

    # Act & Assert
    with pytest.raises(httpx.RequestError) as excinfo:
        tool.search(query)

    assert "Connection failed" in str(excinfo.value)
