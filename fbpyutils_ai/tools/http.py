import json
import httpx
import logging
import requests
from time import perf_counter
from requests.adapters import HTTPAdapter
from typing import Any, Optional, Dict, Union, Generator, List, Tuple
from tenacity import retry, wait_random_exponential, stop_after_attempt


class HTTPClient:
    """HTTP Client for synchronous and asynchronous requests.

    Supports GET, POST, PUT, and DELETE methods.
    Includes streaming response capability.

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
            raise ValueError("base_url deve incluir protocolo (http/https)")

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
        logging.info(f"HTTPClient inicializado para {self.base_url}")

    async def async_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        stream: bool = False,
    ) -> Union[Dict, List, httpx.Response]:
        """Executes an asynchronous HTTP request.

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE).
            endpoint (str): Endpoint relative to base_url.
            params (Optional[Dict]): Query parameters (optional).
            data (Optional[Dict]): Data for form-urlencoded body (optional).
            json (Optional[Dict]): Data for JSON body (optional).
            stream (bool): If True, returns the response object for streaming consumption (default: False).

        Returns:
            Union[Dict, List, httpx.Response]: Parsed JSON response if stream=False, httpx.Response object for streaming if stream=True.

        Raises:
            httpx.HTTPStatusError: For 4xx/5xx status codes.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = perf_counter()

        logging.debug(f"Starting asynchronous request: {method} {url}") # Docstring em inglês
        logging.info(
            f"Params: {params} | Data: {data} | JSON: {json} | Stream: {stream}"
        )  # Log atualizado para incluir stream

        try:
            response = await self._async_client.request(
                method=method, url=url, params=params, data=data, json=json, stream=stream
            )
            response.raise_for_status()

            # Log de métricas de desempenho
            duration = perf_counter() - start_time
            logging.debug(
                f"Asynchronous request completed in {duration:.2f}s | " # Docstring em inglês
                f"Size: {len(response.content)} bytes | Stream: {stream}" # Log atualizado para incluir stream
            )

            return response.json() if not stream else response

        except httpx.HTTPStatusError as e:
            logging.error(
                f"Error {e.response.status_code} in {method} {url}: " # Docstring em inglês
                f"{e.response.text[:200]}..."
            )
            raise
        finally:
            logging.debug(f"Processing of {method} {url} finished") # Docstring em inglês

    def sync_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        stream: bool = False,
    ) -> Union[Dict, List, httpx.Response]:
        """Executes a synchronous HTTP request.

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE).
            endpoint (str): Endpoint relative to base_url.
            params (Optional[Dict]): Query parameters (optional).
            data (Optional[Dict]): Data for form-urlencoded body (optional).
            json (Optional[Dict]): Data for JSON body (optional).
            stream (bool): If True, returns the response object for streaming consumption (default: False).

        Returns:
            Union[Dict, List, httpx.Response]: Parsed JSON response if stream=False, httpx.Response object for streaming if stream=True.

        Raises:
            httpx.HTTPStatusError: For 4xx/5xx status codes.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = perf_counter()

        logging.debug(f"Starting synchronous request: {method} {url}") # Docstring em inglês
        logging.info(
            f"Params: {params} | Data: {data} | JSON: {json} | Stream: {stream}"
        )  # Log atualizado para incluir stream

        try:
            # Usar httpx para requisições síncronas
            method_upper = method.upper()
            if method_upper == "GET":
                response = self._sync_client.get(url, params=params, stream=stream) # Adicionado stream=stream
            elif method_upper == "POST":
                response = self._sync_client.post(url, json=json, stream=stream) # Adicionado stream=stream
            elif method_upper == "PUT":
                response = self._sync_client.put(url, json=json, stream=stream) # Adicionado stream=stream
            elif method_upper == "DELETE":
                response = self._sync_client.delete(url, json=json, stream=stream) # Adicionado stream=stream
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            response.raise_for_status()

            duration = perf_counter() - start_time
            logging.debug(
                f"Synchronous request completed in {duration:.2f}s | " # Docstring em inglês
                f"Size: {len(response.content)} bytes | Stream: {stream}" # Log atualizado para incluir stream
            )

            return response.json() if not stream else response # Retornar response se stream=True

        except httpx.HTTPError as e:  # Capturar exceções de httpx
            logging.exception(
                f"Error in synchronous request {method} {url}: {e}"  # Mensagem de erro mais genérica # Docstring em inglês
            )
            raise
        finally:
            logging.debug(f"Processing of {method} {url} finished") # Docstring em inglês

    def __enter__(self):
        """Suporte para gerenciamento de contexto síncrono."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Garante fechamento adequado do cliente síncrono."""
        self._sync_client.close()

    async def __aenter__(self):
        """Suporte para gerenciamento de contexto assíncrono."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Garante fechamento adequado do cliente assíncrono."""
        await self._async_client.aclose()


# HTTP Request manager for API calls
class RequestsManager:
    """
    A utility class for making HTTP requests with retry logic and error handling.
    
    This class provides a common interface for making HTTP requests to external APIs,
    handling common error scenarios, and supporting both streaming and non-streaming responses.
    
    Features:
    - Support for both GET and POST HTTP methods
    - Streaming response handling (POST only)
    - Automatic retry with exponential backoff
    - JSON response parsing
    - Comprehensive error handling and logging
    - Centralized HTTP session management
    
    The class is primarily designed for interacting with LLM APIs like OpenAI but can be
    used for any service that requires HTTP requests with JSON responses.
    """
    
    @staticmethod
    def create_session(max_retries: int = 2, auth: Optional[Tuple[str, str]] = None,
                      bearer_token: Optional[str] = None, verify_ssl: Union[bool, str] = True) -> requests.Session:
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
    def request(url: str, headers: Dict[str, str], json_data: Dict[str, Any],
                timeout: Union[int, Tuple[int, int]] = (30, 30), method: str = "GET",
                stream: bool = False, max_retries: int = 2, auth: Optional[Tuple[str, str]] = None,
                bearer_token: Optional[str] = None, verify_ssl: Union[bool, str] = True
               ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Convenience method that creates a session and makes a request in one call.
        
        Args:
            url: The URL to make the request to
            headers: The headers to include in the request
            json_data: The JSON data to include in the request body
            timeout: The request timeout in seconds or tuple of (connect, read) timeouts
            method: HTTP method to use ("GET", "POST", "PUT" or "DELETE", defaults to "GET")
            stream: Whether to stream the response
            max_retries: Maximum number of retries for the session adapter
            auth: Tuple of (username, password) for basic authentication
            bearer_token: Bearer token for authentication
            verify_ssl: Verify SSL certificate (True/False or path to CA bundle)
            
        Returns:
            If stream=False, returns the JSON response as a dictionary.
            If stream=True, returns a generator yielding parsed JSON objects from the streaming response.
        """
        session = RequestsManager.create_session(
            max_retries=max_retries,
            auth=auth,
            bearer_token=bearer_token,
            verify_ssl=verify_ssl
        )
        return RequestsManager.make_request(
            session=session,
            url=url,
            headers=headers,
            json_data=json_data,
            timeout=timeout,
            method=method,
            stream=stream
        )
    
    @staticmethod
    @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
    def make_request(session: requests.Session, url: str, headers: Dict[str, str],
                    json_data: Dict[str, Any], timeout: Union[int, Tuple[int, int]],
                    method: str = "GET", stream: bool = False
                   ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Makes an HTTP request to the specified URL with the given parameters.
        
        Args:
            session: The requests Session object to use for the request
            url: The URL to make the request to
            headers: The headers to include in the request
            json_data: The JSON data to include in the request body
            timeout: The request timeout in seconds or tuple of (connect, read) timeouts
            method: HTTP method to use ("GET", "POST", "PUT" or "DELETE", defaults to "GET")
            stream: Whether to stream the response
            
        Returns:
            If stream=False, returns the JSON response as a dictionary.
            If stream=True, returns a generator yielding parsed JSON objects from the streaming response.
            
        Raises:
            requests.exceptions.Timeout: If the request times out
            requests.exceptions.RequestException: For other request-related errors
            ValueError: If an unsupported HTTP method is specified
        """
        # Validate HTTP method
        method = method.upper()
        if method not in ["GET", "POST", "PUT", "DELETE"]:
            raise ValueError(f"Unsupported HTTP method: {method}. Supported methods are GET, POST, PUT and DELETE.")
            
        # Convert timeout to tuple if necessary
        if isinstance(timeout, int):
            timeout = (timeout, timeout)
            
        try:
            if stream:
                # For streaming responses (only supported with POST)
                if method != "POST":
                    logging.warning(f"Streaming is only supported with POST method. Switching from {method} to POST.")
                    method = "POST"
                
                response = session.post(url, headers=headers, json=json_data, timeout=timeout, stream=True)
                response.raise_for_status()
                
                def generate_stream():
                    for line in response.iter_lines():
                        if line:
                            line = line.decode('utf-8')
                            # OpenAI-style streaming sends 'data: [DONE]' to signal the end of the stream
                            if line.startswith('data:') and not 'data: [DONE]' in line:
                                json_str = line[5:].strip()
                                if json_str:
                                    try:
                                        yield json.loads(json_str)
                                    except json.JSONDecodeError as e:
                                        logging.error(f"Error decoding JSON: {e}, line: {json_str}")
                
                return generate_stream()
            else:
                # For normal (non-streaming) responses
                if method == "GET":
                    response = session.get(url, headers=headers, params=json_data, timeout=timeout)
                elif method == "POST":
                    response = session.post(url, headers=headers, json=json_data, timeout=timeout)
                elif method == "PUT":
                    response = session.put(url, headers=headers, json=json_data, timeout=timeout)
                elif method == "DELETE":
                    response = session.delete(url, headers=headers, json=json_data, timeout=timeout)
                
                response.raise_for_status()
                return response.json()
        except requests.exceptions.Timeout as e:
            logging.error(f"{method} request timed out: {e}")
            raise requests.exceptions.Timeout(f"Request to {url} timed out after {timeout} seconds") from e
        except requests.exceptions.RequestException as e:
            error_msg = f"{method} request to {url} failed: {str(e)}"
            logging.error(error_msg)
            raise requests.exceptions.RequestException(error_msg) from e