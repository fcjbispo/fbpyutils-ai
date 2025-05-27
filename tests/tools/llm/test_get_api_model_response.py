import pytest
import requests
from unittest.mock import patch, MagicMock

from fbpyutils_ai.tools.llm.utils import get_api_model_response
from fbpyutils_ai.tools.http import RequestsManager

@patch('fbpyutils_ai.tools.http.RequestsManager.make_request')
@patch('fbpyutils_ai.tools.http.RequestsManager.create_session')
def test_get_api_model_response_success(mock_create_session, mock_make_request):
    """
    Test successful API response retrieval.
    """
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"models": ["model1", "model2"]}
    mock_make_request.return_value = mock_response

    url = "http://example.com/api/models"
    api_key = "fake_api_key"

    response = get_api_model_response(url, api_key)

    mock_create_session.assert_called_once()
    mock_make_request.assert_called_once_with(
        session=mock_create_session.return_value,
        url=url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36", # Use the correct default User-Agent
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json_data={},
        timeout=300,
        method="GET",
        stream=False,
    )
    assert response.status_code == 200
    assert response.json() == {"models": ["model1", "model2"]}

@patch('fbpyutils_ai.tools.http.RequestsManager.make_request')
@patch('fbpyutils_ai.tools.http.RequestsManager.create_session')
def test_get_api_model_response_anthropic_headers(mock_create_session, mock_make_request):
    """
    Test correct headers for Anthropic API.
    """
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_make_request.return_value = mock_response

    url = "https://api.anthropic.com/v1/models"
    api_key = "fake_anthropic_key"

    get_api_model_response(url, api_key)

    mock_make_request.assert_called_once()
    called_headers = mock_make_request.call_args[1]['headers']
    assert called_headers["x-api-key"] == api_key
    assert called_headers["anthropic-version"] == "2023-06-01"
    assert called_headers["Authorization"] == f"Bearer {api_key}" # Ensure Authorization is still present

@patch('fbpyutils_ai.tools.http.RequestsManager.make_request')
@patch('fbpyutils_ai.tools.http.RequestsManager.create_session')
def test_get_api_model_response_custom_timeout(mock_create_session, mock_make_request):
    """
    Test custom timeout parameter is used.
    """
    mock_response = MagicMock(spec=requests.Response)
    mock_response.status_code = 200
    mock_make_request.return_value = mock_response

    url = "http://example.com/api/models"
    api_key = "fake_api_key"
    custom_timeout = 60

    get_api_model_response(url, api_key, timeout=custom_timeout)

    mock_make_request.assert_called_once()
    called_timeout = mock_make_request.call_args[1]['timeout']
    assert called_timeout == custom_timeout

@patch('fbpyutils_ai.tools.http.RequestsManager.make_request', side_effect=requests.exceptions.RequestException("Connection Error"))
@patch('fbpyutils_ai.tools.http.RequestsManager.create_session')
@patch('fbpyutils_ai.logging.error')
def test_get_api_model_response_exception_handling(mock_log_error, mock_create_session, mock_make_request):
    """
    Test exception handling and logging.
    """
    url = "http://example.com/api/models"
    api_key = "fake_api_key"

    with pytest.raises(requests.exceptions.RequestException):
        get_api_model_response(url, api_key)

    mock_create_session.assert_called_once()
    mock_make_request.assert_called_once()
    mock_log_error.assert_called_once_with("Failed to retrieve models: Connection Error")
