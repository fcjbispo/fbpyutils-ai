from typing import Any, Optional, Dict
import httpx
import logging
import requests  # Import requests para usar na sync_request
from time import perf_counter

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
    
    def __init__(self, base_url: str, headers: Optional[Dict] = None):
        """Inicializa o cliente HTTP com configurações básicas.
        
        Args:
            base_url: URL base para as requisições (deve incluir protocolo)
            headers: Cabeçalhos padrão para todas as requisições
            
        Raises:
            ValueError: Se a base_url não for válida
        """
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url deve incluir protocolo (http/https)")
            
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        
        # Configura clientes com timeout padrão e reutilização de conexão
        self._sync_client = httpx.Client(  # Usar httpx.Client para manter consistência
            headers=self.headers,
            timeout=httpx.Timeout(10.0)
        )
        self._async_client = httpx.AsyncClient(
            headers=self.headers,
            timeout=httpx.Timeout(10.0)
        )
        logging.info(f"HTTPClient inicializado para {self.base_url}")

    async def async_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        verify_ssl: bool = True  # Adicionado verify_ssl
    ) -> Any:
        """Executa uma requisição HTTP assíncrona.
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint relativo à base_url
            params: Parâmetros de query (opcional)
            data: Dados para form-urlencoded (opcional)
            json: Dados para JSON body (opcional)
            verify_ssl: Verificar certificado SSL (padrão: True) # Docstring atualizada
            
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
        logging.info(f"Params: {params} | Data: {data} | JSON: {json} | verify_ssl: {verify_ssl}") # Log atualizado

        try:
            response = await self._async_client.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                verify=verify_ssl # Correção: Usar verify_ssl como verify
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
        verify_ssl: bool = True  # Adicionado verify_ssl
    ) -> Any:
        """Executa uma requisição HTTP síncrona.
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint relativo à base_url
            params: Parâmetros de query (opcional)
            data: Dados para form-urlencoded (opcional)
            json: Dados para JSON body (opcional)
            verify_ssl: Verificar certificado SSL (padrão: True) # Docstring atualizada
            
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
        logging.info(f"Params: {params} | Data: {data} | JSON: {json} | verify_ssl: {verify_ssl}") # Log atualizado

        try:
            # Usar requests para requisições síncronas
            method_upper = method.upper()
            if method_upper == "GET":
                response = requests.get(url, params=params, headers=self.headers, verify=verify_ssl)
            elif method_upper == "POST":
                response = requests.post(url, params=params, headers=self.headers, json=json, verify=verify_ssl)
            elif method_upper == "PUT": # Adicionado suporte para PUT
                response = requests.put(url, params=params, headers=self.headers, json=json, verify=verify_ssl)
            elif method_upper == "DELETE": # Adicionado suporte para DELETE
                response = requests.delete(url, params=params, headers=self.headers, json=json, verify=verify_ssl)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            response.raise_for_status()
            
            # Log de métricas de desempenho
            duration = perf_counter() - start_time
            logging.debug(
                f"Requisição síncrona concluída em {duration:.2f}s | "
                f"Tamanho: {len(response.content)} bytes"
            )
            
            return response.json()
            
        except requests.exceptions.RequestException as e: # Capturar exceções de requests
            logging.error(
                f"Erro na requisição síncrona {method} {url}: {e}" # Mensagem de erro mais genérica
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
