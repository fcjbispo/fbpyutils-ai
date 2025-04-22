import json
import gzip
import io
import httpx
import logging
import requests
from time import perf_counter
from requests.adapters import HTTPAdapter
from typing import Any, Optional, Dict, Union, Generator, List, Tuple
from tenacity import retry, wait_random_exponential, stop_after_attempt


def basic_header() -> Dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Content-Type": "application/json",
    }


class HTTPClient:
    """HTTP Client for synchronous and asynchronous requests.

    Supports GET and POST methods.
    Includes streaming response capability and handles JSON/Gzip responses.

    Attributes:
        base_url (str): Base URL for all requests
        headers (Dict): Default HTTP headers

    Examples:
        >>> client = HTTPClient(base_url="https://api.example.com")
        >>> # Synchronous request
        >>> response = client.sync_request("GET", "data")
        >>> # Asynchronous request
        >>> import asyncio
        >>> async def main():
        ...     return await client.async_request("GET", "data")
        >>> asyncio.run(main())
    """

    def __init__(
        self, base_url: str, headers: Optional[Dict] = None, verify_ssl: bool = True
    ):
        """Initializes the HTTP client with basic configurations.

        Args:
            base_url (str): Base URL for requests (must include protocol).
            headers (Optional[Dict]): Default headers for all requests.
            verify_ssl (bool): Verify SSL certificate (default: True).

        Raises:
            ValueError: If base_url is invalid.
        """
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must include protocol (http/https)")

        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.verify_ssl = verify_ssl

        # Configura clientes com timeout padrão e reutilização de conexão
        self._sync_client = httpx.Client(
            headers=self.headers, timeout=httpx.Timeout(10.0)
        )
        self._async_client = httpx.AsyncClient(
            headers=self.headers, timeout=httpx.Timeout(10.0)
        )
        logging.info(f"HTTPClient initialized for {self.base_url}")

    async def _handle_response_content(self, response: httpx.Response) -> Union[Dict, List, str]:
        """Handles response content, including Gzip decompression and JSON parsing."""
        content: bytes
        if response.headers.get('Content-Encoding') == 'gzip':
            logging.debug("Decompressing Gzip content.")
            try:
                buf = io.BytesIO(await response.aread())
                with gzip.GzipFile(fileobj=buf) as f:
                    content = f.read()
            except Exception as e:
                logging.error(f"Failed to decompress Gzip content: {e}")
                # Return raw compressed content if decompression fails
                return await response.aread()
        else:
            content = await response.aread()

        # Attempt to decode as UTF-8, fallback to ISO-8859-1 or ignore errors
        try:
            content_str = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                content_str = content.decode("iso-8859-1")
                logging.warning("Decoded content using ISO-8859-1 as fallback.")
            except UnicodeDecodeError:
                content_str = content.decode("utf-8", errors="ignore")
                logging.warning("Decoded content using UTF-8 with errors ignored.")

        # Attempt JSON parsing
        try:
            # First try httpx's built-in json() which handles BOM etc.
            # We need to re-read the response if we didn't read it before
            # or construct a new response object if we decompressed.
            # Easiest is to try parsing the string we already have.
            return json.loads(content_str)
        except json.JSONDecodeError as e1:
            logging.warning(f"Failed to parse response as JSON with json.loads: {e1}")
            # Return dict with original content and error message
            return {
                'content': content_str,
                'message': f"Failed to parse response as JSON: {e1}"
            }

    async def async_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json_payload: Optional[Dict] = None, # Renamed to avoid conflict
        stream: bool = False,
    ) -> Union[Dict, List, httpx.Response]:
        """Executes an asynchronous HTTP request (GET or POST).

        Args:
            method (str): HTTP method (GET, POST).
            endpoint (str): Endpoint relative to base_url.
            params (Optional[Dict]): Query parameters (optional).
            data (Optional[Dict]): Data for form-urlencoded body (optional, POST only).
            json_payload (Optional[Dict]): Data for JSON body (optional, POST only).
            stream (bool): If True, returns the response object for streaming consumption (default: False).

        Returns:
            Union[Dict, List, httpx.Response]: Parsed JSON response if stream=False,
                                                httpx.Response object for streaming if stream=True.
                                                Returns a dict with error if JSON parsing fails.

        Raises:
            httpx.HTTPStatusError: For 4xx/5xx status codes.
            ValueError: If an unsupported HTTP method is used.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = perf_counter()
        method_upper = method.upper()

        if method_upper not in ["GET", "POST"]:
             raise ValueError(f"Unsupported HTTP method: {method}. Only GET and POST are supported.")

        logging.debug(f"Starting asynchronous request: {method_upper} {url}")
        logging.info(
            f"Params: {params} | Data: {data} | JSON: {json_payload} | Stream: {stream}"
        )

        # Add Accept-Encoding header
        request_headers = self.headers.copy()
        request_headers['Accept-Encoding'] = 'gzip'

        try:
            response: httpx.Response

            if method_upper == "GET":
                response = await self._async_client.get(
                    url, params=params, headers=request_headers
                )
            elif method_upper == "POST":
                response = await self._async_client.post(
                    url, params=params, data=data, json=json_payload, headers=request_headers
                )
            # No else needed due to check above

            response.raise_for_status()

            duration = perf_counter() - start_time
            content_length_header = response.headers.get('Content-Length', 'N/A')
            logging.debug(
                f"Asynchronous request completed in {duration:.2f}s | "
                f"Status: {response.status_code} | "
                f"Content-Length: {content_length_header} | Stream: {stream}"
            )

            if stream:
                logging.debug("Returning raw response object for streaming.")
                return response
            else:
                logging.debug("Processing response content (JSON/Gzip).")
                return await self._handle_response_content(response)

        except httpx.HTTPStatusError as e:
            logging.error(
                f"HTTP Error {e.response.status_code} in {method_upper} {url}: "
                f"{e.response.text[:200]}..."
            )
            # Attempt to parse error response as JSON, otherwise raise original error
            try:
                error_content = await self._handle_response_content(e.response)
                logging.warning(f"Returning parsed error response: {error_content}")
                return error_content # Return parsed error dict/list
            except Exception as parse_err:
                logging.error(f"Could not parse error response body: {parse_err}")
                raise e # Re-raise original HTTPStatusError if parsing fails
        except Exception as e:
            logging.exception(f"Unexpected error during async request {method_upper} {url}: {e}")
            raise
        finally:
            logging.debug(f"Processing of {method_upper} {url} finished")

    def _handle_sync_response_content(self, response: httpx.Response) -> Union[Dict, List, str]:
        """Handles synchronous response content, including Gzip decompression and JSON parsing."""
        content: bytes
        if response.headers.get('Content-Encoding') == 'gzip':
            logging.debug("Decompressing Gzip content.")
            try:
                # httpx sync response content is already read into response.content
                buf = io.BytesIO(response.content)
                with gzip.GzipFile(fileobj=buf) as f:
                    content = f.read()
            except Exception as e:
                logging.error(f"Failed to decompress Gzip content: {e}")
                # Return raw compressed content if decompression fails
                return response.content
        else:
            content = response.content

        # Attempt to decode as UTF-8, fallback to ISO-8859-1 or ignore errors
        try:
            content_str = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                content_str = content.decode("iso-8859-1")
                logging.warning("Decoded content using ISO-8859-1 as fallback.")
            except UnicodeDecodeError:
                content_str = content.decode("utf-8", errors="ignore")
                logging.warning("Decoded content using UTF-8 with errors ignored.")

        # Attempt JSON parsing
        try:
            # First try httpx's built-in json() which handles BOM etc.
            # Need to be careful here as response.content was already read.
            # Try parsing the string we decoded.
            return json.loads(content_str)
        except json.JSONDecodeError as e1:
            logging.warning(f"Failed to parse response as JSON with json.loads: {e1}")
            # Return dict with original content and error message
            return {
                'content': content_str,
                'message': f"Failed to parse response as JSON: {e1}"
            }

    def sync_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json_payload: Optional[Dict] = None, # Renamed
        stream: bool = False,
    ) -> Union[Dict, List, httpx.Response]:
        """Executes a synchronous HTTP request (GET or POST).

        Args:
            method (str): HTTP method (GET, POST).
            endpoint (str): Endpoint relative to base_url.
            params (Optional[Dict]): Query parameters (optional).
            data (Optional[Dict]): Data for form-urlencoded body (optional, POST only).
            json_payload (Optional[Dict]): Data for JSON body (optional, POST only).
            stream (bool): If True, returns the response object for streaming consumption (default: False).

        Returns:
            Union[Dict, List, httpx.Response]: Parsed JSON response if stream=False,
                                                httpx.Response object for streaming if stream=True.
                                                Returns a dict with error if JSON parsing fails.

        Raises:
            httpx.HTTPStatusError: For 4xx/5xx status codes.
            ValueError: If an unsupported HTTP method is used.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = perf_counter()
        method_upper = method.upper()

        if method_upper not in ["GET", "POST"]:
             raise ValueError(f"Unsupported HTTP method: {method}. Only GET and POST are supported.")

        logging.debug(f"Starting synchronous request: {method_upper} {url}")
        logging.info(
            f"Params: {params} | Data: {data} | JSON: {json_payload} | Stream: {stream}"
        )

        # Add Accept-Encoding header
        request_headers = self.headers.copy()
        request_headers['Accept-Encoding'] = 'gzip'

        try:
            response: httpx.Response

            if method_upper == "GET":
                response = self._sync_client.get(url, params=params, headers=request_headers)
            elif method_upper == "POST":
                response = self._sync_client.post(url, params=params, data=data, json=json_payload, headers=request_headers)
            # No else needed

            response.raise_for_status()

            duration = perf_counter() - start_time
            content_length_header = response.headers.get('Content-Length', 'N/A')
            logging.debug(
                f"Synchronous request completed in {duration:.2f}s | "
                f"Status: {response.status_code} | "
                f"Content-Length: {content_length_header} | Stream: {stream}"
            )

            if stream:
                logging.debug("Returning raw response object for streaming.")
                return response
            else:
                logging.debug("Processing response content (JSON/Gzip).")
                return self._handle_sync_response_content(response)

        except httpx.HTTPStatusError as e:
            logging.error(
                f"HTTP Error {e.response.status_code} in {method_upper} {url}: "
                f"{e.response.text[:200]}..."
            )
            # Attempt to parse error response as JSON, otherwise raise original error
            try:
                error_content = self._handle_sync_response_content(e.response)
                logging.warning(f"Returning parsed error response: {error_content}")
                return error_content # Return parsed error dict/list
            except Exception as parse_err:
                logging.error(f"Could not parse error response body: {parse_err}")
                raise e # Re-raise original HTTPStatusError if parsing fails
        except Exception as e:
            logging.exception(f"Unexpected error during sync request {method_upper} {url}: {e}")
            raise
        finally:
            logging.debug(f"Processing of {method_upper} {url} finished")

    def __enter__(self):
        """Support for synchronous context management."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensures proper closing of the synchronous client."""
        self._sync_client.close()

    async def __aenter__(self):
        """Support for asynchronous context management."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ensures proper closing of the asynchronous client."""
        await self._async_client.aclose()


# HTTP Request manager for API calls
class RequestsManager:
    """
    A utility class for making HTTP requests with retry logic and error handling.

    This class provides a common interface for making HTTP requests to external APIs,
    handling common error scenarios, and supporting both streaming and non-streaming responses.

    Features:
    - Support for GET and POST HTTP methods.
    - Streaming response handling (POST only).
    - Automatic retry with exponential backoff.
    - JSON response parsing with fallback and error reporting.
    - Gzip content decompression.
    - Comprehensive error handling and logging.
    - Centralized HTTP session management.

    The class is primarily designed for interacting with LLM APIs like OpenAI but can be
    used for any service that requires HTTP requests with JSON responses.
    """

    @staticmethod
    def create_session(
        max_retries: int = 2,
        auth: Optional[Tuple[str, str]] = None,
        bearer_token: Optional[str] = None,
        verify_ssl: Union[bool, str] = True,
    ) -> requests.Session:
        """
        Creates and configures a requests Session with retry capabilities.

        Args:
            max_retries: Maximum number of retries for the session adapter
            auth: Tuple of (username, password) for basic authentication
            bearer_token: Bearer token for authentication
            verify_ssl: Verify SSL certificate (True/False or path to CA bundle)

        Returns:
            A configured requests.Session object
        """
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=max_retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        if auth:
            session.auth = auth
        if bearer_token:
            session.headers.update({"Authorization": f"Bearer {bearer_token}"})

        session.verify = verify_ssl
        return session

    @staticmethod
    def request(
        url: str,
        headers: Dict[str, str],
        json_data: Dict[str, Any],
        timeout: Union[int, Tuple[int, int]] = (30, 30),
        method: str = "GET",
        stream: bool = False,
        max_retries: int = 2,
        auth: Optional[Tuple[str, str]] = None,
        bearer_token: Optional[str] = None,
        verify_ssl: Union[bool, str] = True,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Convenience method that creates a session and makes a request in one call.

        Args:
            url: The URL to make the request to.
            headers: The headers to include in the request.
            json_data: The JSON data to include in the request body.
            timeout: The request timeout in seconds or tuple of (connect, read) timeouts.
            method: HTTP method to use ("GET" or "POST", defaults to "GET").
            stream: Whether to stream the response (POST only).
            max_retries: Maximum number of retries for the session adapter.
            auth: Tuple of (username, password) for basic authentication.
            bearer_token: Bearer token for authentication.
            verify_ssl: Verify SSL certificate (True/False or path to CA bundle).

        Returns:
            If stream=False, returns the parsed JSON response (Dict/List) or an error dict.
            If stream=True, returns a generator yielding parsed JSON objects from the streaming response.

        Raises:
            ValueError: If an unsupported HTTP method is specified.
            requests.exceptions.RequestException: For request-related errors.
        """
        session = RequestsManager.create_session(
            max_retries=max_retries,
            auth=auth,
            bearer_token=bearer_token,
            verify_ssl=verify_ssl,
        )
        return RequestsManager.make_request(
            session=session,
            url=url,
            headers=headers,
            json_data=json_data,
            timeout=timeout,
            method=method,
            stream=stream,
        )

    @staticmethod
    # @retry decorator removed from here and moved to the internal method
    def make_request(
        session: requests.Session,
        url: str,
        headers: Dict[str, str],
        json_data: Dict[str, Any],
        timeout: Union[int, Tuple[int, int]],
        method: str = "GET",
        stream: bool = False,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Makes an HTTP request to the specified URL with the given parameters.

        Args:
            session: The requests Session object to use for the request.
            url: The URL to make the request to.
            headers: The headers to include in the request.
            json_data: The JSON data to include in the request body.
            timeout: The request timeout in seconds or tuple of (connect, read) timeouts.
            method: HTTP method to use ("GET" or "POST", defaults to "GET").
            stream: Whether to stream the response (POST only).

        Returns:
            If stream=False, returns the parsed JSON response (Dict/List) or an error dict.
            If stream=True, returns a generator yielding parsed JSON objects from the streaming response.

        Raises:
            requests.exceptions.Timeout: If the request times out.
            requests.exceptions.RequestException: For other request-related errors.
            ValueError: If an unsupported HTTP method is specified or stream=True for GET.
        """
        method = method.upper()
        if method not in ["GET", "POST"]:
            raise ValueError(
                f"Unsupported HTTP method: {method}. Supported methods are GET and POST."
            )
        if stream and method != "POST":
            raise ValueError("Streaming is only supported for POST requests.")

        # Convert timeout to tuple if necessary
        if isinstance(timeout, int):
            timeout = (timeout, timeout)

        # Add Accept-Encoding header if not present
        request_headers = headers.copy()
        if 'Accept-Encoding' not in request_headers:
             request_headers['Accept-Encoding'] = 'gzip'

        # Call the internal method that handles execution and retries
        return RequestsManager._execute_request_with_retry(
            session=session,
            url=url,
            headers=request_headers, # Use updated headers
            json_data=json_data,
            timeout=timeout,
            method=method,
            stream=stream,
        )

    @staticmethod
    @retry(
        wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3)
    )
    def _execute_request_with_retry(
        session: requests.Session,
        url: str,
        headers: Dict[str, str],
        json_data: Dict[str, Any],
        timeout: Tuple[int, int],
        method: str,
        stream: bool,
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """Internal method to execute the request with retry logic and handle response."""
        try:
            response: requests.Response
            if stream:
                # Streaming only supported for POST
                response = session.post(
                    url, headers=headers, json=json_data, timeout=timeout, stream=True
                )
                response.raise_for_status() # Check for HTTP errors before streaming

                def generate_stream():
                    # Gzip handled automatically by requests for streaming if header present
                    for line in response.iter_lines():
                        if line:
                            line_str = line.decode("utf-8")
                            if line_str.startswith("data:") and "data: [DONE]" not in line_str:
                                json_str = line_str[5:].strip()
                                if json_str:
                                    try:
                                        yield json.loads(json_str)
                                    except json.JSONDecodeError as e:
                                        logging.error(
                                            f"Error decoding JSON stream line: {e}, line: {json_str}"
                                        )
                                        # Optionally yield an error dict or skip
                                        # yield {'error': 'JSONDecodeError', 'line': json_str}
                            elif line_str.strip(): # Log non-data lines if needed
                                logging.debug(f"Received non-data line: {line_str}")


                return generate_stream()
            else:
                # Normal (non-streaming) responses
                if method == "GET":
                    response = session.get(
                        url, headers=headers, params=json_data, timeout=timeout
                    )
                elif method == "POST":
                    response = session.post(
                        url, headers=headers, json=json_data, timeout=timeout
                    )
                # No else needed as method is validated

                response.raise_for_status() # Check for HTTP errors

                # Handle content (Gzip auto-handled by requests if header present)
                try:
                    # Try parsing directly with response.json() first
                    return response.json()
                except json.JSONDecodeError as e1:
                    logging.warning(f"Failed to parse response with response.json(): {e1}. Trying json.loads(response.text).")
                    try:
                        # Fallback: try parsing response.text
                        # response.text handles decoding based on headers/chardet
                        return json.loads(response.text)
                    except json.JSONDecodeError as e2:
                        logging.error(f"Failed to parse response as JSON with json.loads: {e2}")
                        return {
                            'content': response.text, # Return decoded text
                            'message': f"Failed to parse response as JSON: {e2}"
                        }

        except requests.exceptions.Timeout as e:
            logging.error(f"{method} request to {url} timed out after {timeout}s: {e}")
            raise requests.exceptions.Timeout(
                f"Request to {url} timed out after {timeout} seconds"
            ) from e
        except requests.exceptions.HTTPError as e:
             # Handle HTTP errors (4xx, 5xx) specifically for non-streaming
             # For streaming, raise_for_status is called before generator creation
            logging.error(f"HTTP Error {e.response.status_code} for {method} {url}: {e.response.text[:200]}...")
            # Attempt to parse error response as JSON
            try:
                return e.response.json()
            except json.JSONDecodeError:
                 logging.warning("Could not parse HTTP error response as JSON.")
                 # Return dict with error details if JSON parsing fails
                 return {
                     'content': e.response.text,
                     'message': f"HTTP Error: {e.response.status_code}",
                     'status_code': e.response.status_code
                 }
        except requests.exceptions.RequestException as e:
            error_msg = f"RequestException for {method} {url}: {str(e)}"
            logging.error(error_msg)
            raise requests.exceptions.RequestException(error_msg) from e
        except Exception as e:
            # Catch any other unexpected errors
            logging.exception(f"Unexpected error during request {method} {url}: {e}")
            raise
