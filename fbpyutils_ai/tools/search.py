import os
from typing import Dict, Optional, Union, List
import logging

import httpx
from fbpyutils_ai import logging
from fbpyutils_ai.tools import HTTPClient  # Importando HTTPClient
import pandas as pd


class SearXNGUtils:
    """Utilitários para processamento de resultados do SearXNG."""

    @staticmethod
    def simplify_results(
        results: List[Dict[str, Union[str, int, float, bool, None]]]
    ) -> List[Dict[str, Union[str, int, float, bool, None]]]:
        """Simplifica a lista de resultados, extraindo campos principais.

        Args:
            results (List[Dict[str, Union[str, int, float, bool, None]]]): Lista de resultados brutos do SearXNG.

        Returns:
            List[Dict[str, Union[str, int, float, bool, None]]]: Lista de resultados simplificados,
            contendo 'url', 'title', 'content', 'score', 'publishedDate' e 'other_info'.
        """
        logging.debug("Entrando em simplify_results")
        simplified_results = []
        if results:
            key_columns = ["url", "title", "content", "score", "publishedDate"]
            for result in results:
                result_record = {}
                for key in key_columns:
                    result_record[key] = result.get(key)
                other_keys = [k for k in result.keys() if k not in key_columns]
                result_record["other_info"] = {k: result[k] for k in other_keys}
                simplified_results.append(result_record)
        logging.debug("Saindo de simplify_results")
        return simplified_results

    @staticmethod
    def convert_to_dataframe(
        results: List[Dict[str, Union[str, int, float, bool, None]]]
    ) -> pd.DataFrame:
        """Converte a lista de resultados do SearXNG em um DataFrame do pandas.

        Args:
            results (List[Dict[str, Union[str, int, float, bool, None]]]): Lista de resultados do SearXNG.

        Returns:
            pd.DataFrame: DataFrame contendo os resultados da busca, com colunas 'url', 'title', 'content', 'score', 'publishedDate' e 'other_info'.
        """
        logging.debug("Entrando em convert_to_dataframe")
        df = pd.DataFrame(columns=["url", "title", "content", "score", "publishedDate", "other_info"])
        if results:
            results_list = SearXNGUtils.simplify_results(results)
            df = pd.DataFrame.from_dict(results_list, orient="columns")
        logging.debug("Saindo de convert_to_dataframe")
        return df


class SearXNGTool:
    """
    Ferramenta para busca usando a API REST do SearXNG.

    Integração com a API do SearXNG para realizar buscas programáticas.
    Suporta diferentes categorias de busca, idiomas e níveis de segurança.
    """

    SAFESEARCH_NONE = 0
    SAFESEARCH_MODERATE = 1
    SAFESEARCH_STRICT = 2

    CATEGORIES = (
        "general",
        "images",
        "videos",
        "news",
        "map",
        "music",
        "it",
        "science",
        "files",
        "social media",
    )

    LANGUAGES = (
        "auto",
        "en",
        "pt",
        "es",
        "fr",
        "de",
        "it",
        "ru",
        "nl",
        "pd",
        "vi",
        "id",
        "ar",
        "th",
        "zh-cn",
        "ja",
        "ko",
        "tr",
        "cs",
        "da",
        "fi",
        "hu",
        "no",
        "sv",
        "uk",
    )

    def __init__(self, base_url: str = None, api_key: str = None, verify_ssl: bool = False):
        """Inicializa a ferramenta SearXNGTool.

        Args:
            base_url (str, optional): URL base da API do SearXNG.
                Se não fornecido, usa a variável de ambiente 'FBPY_SEARXNG_BASE_URL' ou 'https://searxng.site' como padrão.
            api_key (str, optional): Chave de API para autenticação no SearXNG.
                Se não fornecida, usa a variável de ambiente 'SEARXNG_API_KEY'.
            verify_ssl (bool, optional): Verifica o certificado SSL da URL base.
                Padrão é False.
        """
        logging.info("Inicializando SearXNGTool")
        self.base_url = base_url or os.getenv(
            "FBPY_SEARXNG_BASE_URL", "https://searxng.site"
        )
        self.api_key = api_key or os.getenv("FBPY_SEARXNG_API_KEY", None)
        self.verify_ssl = (verify_ssl and 'https://' in self.base_url)
        self.http_client = HTTPClient(base_url=self.base_url, headers=self._build_headers(), verify_ssl=self.verify_ssl)  # Inicializa HTTPClient com headers
        logging.info(
            f"SearXNGTool inicializado com base_url={self.base_url}, api_key={'PROVIDED' if self.api_key else 'NOT PROVIDED'} and verify_ssl={self.verify_ssl}"
        )

    def _build_headers(self) -> Dict[str, str]:
        """Constrói os cabeçalhos HTTP padrão para as requisições."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _validate_search_parameters(
        self, method: str, language: str, safesearch: int
    ) -> None:
        """Valida os parâmetros de busca."""
        if method not in ("GET", "POST"):
            logging.error(f"Método HTTP inválido: {method}")
            raise ValueError(f"Método inválido: {method}. Use 'GET' ou 'POST'.")
        if language not in self.LANGUAGES and language != "auto":
            logging.error(f"Idioma inválido: {language}")
            raise ValueError(
                f"Idioma inválido: {language}. Use 'auto' ou um código ISO 639-1 válido."
            )
        if safesearch not in (
            self.SAFESEARCH_NONE,
            self.SAFESEARCH_MODERATE,
            self.SAFESEARCH_STRICT,
        ):
            logging.error(f"Nível de segurança inválido: {safesearch}")
            raise ValueError(
                f"Nível de segurança inválido: {safesearch}. Use 'SAFESEARCH_NONE|0', 'SAFESEARCH_MODERATE|1' ou 'SAFESEARCH_STRICT|2'."
            )

    def _prepare_search_params(
        self, query: str, categories: Optional[Union[str, List[str]]], language: str, time_range: str, safesearch: int
    ) -> Dict:
        """Prepara os parâmetros da requisição de busca."""
        params = {
            "q": query,
            "format": "json",
            "language": language,
            "safesearch": safesearch,
            "time_range": time_range,
            "pageno": 1,  # Página inicial de resultados
        }
        if not categories:
            categories = ["general"]
        for category in categories:
            if category.lower() in self.CATEGORIES:
                params[f"category_{category.lower()}"] = 1
        logging.debug(f"Parâmetros da requisição definidos: {params}")
        return params

    def _handle_http_error(self, e: Exception) -> List[Dict]:
        """Loga o erro HTTP e retorna uma lista vazia."""
        logging.error(f"Erro na requisição ao SearXNG: {e}")
        return []

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
