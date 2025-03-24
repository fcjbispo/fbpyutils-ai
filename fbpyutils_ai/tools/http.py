import json
import httpx
import logging
import requests
from time import perf_counter
from requests.adapters import HTTPAdapter
from typing import Any, Optional, Dict, Union, Generator
from tenacity import retry, wait_random_exponential, stop_after_attempt


class HTTPClient:
    """Cliente HTTP para requisições síncronas e assíncronas.

    Attributes:
        base_url (str): URL base para todas as requisições
        headers (Dict): Cabeçalhos HTTP padrão

    Examples:
        >>> client = HTTPClient(base_url="https://api.example.com")
        >>> # Requisição síncrona
        >>> response = client.sync_request("GET", "data")
        >>> # Requisição assíncrona
        >>> import asyncio
        >>> async def main():
        ...     return await client.async_request("GET", "data")
        >>> asyncio.run(main())
    """

    def __init__(
        self, base_url: str, headers: Optional[Dict] = None, verify_ssl: bool = True
    ):
        """Inicializa o cliente HTTP com configurações básicas.

        Args:
            base_url: URL base para as requisições (deve incluir protocolo)
            headers: Cabeçalhos padrão para todas as requisições
            verify_ssl: Verificar certificado SSL (padrão: True)

        Raises:
            ValueError: Se a base_url não for válida
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
    ) -> Any:
        """Executa uma requisição HTTP assíncrona.

        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint relativo à base_url
            params: Parâmetros de query (opcional)
            data: Dados para form-urlencoded (opcional)
            json: Dados para JSON body (opcional)

        Returns:
            dict ou list: Resposta parseada como JSON

        Raises:
            httpx.HTTPStatusError: Para códigos de status 4xx/5xx

        Examples:
            >>> async def get_data():
            ...     async with HTTPClient("https://api.example.com") as client:
            ...         return await client.async_request("GET", "data")
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = perf_counter()

        logging.debug(f"Iniciando requisição assíncrona: {method} {url}")
        logging.info(
            f"Params: {params} | Data: {data} | JSON: {json}"
        )  # Log atualizado

        try:
            response = await self._async_client.request(
                method=method, url=url, params=params, data=data, json=json
            )
            response.raise_for_status()

            # Log de métricas de desempenho
            duration = perf_counter() - start_time
            logging.debug(
                f"Requisição assíncrona concluída em {duration:.2f}s | "
                f"Tamanho: {len(response.content)} bytes"
            )

            return response.json()

        except httpx.HTTPStatusError as e:
            logging.error(
                f"Erro {e.response.status_code} em {method} {url}: "
                f"{e.response.text[:200]}..."
            )
            raise
        finally:
            logging.debug(f"Finalizado processamento de {method} {url}")

    def sync_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
    ) -> Any:
        """Executa uma requisição HTTP síncrona.

        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint relativo à base_url
            params: Parâmetros de query (opcional)
            data: Dados para form-urlencoded (opcional)
            json: Dados para JSON body (opcional)

        Returns:
            dict ou list: Resposta parseada como JSON

        Raises:
            httpx.HTTPStatusError: Para códigos de status 4xx/5xx

        Examples:
            >>> client = HTTPClient("https://api.example.com")
            >>> response = client.sync_request("GET", "data")
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = perf_counter()

        logging.debug(f"Iniciando requisição síncrona: {method} {url}")
        logging.info(
            f"Params: {params} | Data: {data} | JSON: {json}"
        )  # Log atualizado

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
                response = self._sync_client.delete(url, json=json)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            response.raise_for_status()

            duration = perf_counter() - start_time
            logging.debug(
                f"Requisição síncrona concluída em {duration:.2f}s | "
                f"Tamanho: {len(response.content)} bytes"
            )

            return response.json()

        except httpx.HTTPError as e:  # Capturar exceções de httpx
            logging.exception(
                f"Erro na requisição síncrona {method} {url}: {e}"  # Mensagem de erro mais genérica
            )
            raise
        finally:
            logging.debug(f"Finalizado processamento de {method} {url}")

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
    def create_session(max_retries: int = 2) -> requests.Session:
        """
        Creates and configures a requests Session with retry capabilities.
        
        Args:
            max_retries: Maximum number of retries for the session adapter
            
        Returns:
            A configured requests.Session object
        """
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=max_retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
        
    @staticmethod
    def request(url: str, headers: Dict[str, str], json_data: Dict[str, Any], 
                timeout: int = 300, method: str = "GET", stream: bool = False, 
                max_retries: int = 2) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Convenience method that creates a session and makes a request in one call.
        
        Args:
            url: The URL to make the request to
            headers: The headers to include in the request
            json_data: The JSON data to include in the request body
            timeout: The request timeout in seconds
            method: HTTP method to use ("GET" or "POST", defaults to "GET")
            stream: Whether to stream the response
            max_retries: Maximum number of retries for the session adapter
            
        Returns:
            If stream=False, returns the JSON response as a dictionary.
            If stream=True, returns a generator yielding parsed JSON objects from the streaming response.
        """
        session = RequestsManager.create_session(max_retries=max_retries)
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
                    json_data: Dict[str, Any], timeout: int, method: str = "GET", 
                    stream: bool = False) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Makes an HTTP request to the specified URL with the given parameters.
        
        Args:
            session: The requests Session object to use for the request
            url: The URL to make the request to
            headers: The headers to include in the request
            json_data: The JSON data to include in the request body
            timeout: The request timeout in seconds
            method: HTTP method to use ("GET" or "POST", defaults to "GET")
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
        if method not in ["GET", "POST"]:
            raise ValueError(f"Unsupported HTTP method: {method}. Supported methods are GET and POST.")
            
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
                else:  # POST
                    response = session.post(url, headers=headers, json=json_data, timeout=timeout)
                
                response.raise_for_status()
                return response.json()
        except requests.exceptions.Timeout as e:
            logging.error(f"{method} request timed out: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logging.error(f"{method} request failed: {e}")
            raise