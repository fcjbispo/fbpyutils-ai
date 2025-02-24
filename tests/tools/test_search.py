import os
from typing import Dict, Optional, Union, List, Tuple
import logging

import httpx
from fbpyutils_ai import logging
from fbpyutils_ai.tools import HTTPClient
import pandas as pd


class SearXNGUtils:
    # ... (rest of the class remains the same)


class SearXNGTool:
    # ... (rest of the class remains the same)

    def search(
        self,
        query: str,
        method: str = "GET",
        categories: Optional[Union[str, List[str]]] = ["general"],
        language: str = "auto",
        time_range: str = None,
        safesearch: int = SAFESEARCH_NONE
    ) -> List[Dict]:
        """Realiza uma busca síncrona no SearXNG.

        Args:
            query (str): Termo de busca.
            method (str, optional): Método HTTP para a requisição ('GET' ou 'POST'). Padrão é 'GET'.
            categories (Optional[Union[str, List[str]]], optional): Categorias de busca (e.g., 'general', 'images', 'news').
                Pode ser uma string ou uma lista de strings. Padrão é ['general'].
            language (str, optional): Idioma da busca (código ISO 639-1, e.g., 'en', 'pt', 'es'). Padrão é 'auto'.
            time_range (str, optional): Intervalo de tempo para a busca (e.g., 'day', 'week', 'month', 'year'). Padrão é None.
            safesearch (int, optional): Nível de segurança para a busca.
                Use as constantes SAFESEARCH_NONE, SAFESEARCH_MODERATE ou SAFESEARCH_STRICT. Padrão é SAFESEARCH_NONE.

        Returns:
            List[Dict]: Lista de resultados da busca, onde cada resultado é um dicionário.
                      Retorna uma lista vazia em caso de erro na requisição.

        Raises:
            ValueError: Se o método HTTP for inválido, o idioma for inválido ou o nível de segurança for inválido.
            requests.exceptions.RequestException: Se ocorrer algum erro durante a requisição HTTP.
        """
        logging.info(f"Iniciando busca síncrona no SearXNG com query: '{query}'")
        self._validate_search_parameters(method, language, safesearch)
        params = self._prepare_search_params(query, categories, language, time_range, safesearch)
        url = f"{self.base_url}/search"

        try:
            response = self.http_client.sync_request(
                method=method, endpoint="search", params=params
            )
            results = response.get("results", [])
            logging.info(f"Busca síncrona no SearXNG para query: '{query}' completada com sucesso. Resultados encontrados: {len(results)}")
            return results
        except httpx.HTTPError as e:
            return self._handle_http_error(e)
        finally:
            logging.debug(f"Finalizando busca síncrona no SearXNG para query: '{query}'")

    async def async_search(
        self,
        query: str,
        method: str = "GET",
        categories: Optional[Union[str, List[str]]] = ["general"],
        language: str = "auto",
        time_range: str = None,
        safesearch: int = SAFESEARCH_NONE
    ) -> List[Dict]:
        """Realiza uma busca assíncrona no SearXNG.

        Args:
            query (str): Termo de busca.
            method (str, optional): Método HTTP para a requisição ('GET' ou 'POST'). Padrão é 'GET'.
            categories (Optional[Union[str, List[str]]], optional): Categorias de busca (e.g., 'general', 'images', 'news').
                Pode ser uma string ou uma lista de strings. Padrão é ['general'].
            language (str, optional): Idioma da busca (código ISO 639-1, e.g., 'en', 'pt', 'es'). Padrão é 'auto'.
            time_range (str, optional): Intervalo de tempo para a busca (e.g., 'day', 'week', 'month', 'year'). Padrão é None.
            safesearch (int, optional): Nível de segurança para a busca.
                Use as constantes SAFESEARCH_NONE, SAFESEARCH_MODERATE ou SAFESEARCH_STRICT. Padrão é SAFESEARCH_NONE.

        Returns:
            List[Dict]: Lista de resultados da busca, onde cada resultado é um dicionário.
                      Retorna uma lista vazia em caso de erro na requisição.

        Raises:
            ValueError: Se o método HTTP for inválido, o idioma for inválido ou o nível de segurança for inválido.
            httpx.HTTPError: Se ocorrer algum erro durante a requisição HTTP.
        """
        logging.info(f"Iniciando busca assíncrona no SearXNG com query: '{query}'")
        self._validate_search_parameters(method, language, safesearch)
        params = self._prepare_search_params(query, categories, language, time_range, safesearch)
        url = f"{self.base_url}/search"

        try:
            response = await self.http_client.async_request(
                method=method, endpoint="search", params=params
            )
            results = response.get("results", [])
            logging.info(f"Busca assíncrona no SearXNG para query: '{query}' completada com sucesso. Resultados encontrados: {len(results)}")
            return results
        except httpx.HTTPError as e:
            return self._handle_http_error(e)
        finally:
            logging.debug(f"Finalizando busca assíncrona no SearXNG para query: '{query}'")
