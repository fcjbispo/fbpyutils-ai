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

# Test cases for cancel_crawl
@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_cancel_crawl_success(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_response_data = {"status": "cancelled"}
    mock_client_instance.sync_request.return_value = mock_response_data
    tool = FireCrawlTool()
    job_id = "test_job_id"

    # Act
    result = tool.cancel_crawl(job_id)

    # Assert
    mock_client_instance.sync_request.assert_called_once_with(
        "DELETE",
        f"crawl/cancel/{job_id}",
        params=None,
        data=None,
        json=None,
        stream=False
    )
    assert result == mock_response_data

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_cancel_crawl_job_not_found(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_client_instance.sync_request.side_effect = httpx.HTTPStatusError(
        "Not Found", request=httpx.Request("DELETE", "url"), response=httpx.Response(404)
    )
    tool = FireCrawlTool()
    job_id = "non_existent_job_id"

    # Act & Assert
    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        tool.cancel_crawl(job_id)

    mock_client_instance.sync_request.assert_called_once_with(
        "DELETE",
        f"crawl/cancel/{job_id}",
        params=None,
        data=None,
        json=None,
        stream=False
    )
    assert excinfo.value.response.status_code == 404

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_cancel_crawl_api_error(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_client_instance.sync_request.side_effect = httpx.HTTPStatusError(
        "Internal Server Error", request=httpx.Request("DELETE", "url"), response=httpx.Response(500)
    )
    tool = FireCrawlTool()
    job_id = "test_job_id"

    # Act & Assert
    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        tool.cancel_crawl(job_id)

    mock_client_instance.sync_request.assert_called_once_with(
        "DELETE",
        f"crawl/cancel/{job_id}",
        params=None,
        data=None,
        json=None,
        stream=False
    )
    assert excinfo.value.response.status_code == 500

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_cancel_crawl_connection_error(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_client_instance.sync_request.side_effect = httpx.RequestError("Connection failed", request=httpx.Request("DELETE", "url"))
    tool = FireCrawlTool()
    job_id = "test_job_id"

    # Act & Assert
    with pytest.raises(httpx.RequestError) as excinfo:
        tool.cancel_crawl(job_id)

    mock_client_instance.sync_request.assert_called_once_with(
        "DELETE",
        f"crawl/cancel/{job_id}",
        params=None,
        data=None,
        json=None,
        stream=False
    )
    assert "Connection failed" in str(excinfo.value)
