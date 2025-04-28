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

# Test cases for extract
@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_extract_success_basic_params(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_response_data = {"success": True, "id": "test_extract_job_id"}
    mock_client_instance.sync_request.return_value = mock_response_data
    tool = FireCrawlTool()
    urls = ["http://example.com/product/*"]
    schema = {"product_name": "string"}

    # Act
    result = tool.extract(urls, schema=schema)

    # Assert
    expected_payload = {
        "urls": urls,
        "schema": schema,
        "ignoreSitemap": False, # Default
        "includeSubdomains": True, # Default
        "showSources": False, # Default
    }
    mock_client_instance.sync_request.assert_called_once_with(
        "POST",
        "extract",
        json=expected_payload
    )
    assert result == mock_response_data

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_extract_success_optional_params(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_response_data = {"success": True, "id": "test_extract_job_id_optional"}
    mock_client_instance.sync_request.return_value = mock_response_data
    tool = FireCrawlTool()
    urls = ["http://example.com/article/*"]
    optional_params = {
        "prompt": "Extract author and title",
        "schema": {"author": "string", "title": "string"},
        "ignoreSitemap": True,
        "includeSubdomains": False,
        "showSources": True,
        "scrapeOptions": {
            "formats": ["markdown"],
            "onlyMainContent": True,
            "waitFor": 1000,
            "timeout": 45000,
            "removeBase64Images": True,
            "blockAds": True,
            "includeTags": ["article"],
            "excludeTags": ["aside"],
            "headers": {"X-Test": "extract"},
            "jsonOptions": {"schema": {"title": "string"}},
            "extra_scrape_param": "extra" # Test kwargs in scrapeOptions
        },
        "extra_extract_param": "extra" # Test kwargs in extract
    }

    # Act
    result = tool.extract(urls, **optional_params)

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
        "urls": urls,
        "prompt": optional_params["prompt"],
        "schema": optional_params["schema"],
        "ignoreSitemap": optional_params["ignoreSitemap"],
        "includeSubdomains": optional_params["includeSubdomains"],
        "showSources": optional_params["showSources"],
        "scrapeOptions": expected_scrape_options,
        "extra_extract_param": optional_params["extra_extract_param"]
    }
    mock_client_instance.sync_request.assert_called_once_with(
        "POST",
        "extract",
        json=expected_payload
    )
    assert result == mock_response_data

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_extract_ignore_unsupported_params(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_response_data = {"success": True, "id": "test_extract_job_id_unsupported"}
    mock_client_instance.sync_request.return_value = mock_response_data
    tool = FireCrawlTool()
    urls = ["http://example.com"]
    unsupported_params = {
        "enableWebSearch": True, # Unsupported
        "prompt": "Extract data", # Supported
        "schema": {"data": "string"}, # Supported
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
    result = tool.extract(urls, **unsupported_params)

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
        "urls": urls,
        "prompt": unsupported_params["prompt"],
        "schema": unsupported_params["schema"],
        "ignoreSitemap": False, # Default
        "includeSubdomains": True, # Default
        "showSources": False, # Default
        "scrapeOptions": expected_scrape_options,
    }
    # Ensure unsupported parameters are NOT in the main payload
    assert "enableWebSearch" not in expected_payload

    mock_client_instance.sync_request.assert_called_once_with(
        "POST",
        "extract",
        json=expected_payload
    )
    assert result == mock_response_data

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_extract_api_error(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_client_instance.sync_request.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=httpx.Request("POST", "url"), response=httpx.Response(400)
    )
    tool = FireCrawlTool()
    urls = ["http://example.com"]

    # Act & Assert
    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        tool.extract(urls)

    assert excinfo.value.response.status_code == 400

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_extract_connection_error(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_client_instance.sync_request.side_effect = httpx.RequestError("Connection failed", request=httpx.Request("POST", "url"))
    tool = FireCrawlTool()
    urls = ["http://example.com"]

    # Act & Assert
    with pytest.raises(httpx.RequestError) as excinfo:
        tool.extract(urls)

    assert "Connection failed" in str(excinfo.value)
