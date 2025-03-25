import pytest
import requests
from unittest.mock import patch, MagicMock
from requests.exceptions import Timeout, RequestException
from requests.adapters import HTTPAdapter

from fbpyutils_ai.tools.http import RequestsManager

@pytest.fixture
def mock_session():
    session = MagicMock()
    return session

def test_make_request_success_post(mock_session):
    """Test successful POST request with normal response"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "data": "test_data"}
    mock_session.post.return_value = mock_response
    
    # Make the request with POST method
    result = RequestsManager.make_request(
        session=mock_session,
        url="https://test.com/api",
        headers={"Content-Type": "application/json"},
        json_data={"test": "data"},
        timeout=10,
        method="POST",
        stream=False
    )
    
    # Verify request was made correctly
    mock_session.post.assert_called_once_with(
        "https://test.com/api",
        headers={"Content-Type": "application/json"},
        json={"test": "data"},
        timeout=10
    )
    
    # Verify result
    assert result == {"success": True, "data": "test_data"}
    
def test_make_request_success_get(mock_session):
    """Test successful GET request with normal response"""
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "data": "test_data"}
    mock_session.get.return_value = mock_response
    
    # Make the request with GET method (the default)
    result = RequestsManager.make_request(
        session=mock_session,
        url="https://test.com/api",
        headers={"Content-Type": "application/json"},
        json_data={"test": "data"},
        timeout=10,
        stream=False
    )
    
    # Verify request was made correctly
    mock_session.get.assert_called_once_with(
        "https://test.com/api",
        headers={"Content-Type": "application/json"},
        params={"test": "data"},  # Note: GET uses params instead of json
        timeout=10
    )
    
    # Verify result
    assert result == {"success": True, "data": "test_data"}

def test_make_request_streaming(mock_session):
    """Test successful request with streaming response"""
    # Setup mock response
    mock_response = MagicMock()
    # Mock iter_lines to return some data lines
    mock_response.iter_lines.return_value = [
        b'data: {"id": 1, "content": "first chunk"}',
        b'data: {"id": 2, "content": "second chunk"}',
        b'data: [DONE]'  # This should be ignored
    ]
    mock_session.post.return_value = mock_response
    
    # Make the streaming request - note that streaming forces POST even if method is GET
    stream_generator = RequestsManager.make_request(
        session=mock_session,
        url="https://test.com/api/stream",
        headers={"Content-Type": "application/json"},
        json_data={"test": "data"},
        timeout=10,
        method="GET",  # This should be ignored for streaming
        stream=True
    )
    
    # Verify request was made correctly with POST method
    mock_session.post.assert_called_once_with(
        "https://test.com/api/stream",
        headers={"Content-Type": "application/json"},
        json={"test": "data"},
        timeout=10,
        stream=True
    )
    
    # Collect results from the generator
    results = list(stream_generator)
    
    # Verify results (should have 2 items, not including the [DONE] marker)
    assert len(results) == 2
    assert results[0] == {"id": 1, "content": "first chunk"}
    assert results[1] == {"id": 2, "content": "second chunk"}

def test_make_request_timeout_get(mock_session):
    """Test GET request that times out"""
    # Setup mock to raise Timeout
    mock_session.get.side_effect = Timeout("Request timed out")
    
    # Make the request and expect it to raise Timeout
    with pytest.raises(Timeout):
        RequestsManager.make_request(
            session=mock_session,
            url="https://test.com/api",
            headers={"Content-Type": "application/json"},
            json_data={"test": "data"},
            timeout=10,
            method="GET",
            stream=False
        )
        
def test_make_request_timeout_post(mock_session):
    """Test POST request that times out"""
    # Setup mock to raise Timeout
    mock_session.post.side_effect = Timeout("Request timed out")
    
    # Make the request and expect it to raise Timeout
    with pytest.raises(Timeout):
        RequestsManager.make_request(
            session=mock_session,
            url="https://test.com/api",
            headers={"Content-Type": "application/json"},
            json_data={"test": "data"},
            timeout=10,
            method="POST",
            stream=False
        )

def test_make_request_error_post(mock_session):
    """Test POST request that fails with other error"""
    # Setup mock to raise RequestException
    mock_session.post.side_effect = RequestException("Connection failed")
    
    # Make the request and expect it to raise RequestException
    with pytest.raises(RequestException):
        RequestsManager.make_request(
            session=mock_session,
            url="https://test.com/api",
            headers={"Content-Type": "application/json"},
            json_data={"test": "data"},
            timeout=10,
            method="POST",
            stream=False
        )
        
def test_make_request_error_get(mock_session):
    """Test GET request that fails with other error"""
    # Setup mock to raise RequestException
    mock_session.get.side_effect = RequestException("Connection failed")
    
    # Make the request and expect it to raise RequestException
    with pytest.raises(RequestException):
        RequestsManager.make_request(
            session=mock_session,
            url="https://test.com/api",
            headers={"Content-Type": "application/json"},
            json_data={"test": "data"},
            timeout=10,
            method="GET",
            stream=False
        )

def test_retry_logic_post():
    """Test that retry logic is applied to the POST method"""
    with patch('requests.Session.post') as mock_post:
        # Setup mock to raise RequestException twice, then succeed on third try
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_post.side_effect = [
            RequestException("First failure"),
            RequestException("Second failure"),
            mock_response
        ]
        
        # Create a session to test with
        session = requests.Session()
        
        # Make the request, should succeed after retries
        result = RequestsManager.make_request(
            session=session,
            url="https://test.com/api",
            headers={"Content-Type": "application/json"},
            json_data={"test": "data"},
            timeout=10,
            method="POST",
            stream=False
        )
        
        # Verify the result and that post was called 3 times
        assert result == {"success": True}
        assert mock_post.call_count == 3
        
def test_retry_logic_get():
    """Test that retry logic is applied to the GET method"""
    with patch('requests.Session.get') as mock_get:
        # Setup mock to raise RequestException twice, then succeed on third try
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_get.side_effect = [
            RequestException("First failure"),
            RequestException("Second failure"),
            mock_response
        ]
        
        # Create a session to test with
        session = requests.Session()
        
        # Make the request, should succeed after retries
        result = RequestsManager.make_request(
            session=session,
            url="https://test.com/api",
            headers={"Content-Type": "application/json"},
            json_data={"test": "data"},
            timeout=10,
            method="GET",
            stream=False
        )
        
        # Verify the result and that get was called 3 times
        assert result == {"success": True}
        assert mock_get.call_count == 3

def test_invalid_method():
    """Test handling of invalid HTTP method"""
    session = requests.Session()
    
    # Make the request with an invalid method
    with pytest.raises(ValueError) as excinfo:
        RequestsManager.make_request(
            session=session,
            url="https://test.com/api",
            headers={"Content-Type": "application/json"},
            json_data={"test": "data"},
            timeout=10,
            method="PUT",  # Not supported
            stream=False
        )
    
    # Verify the error message
    assert "Unsupported HTTP method: PUT" in str(excinfo.value)

def test_create_session():
    """Test that create_session returns a properly configured Session"""
    session = RequestsManager.create_session(max_retries=3)
    
    # Check that it's a Session object
    assert isinstance(session, requests.Session)
    
    # Check that adapters are mounted
    assert any(isinstance(adapter, HTTPAdapter) for adapter in session.adapters.values())
    
    # Check max_retries is set correctly for https adapter
    https_adapter = session.adapters.get('https://')
    assert https_adapter.max_retries.total == 3

def test_request_convenience_method():
    """Test the convenience request method that creates a session and makes a request"""
    # Mock make_request to avoid actual HTTP calls
    with patch.object(RequestsManager, 'make_request') as mock_make_request, \
         patch.object(RequestsManager, 'create_session') as mock_create_session:
        
        # Set up mocks
        mock_session = MagicMock()
        mock_create_session.return_value = mock_session
        mock_make_request.return_value = {"success": True}
        
        # Call the convenience method
        result = RequestsManager.request(
            url="https://test.com/api",
            headers={"Content-Type": "application/json"},
            json_data={"test": "data"},
            timeout=30,
            method="POST",
            stream=False,
            max_retries=5
        )
        
        # Verify session was created
        mock_create_session.assert_called_once_with(max_retries=5)
        
        # Verify make_request was called with the right params
        mock_make_request.assert_called_once_with(
            session=mock_session,
            url="https://test.com/api",
            headers={"Content-Type": "application/json"},
            json_data={"test": "data"},
            timeout=30,
            method="POST", 
            stream=False
        )
        
        # Verify result was returned
        assert result == {"success": True}