import json
import httpx
import logging
import requests
import random
from time import perf_counter
from requests.adapters import HTTPAdapter
from typing import Any, Optional, Dict, Union, Generator, List, Tuple, AsyncGenerator
from tenacity import retry, wait_random_exponential, stop_after_attempt


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
]


def basic_header(random_user_agent: bool = False) -> Dict[str, str]:
    """
    Returns a basic HTTP header with a suitable agent identification and content type JSON.

    Args:
        random_user_agent (bool): If True, a random user agent will be used. Defaults to False.
    """
    user_agent = random.choice(USER_AGENTS) if random_user_agent else USER_AGENTS[0]
    return {
        "User-Agent": user_agent,
        "Content-Type": "application/json"
    }

class HTTPClient:
    """HTTP Client for synchronous and asynchronous requests.

    Supports GET, POST, PUT, and DELETE methods.
    Includes streaming response capability.
    Methods return the raw httpx.Response object, allowing the caller to
    handle content parsing (e.g., response.json(), response.text, response.content)
    and streaming (e.g., async for data in response.aiter_bytes()).

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

    async def async_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        stream: bool = False,
    ) -> httpx.Response:
        """Executes an asynchronous HTTP request.

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE).
            endpoint (str): Endpoint relative to base_url.
            params (Optional[Dict]): Query parameters (optional).
            data (Optional[Dict]): Data for form-urlencoded body (optional).
            json (Optional[Dict]): Data for JSON body (optional).
            stream (bool): If True, returns the response object for streaming consumption (default: False).

        Returns:
            httpx.Response: The raw httpx.Response object. The caller is responsible
                            for processing the response (e.g., calling response.json(),
                            response.text, or iterating over response.aiter_bytes()).

        Raises:
            httpx.HTTPStatusError: For 4xx/5xx status codes.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = perf_counter()

        logging.debug(f"Starting asynchronous request: {method} {url}")
        logging.info(
            f"Params: {params} | Data: {data} | JSON: {json} | Stream: {stream}"
        )  # Log atualizado para incluir stream

        try:
            # Use métodos específicos (get, post, etc.) que aceitam 'stream'
            method_upper = method.upper()
            response: httpx.Response # Type hint

            if method_upper == "GET":
                response = await self._async_client.get(url, params=params) # Não passar stream aqui diretamente, httpx lida com isso
            elif method_upper == "POST":
                response = await self._async_client.post(url, params=params, data=data, json=json) # Não passar stream aqui diretamente
            elif method_upper == "PUT":
                response = await self._async_client.put(url, params=params, data=data, json=json) # Não passar stream aqui diretamente
            elif method_upper == "DELETE":
                response = await self._async_client.delete(url, params=params, data=data, json=json) # Não passar stream aqui diretamente
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status() 

            # Log de métricas de desempenho
            duration = perf_counter() - start_time
            # Determinar o tamanho do conteúdo de forma segura
            # Determinar o tamanho do conteúdo de forma segura, evitando acessar .content em streams
            content_length_info = "N/A (streaming)" if stream else response.headers.get("content-length", "N/A")
            if not stream and response.is_closed and hasattr(response, "_content"):
                 content_length_info = f"{len(response._content)} bytes"
            elif not stream and not response.is_closed:
                 content_length_info = "N/A (content not read by client method)"

            logging.debug(
                f"Asynchronous request completed in {duration:.2f}s | "
                f"Content-Length: {content_length_info} | Stream: {stream}"
            )

            if stream:
                # Para stream=True, retorne o objeto de resposta para o chamador iterar
                # O chamador é responsável por ler o stream (ex: response.aiter_bytes())
                return response 
            else:
                # For stream=False, return the raw response object
                return response

        except httpx.HTTPStatusError as e:
            logging.error(
                f"Error {e.response.status_code} in {method} {url}: "
                f"{e.response.text[:200]}..."
            )
            raise
        finally:
            logging.debug(f"Processing of {method} {url} finished")

    def sync_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        stream: bool = False,
    ) -> httpx.Response:
        """Executes a synchronous HTTP request.

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE).
            endpoint (str): Endpoint relative to base_url.
            params (Optional[Dict]): Query parameters (optional).
            data (Optional[Dict]): Data for form-urlencoded body (optional).
            json (Optional[Dict]): Data for JSON body (optional).
            stream (bool): If True, returns the response object for streaming consumption (default: False).

        Returns:
            httpx.Response: The raw httpx.Response object. The caller is responsible
                            for processing the response (e.g., calling response.json(),
                            response.text, or iterating over response.iter_bytes()).

        Raises:
            httpx.HTTPStatusError: For 4xx/5xx status codes.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = perf_counter()

        logging.debug(f"Starting synchronous request: {method} {url}")
        logging.info(
            f"Params: {params} | Data: {data} | JSON: {json} | Stream: {stream}"
        )  # Log atualizado para incluir stream

        try:
            # Usar httpx para requisições síncronas
            method_upper = method.upper()
            if method_upper == "GET":
                response = self._sync_client.get(url, params=params)
            elif method_upper == "POST":
                response = self._sync_client.post(url, json=json)
            elif method_upper == "PUT":
                response = self._sync_client.put(url, json=json)
            elif method_upper == "DELETE":
                response = self._sync_client.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            response.raise_for_status() 

            duration = perf_counter() - start_time
            logging.debug(
                f"Synchronous request completed in {duration:.2f}s | "
                f"Size: {'N/A (streaming)' if stream else f'{len(response.content)} bytes'} | Stream: {stream}"
            )

            # Return the raw response object
            return response

        except httpx.HTTPError as e:  # Capturar exceções de httpx
            logging.exception(
                f"Error in synchronous request {method} {url}: {e}"  # Generic error message
            )
            raise
        finally:
            logging.debug(f"Processing of {method} {url} finished")

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
               ) -> requests.Response:
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
            requests.Response: The raw requests.Response object. The caller is responsible
                               for processing the response (e.g., calling response.json(),
                               response.text, or iterating over response.iter_lines() or
                               response.iter_content()).
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
    # @retry decorator removed from here and moved to the internal method
    def make_request(session: requests.Session, url: str, headers: Dict[str, str],
                    json_data: Dict[str, Any], timeout: Union[int, Tuple[int, int]],
                    method: str = "GET", stream: bool = False
                   ) -> requests.Response:
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
            requests.Response: The raw requests.Response object. The caller is responsible
                               for processing the response (e.g., calling response.json(),
                               response.text, or iterating over response.iter_lines() or
                               response.iter_content()).

        Raises:
            requests.exceptions.Timeout: If the request times out
            requests.exceptions.RequestException: For other request-related errors
            ValueError: If an unsupported HTTP method is specified
        """
        # Validate HTTP method
        method = method.upper()
        if method not in ["GET", "POST", "PUT", "DELETE"]:
            raise ValueError(f"Unsupported HTTP method: {method}. Supported methods are GET, POST, PUT and DELETE.")
            if stream and method != "POST":
                 if stream and method != "POST":
                      raise ValueError("Streaming is only supported for POST requests in RequestsManager.")

        # Convert timeout to tuple if necessary
        if isinstance(timeout, int):
            timeout = (timeout, timeout)

        # Call the internal method that handles execution and retries
        return RequestsManager._execute_request_with_retry(
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
    def _execute_request_with_retry(session: requests.Session, url: str, headers: Dict[str, str],
                                   json_data: Dict[str, Any], timeout: Tuple[int, int],
                                   method: str, stream: bool
                                  ) -> requests.Response:
        """Internal method to execute the request with retry logic."""
        try:
            if stream:
                # For streaming responses (ensure method is POST as validated in make_request)
                # Note: The check and warning for non-POST stream is now in make_request logic,
                # but we ensure method is POST here if stream is True.
                if method != "POST":
                     # This case might occur if called directly, enforce POST for stream
                     logging.warning(f"Internal: Streaming requires POST. Overriding method {method} to POST.")
                     method = "POST"

                response = session.post(url, headers=headers, json=json_data, timeout=timeout, stream=True)
                response.raise_for_status() 

                # For streaming responses, return the raw response object
                # The caller is responsible for iterating over response.iter_lines() or response.iter_content()
                return response
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
                # No else needed here as method is validated in make_request

                response.raise_for_status() 
                # Return the raw response object
                return response
        except requests.exceptions.Timeout as e:
            logging.error(f"{method} request timed out: {e}")
            raise requests.exceptions.Timeout(f"Request to {url} timed out after {timeout} seconds") from e
        except requests.exceptions.RequestException as e:
            error_msg = f"{method} request to {url} failed: {str(e)}"
            logging.error(error_msg)
            raise requests.exceptions.RequestException(error_msg) from e
