import json
import httpx
import logging
import requests
import random
from time import perf_counter
from requests.adapters import HTTPAdapter
from typing import Any, Optional, Dict, Union, Generator, List, Tuple
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
    user_agent = random.choice(USER_AGENTS) if random_user_agent else "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0"
    return {
        "User-Agent": user_agent,
        "Content-Type": "application/json"
    }

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
            content_length = 'N/A (streaming)' if stream else len(response.content)
            logging.debug(
                f"Asynchronous request completed in {duration:.2f}s | "
                f"Size: {content_length} | Stream: {stream}"
            )

            if stream:
                # Para stream=True, retorne o objeto de resposta para o chamador iterar
                # O chamador é responsável por ler o stream (ex: response.aiter_bytes())
                return response
            else:
                # Para stream=False, leia o corpo e retorne o JSON
                # A chamada a .json() já lê o corpo se necessário
                return response.json()

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

            return response.json() if not stream else response # Retornar response se stream=True

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
    # @retry decorator removed from here and moved to the internal method
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
                                  ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
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

                def generate_stream():
                    for line in response.iter_lines():
                        if line:
                            line = line.decode('utf-8')
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
                # No else needed here as method is validated in make_request

                response.raise_for_status()
                return response.json()
        except requests.exceptions.Timeout as e:
            logging.error(f"{method} request timed out: {e}")
            raise requests.exceptions.Timeout(f"Request to {url} timed out after {timeout} seconds") from e
        except requests.exceptions.RequestException as e:
            error_msg = f"{method} request to {url} failed: {str(e)}"
            logging.error(error_msg)
            raise requests.exceptions.RequestException(error_msg) from e
