import pytest
from unittest.mock import MagicMock, patch, call
from fbpyutils_ai.tools.crawl import FireCrawlTool
from fbpyutils_ai.tools.http import HTTPClient
import httpx

# Mock environment variables for testing
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("FBPY_FIRECRAWL_BASE_URL", "http://localhost:3005/v1")
    monkeypatch.setenv("FBPY_FIRECRAWL_API_KEY", "test_token")

# Test cases for get_extract_status
@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_get_extract_status_success(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_response_data = {
        "success": True,
        "data": {"extracted_info": "some data"},
        "status": "completed",
        "expiresAt": "..."
    }
    mock_client_instance.sync_request.return_value = mock_response_data
    tool = FireCrawlTool()
    job_id = "test_extract_job_id"

    # Act
    status = tool.get_extract_status(job_id)

    # Assert
    mock_client_instance.sync_request.assert_called_once_with(
        "GET",
        f"extract/{job_id}",
        params=None,
        data=None,
        json=None,
        stream=False
    )
    assert status == mock_response_data

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_get_extract_status_job_not_found(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_client_instance.sync_request.side_effect = httpx.HTTPStatusError(
        "Not Found", request=httpx.Request("GET", "url"), response=httpx.Response(404)
    )
    tool = FireCrawlTool()
    job_id = "non_existent_extract_job_id"

    # Act & Assert
    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        tool.get_extract_status(job_id)

    mock_client_instance.sync_request.assert_called_once_with(
        "GET",
        f"extract/{job_id}",
        params=None,
        data=None,
        json=None,
        stream=False
    )
    assert excinfo.value.response.status_code == 404

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_get_extract_status_api_error(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_client_instance.sync_request.side_effect = httpx.HTTPStatusError(
        "Internal Server Error", request=httpx.Request("GET", "url"), response=httpx.Response(500)
    )
    tool = FireCrawlTool()
    job_id = "test_extract_job_id"

    # Act & Assert
    with pytest.raises(httpx.HTTPStatusError) as excinfo:
        tool.get_extract_status(job_id)

    mock_client_instance.sync_request.assert_called_once_with(
        "GET",
        f"extract/{job_id}",
        params=None,
        data=None,
        json=None,
        stream=False
    )
    assert excinfo.value.response.status_code == 500

@patch('fbpyutils_ai.tools.crawl.HTTPClient')
def test_get_extract_status_connection_error(mock_http_client):
    # Arrange
    mock_client_instance = mock_http_client.return_value
    mock_client_instance.sync_request.side_effect = httpx.RequestError("Connection failed", request=httpx.Request("GET", "url"))
    tool = FireCrawlTool()
    job_id = "test_extract_job_id"

    # Act & Assert
    with pytest.raises(httpx.RequestError) as excinfo:
        tool.get_extract_status(job_id)

    mock_client_instance.sync_request.assert_called_once_with(
        "GET",
        f"extract/{job_id}",
        params=None,
        data=None,
        json=None,
        stream=False
    )
    assert "Connection failed" in str(excinfo.value)
