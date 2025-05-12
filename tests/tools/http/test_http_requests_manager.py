import json
import pytest
import requests
from unittest.mock import patch, MagicMock
from requests.exceptions import Timeout, RequestException
import tenacity # Import tenacity for RetryError
from tenacity import stop_after_attempt, wait_fixed, RetryError # Import specific tenacity components and RetryError
from requests.adapters import HTTPAdapter
from tenacity.wait import wait_base # Import wait_base for type checking
from tenacity.stop import stop_base # Import stop_base for type checking
from tenacity.wait import wait_base # Import wait_base for type checking
from tenacity.stop import stop_base # Import stop_base for type checking

from fbpyutils_ai.tools.http import RequestsManager

@pytest.fixture  
def mock_session():
    session = MagicMock()
    return session

def test_make_request_success_post(mock_session):
    """Test successful POST request with normal response"""
    # Setup mock response
    # Setup mock response using a real requests.Response object
    mock_response = requests.Response()
    mock_response.status_code = 200
    # Mock the json method on the real Response object
    mock_response.json = MagicMock(return_value={"success": True, "data": "test_data"})
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
        timeout=(10, 10)  # Expect tuple after internal conversion
    )
    
    # Verify result
    assert isinstance(result, requests.Response)
    assert result.json() == {"success": True, "data": "test_data"}
    
def test_make_request_success_get(mock_session):
    """Test successful GET request with normal response"""
    # Setup mock response
    # Setup mock response using a real requests.Response object
    mock_response = requests.Response()
    mock_response.status_code = 200
    # Mock the json method on the real Response object
    mock_response.json = MagicMock(return_value={"success": True, "data": "test_data"})
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
        timeout=(10, 10)  # Expect tuple after internal conversion
    )
    
    # Verify result
    assert isinstance(result, requests.Response)
    assert result.json() == {"success": True, "data": "test_data"}

def test_make_request_streaming(mock_session):
    """Test successful request with streaming response"""
    # Setup mock response
    # Setup mock response using a real requests.Response object
    mock_response = requests.Response()
    mock_response.status_code = 200
    # Mock iter_lines to return some data lines
    mock_response.iter_lines = MagicMock(return_value=[
        b'data: {"id": 1, "content": "first chunk"}',
        b'data: {"id": 2, "content": "second chunk"}',
        b'data: [DONE]'  # This should be ignored
    ])
    mock_session.post.return_value = mock_response
    
    # Make the streaming request - note that streaming forces POST even if method is GET
    response = RequestsManager.make_request(
        session=mock_session,
        url="https://test.com/api/stream",
        headers={"Content-Type": "application/json"},
        json_data={"test": "data"},
        timeout=10,
        method="POST", # Streaming requires POST in RequestsManager
        stream=True
    )
    
    # Verify request was made correctly with POST method
    mock_session.post.assert_called_once_with(
        "https://test.com/api/stream",
        headers={"Content-Type": "application/json"},
        json={"test": "data"},
        timeout=(10, 10), # Expect tuple after internal conversion
        stream=True
    )
    
    # Verify that a requests.Response object is returned
    assert isinstance(response, requests.Response)
    
    # Simulate client consuming the stream and parsing JSON
    results = []
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data:') and not 'data: [DONE]' in line:
                json_str = line[5:].strip()
                if json_str:
                    try:
                        results.append(json.loads(json_str))
                    except json.JSONDecodeError:
                        pytest.fail(f"Failed to decode JSON from stream line: {json_str}")

    # Verify results (should have 2 items, not including the [DONE] marker)
    assert len(results) == 2
    assert results[0] == {"id": 1, "content": "first chunk"}
    assert results[1] == {"id": 2, "content": "second chunk"}

def test_make_request_timeout_get(mock_session):
    """Test GET request that times out"""
    # Setup mock to raise Timeout
    mock_session.get.side_effect = Timeout("Request timed out")
    
    # Make the request and expect it to raise Timeout
    # Expect RetryError because of the @retry decorator
    with pytest.raises(tenacity.RetryError) as excinfo:
        RequestsManager.make_request(
            session=mock_session,
            url="https://test.com/api",
            headers={"Content-Type": "application/json"},
            json_data={"test": "data"},
            timeout=10,
            method="GET",
            stream=False,
            stop=tenacity.stop_after_attempt(3) # Explicitly pass stop parameter
        )
    # Optionally check the root cause
    assert isinstance(excinfo.value.__cause__, Timeout) # Check the chained exception
    # Verify the mock was called the expected number of times (3 attempts)
    assert mock_session.get.call_count == 3
        
def test_make_request_timeout_post(mock_session):
    """Test POST request that times out"""
    # Setup mock to raise Timeout
    mock_session.post.side_effect = Timeout("Request timed out")
    
    # Make the request and expect it to raise Timeout
    # Expect RetryError because of the @retry decorator
    with pytest.raises(tenacity.RetryError) as excinfo:
        RequestsManager.make_request(
            session=mock_session,
            url="https://test.com/api",
            headers={"Content-Type": "application/json"},
            json_data={"test": "data"},
            timeout=10,
            method="POST",
            stream=False,
            stop=tenacity.stop_after_attempt(3) # Explicitly pass stop parameter
        )
    # Optionally check the root cause
    assert isinstance(excinfo.value.__cause__, Timeout) # Check the chained exception
    # Verify the mock was called the expected number of times (3 attempts)
    assert mock_session.post.call_count == 3

def test_make_request_error_post(mock_session):
    """Test POST request that fails with other error"""
    # Setup mock to raise RequestException
    mock_session.post.side_effect = RequestException("Connection failed")
    
    # Make the request and expect it to raise RequestException
    # Expect RetryError because of the @retry decorator
    with pytest.raises(tenacity.RetryError) as excinfo:
        RequestsManager.make_request(
            session=mock_session,
            url="https://test.com/api",
            headers={"Content-Type": "application/json"},
            json_data={"test": "data"},
            timeout=10,
            method="POST",
            stream=False,
            stop=tenacity.stop_after_attempt(3) # Explicitly pass stop parameter
        )
    # Optionally check the root cause
    assert isinstance(excinfo.value.__cause__, RequestException) # Check the chained exception
    # Verify the mock was called the expected number of times (3 attempts)
    assert mock_session.post.call_count == 3
        
def test_make_request_error_get(mock_session):
    """Test GET request that fails with other error"""
    # Setup mock to raise RequestException
    mock_session.get.side_effect = RequestException("Connection failed")
    
    # Make the request and expect it to raise RequestException
    # Expect RetryError because of the @retry decorator
    with pytest.raises(tenacity.RetryError) as excinfo:
        RequestsManager.make_request(
            session=mock_session,
            url="https://test.com/api",
            headers={"Content-Type": "application/json"},
            json_data={"test": "data"},
            timeout=10,
            method="GET",
            stream=False,
            stop=tenacity.stop_after_attempt(3) # Explicitly pass stop parameter
        )
    # Optionally check the root cause
    assert isinstance(excinfo.value.__cause__, RequestException) # Check the chained exception
    # Verify the mock was called the expected number of times (3 attempts)
    assert mock_session.get.call_count == 3

def test_retry_logic_post():
    """Test that retry logic is applied to the POST method"""
    with patch('requests.Session.post') as mock_post:
        # Setup mock to raise RequestException twice, then succeed on third try
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"success": True})
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
            stream=False,
            stop=tenacity.stop_after_attempt(3) # Explicitly pass stop parameter
        )
        
        # Verify the result and that post was called 3 times
        assert isinstance(result, requests.Response)
        assert result.json() == {"success": True}
        assert mock_post.call_count == 3
        
def test_retry_logic_get():
    """Test that retry logic is applied to the GET method"""
    with patch('requests.Session.get') as mock_get:
        # Setup mock to raise RequestException twice, then succeed on third try
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value={"success": True})
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
            stream=False,
            stop=tenacity.stop_after_attempt(3) # Explicitly pass stop parameter
        )
        
        # Verify the result and that get was called 3 times
        assert isinstance(result, requests.Response)
        assert result.json() == {"success": True}
        assert mock_get.call_count == 3

def test_invalid_method():
    """Test handling of invalid HTTP method"""
    session = requests.Session()
    
    # Make the request with an invalid method
    # Expect ValueError directly from validation for a truly unsupported method
    with pytest.raises(ValueError) as excinfo:
        RequestsManager.make_request(
            session=session,
            url="https://test.com/api",
            headers={"Content-Type": "application/json"},
            json_data={"test": "data"},
            timeout=10,
            method="PATCH",  # Truly unsupported method
            stream=False
        )
    
    # Verify the error message
    assert "Unsupported HTTP method: PATCH" in str(excinfo.value)

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
            max_retries=5,
            wait=tenacity.wait_fixed(1), # Pass wait parameter
            stop=tenacity.stop_after_attempt(4) # Pass stop parameter
        )
        
        # Verify session was created
        mock_create_session.assert_called_once_with(
            max_retries=5, auth=None, bearer_token=None, verify_ssl=True
        )
        
        # Verify make_request was called with the right params, including retry parameters
        mock_make_request.assert_called_once_with(
            session=mock_session,
            url="https://test.com/api",
            headers={"Content-Type": "application/json"},
            json_data={"test": "data"},
            timeout=30,
            method="POST",
            stream=False,
            wait=tenacity.wait_fixed(1), # Verify wait parameter is passed
            stop=tenacity.stop_after_attempt(4) # Verify stop parameter is passed
        )
        
        # Verify result was returned
        assert result == {"success": True}
        
        # Verify make_request was called with the right params, including retry parameters
        # Compare types and parameters, not object identity for tenacity objects
        call_args, call_kwargs = mock_make_request.call_args
        assert 'wait' in call_kwargs
        assert 'stop' in call_kwargs
        assert isinstance(call_kwargs['wait'], wait_base)
        assert call_kwargs['wait'].__dict__ == tenacity.wait_fixed(1).__dict__
        assert isinstance(call_kwargs['stop'], stop_base)
        assert call_kwargs['stop'].__dict__ == tenacity.stop_after_attempt(4).__dict__
