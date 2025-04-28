

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

# Test cases for batch_scrape
@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_batch_scrape_success_basic_params(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_response_data = {
        "success": True,
        "id": "test_batch_job_id",
        "url": "http://localhost:3005/v1/batch/scrape/test_batch_job_id",
        "invalidURLs": []
    }
    mock_client_instance.sync_request.return_value = mock_response_data
    tool = FireCrawlTool()
    urls = ["http://example.com/page1", "http://example.com/page2"]
    formats = ["markdown"]
    only_main_content = True

    # Act
    result = tool.batch_scrape(urls, formats=formats, onlyMainContent=only_main_content)

    # Assert
    expected_payload = {
        "urls": urls,
        "ignoreInvalidURLs": False, # Default value
        "formats": formats,
        "onlyMainContent": only_main_content,
        "waitFor": 0, # Default value
        "timeout": 30000, # Default value
        "removeBase64Images": False, # Default value
        "blockAds": False, # Default value
    }
    mock_client_instance.sync_request.assert_called_once_with(
        "POST",
        "batch/scrape",
        json=expected_payload
    )
    assert result == mock_response_data

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_batch_scrape_success_optional_params(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_response_data = {
        "success": True,
        "id": "test_batch_job_id_optional",
        "url": "http://localhost:3005/v1/batch/scrape/test_batch_job_id_optional",
        "invalidURLs": ["http://invalid.com"]
    }
    mock_client_instance.sync_request.return_value = mock_response_data
    tool = FireCrawlTool()
    urls = ["http://example.com/page1", "http://invalid.com"]
    optional_params = {
        "webhook": {"url": "http://webhook.site/test"},
        "ignoreInvalidURLs": True,
        "formats": ["html", "links"],
        "onlyMainContent": False,
        "includeTags": ["div.content"],
        "excludeTags": ["footer"],
        "headers": {"X-Custom-Header": "test"},
        "waitFor": 1000,
        "timeout": 60000,
        "jsonOptions": {"schema": {"title": "string"}},
        "removeBase64Images": True,
        "blockAds": True,
        "extra_param": "extra_value" # Test kwargs
    }

    # Act
    result = tool.batch_scrape(urls, **optional_params)

    # Assert
    expected_payload = {
        "urls": urls,
        "webhook": optional_params["webhook"],
        "ignoreInvalidURLs": optional_params["ignoreInvalidURLs"],
        "formats": optional_params["formats"],
        "onlyMainContent": optional_params["onlyMainContent"],
        "waitFor": optional_params["waitFor"],
        "timeout": optional_params["timeout"],
        "removeBase64Images": optional_params["removeBase64Images"],
        "blockAds": optional_params["blockAds"],
        "includeTags": optional_params["includeTags"],
        "excludeTags": optional_params["excludeTags"],
        "headers": optional_params["headers"],
        "jsonOptions": optional_params["jsonOptions"],
        "extra_param": optional_params["extra_param"]
    }
    mock_client_instance.sync_request.assert_called_once_with(
        "POST",
        "batch/scrape",
        json=expected_payload
    )
    assert result == mock_response_data

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_batch_scrape_ignore_unsupported_params(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_response_data = {
        "success": True,
        "id": "test_batch_job_id_unsupported",
        "url": "http://localhost:3005/v1/batch/scrape/test_batch_job_id_unsupported",
        "invalidURLs": []
    }
    mock_client_instance.sync_request.return_value = mock_response_data
    tool = FireCrawlTool()
    urls = ["http://example.com"]
    unsupported_params = {
        "mobile": True,
        "skipTlsVerification": True,
        "actions": [{"type": "click", "selector": "#btn"}],
        "location": {"country": "JP"},
        "proxy": "stealth",
        "changeTrackingOptions": {"mode": "git-diff"},
        "formats": ["markdown"], # Supported param
        "onlyMainContent": True # Supported param
    }

    # Act
    result = tool.batch_scrape(urls, **unsupported_params)

    # Assert
    expected_payload = {
        "urls": urls,
        "ignoreInvalidURLs": False, # Default value
        "formats": unsupported_params["formats"],
        "onlyMainContent": unsupported_params["onlyMainContent"],
        "waitFor": 0, # Default value
        "timeout": 30000, # Default value
        "removeBase64Images": False, # Default value
        "blockAds": False, # Default value
    }
    # Ensure unsupported parameters are NOT in the payload
    assert "mobile" not in expected_payload
    assert "skipTlsVerification" not in expected_payload
    assert "actions" not in expected_payload
    assert "location" not in expected_payload
    assert "proxy" not in expected_payload
    assert "changeTrackingOptions" not in expected_payload

    mock_client_instance.sync_request.assert_called_once_with(
        "POST",
        "batch/scrape",
        json=expected_payload
    )
    assert result == mock_response_data

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_batch_scrape_api_error(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_client_instance.sync_request.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=httpx.Request("POST", "url"), response=httpx.Response(400)
    )
    tool = FireCrawlTool()
    urls = ["http://example.com"]

    # Act & Assert
    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        tool.batch_scrape(urls)

    assert excinfo.value.response.status_code == 400

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_batch_scrape_connection_error(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_client_instance.sync_request.side_effect = httpx.RequestError("Connection failed", request=httpx.Request("POST", "url"))
    tool = FireCrawlTool()
    urls = ["http://example.com"]

    # Act & Assert
    with pytest.raises(httpx.RequestError) as excinfo:
        tool.batch_scrape(urls)

    assert "Connection failed" in str(excinfo.value)
