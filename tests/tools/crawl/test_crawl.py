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

# Test cases for crawl
@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_crawl_success_basic_params(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_response_data = {"jobId": "test_crawl_job_id"}
    mock_client_instance.sync_request.return_value = mock_response_data
    tool = FireCrawlTool()
    url = "http://example.com"

    # Act
    result = tool.crawl(url)

    # Assert
    expected_payload = {
        "url": url,
    }
    mock_client_instance.sync_request.assert_called_once_with(
        "POST",
        "crawl",
        json=expected_payload
    )
    assert result == mock_response_data

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_crawl_success_optional_params(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_response_data = {"jobId": "test_crawl_job_id_optional"}
    mock_client_instance.sync_request.return_value = mock_response_data
    tool = FireCrawlTool()
    url = "http://example.com"
    optional_params = {
        "excludePaths": ["/login"],
        "includePaths": ["/blog/*"],
        "maxDepth": 5,
        "maxDiscoveryDepth": 10,
        "ignoreSitemap": True,
        "ignoreQueryParameters": True,
        "limit": 50,
        "allowBackwardLinks": True,
        "allowExternalLinks": True,
        "webhook": {"url": "http://webhook.site/test"},
        "scrapeOptions": {
            "formats": ["html"],
            "onlyMainContent": True,
            "waitFor": 5000,
            "timeout": 45000,
            "removeBase64Images": True,
            "blockAds": True,
            "includeTags": ["article"],
            "excludeTags": ["aside"],
            "headers": {"X-Test": "crawl"},
            "jsonOptions": {"schema": {"title": "string"}},
            "extra_scrape_param": "extra" # Test kwargs in scrapeOptions
        },
        "extra_crawl_param": "extra" # Test kwargs in crawl
    }

    # Act
    result = tool.crawl(url, **optional_params)

    # Assert
    expected_payload = {
        "url": url,
        "excludePaths": optional_params["excludePaths"],
        "includePaths": optional_params["includePaths"],
        "maxDepth": optional_params["maxDepth"],
        "maxDiscoveryDepth": optional_params["maxDiscoveryDepth"],
        "ignoreSitemap": optional_params["ignoreSitemap"],
        "ignoreQueryParameters": optional_params["ignoreQueryParameters"],
        "limit": optional_params["limit"],
        "allowBackwardLinks": optional_params["allowBackwardLinks"],
        "allowExternalLinks": optional_params["allowExternalLinks"],
        "webhook": optional_params["webhook"],
        "scrapeOptions": {
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
        },
        "extra_crawl_param": optional_params["extra_crawl_param"]
    }
    mock_client_instance.sync_request.assert_called_once_with(
        "POST",
        "crawl",
        json=expected_payload
    )
    assert result == mock_response_data

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_crawl_ignore_unsupported_scrape_params_in_pageOptions(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_response_data = {"jobId": "test_crawl_job_id_unsupported"}
    mock_client_instance.sync_request.return_value = mock_response_data
    tool = FireCrawlTool()
    url = "http://example.com"
    unsupported_params = {
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
    result = tool.crawl(url, **unsupported_params)

    # Assert
    expected_scrape_options = {
        "formats": unsupported_params["scrapeOptions"]["formats"],
        "onlyMainContent": unsupported_params["scrapeOptions"]["onlyMainContent"],
    }
    # Ensure unsupported parameters are NOT in scrapeOptions
    assert "mobile" not in expected_scrape_options
    assert "skipTlsVerification" not in expected_scrape_options
    assert "actions" not in expected_scrape_options
    assert "location" not in expected_scrape_options
    assert "proxy" not in expected_scrape_options
    assert "changeTrackingOptions" not in expected_scrape_options

    expected_payload = {
        "url": url,
        "scrapeOptions": expected_scrape_options,
    }

    mock_client_instance.sync_request.assert_called_once_with(
        "POST",
        "crawl",
        json=expected_payload
    )
    assert result == mock_response_data


@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_crawl_api_error(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_client_instance.sync_request.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=httpx.Request("POST", "url"), response=httpx.Response(400)
    )
    tool = FireCrawlTool()
    url = "http://example.com"

    # Act & Assert
    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        tool.crawl(url)

    assert excinfo.value.response.status_code == 400

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_crawl_connection_error(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_client_instance.sync_request.side_effect = httpx.RequestError("Connection failed", request=httpx.Request("POST", "url"))
    tool = FireCrawlTool()
    url = "http://example.com"

    # Act & Assert
    with pytest.raises(httpx.RequestError) as excinfo:
        tool.crawl(url)

    assert "Connection failed" in str(excinfo.value)
