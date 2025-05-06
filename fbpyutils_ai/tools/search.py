import os
from typing import Any, Dict, Optional, Union, List
import logging

import httpx
from fbpyutils_ai import logging
from fbpyutils_ai.tools.http import HTTPClient  # Importando HTTPClient
import pandas as pd


class SearXNGUtils:
    """Utilities for processing SearXNG results."""

    @staticmethod
    def simplify_results(
        results: List[Dict[str, Union[str, int, float, bool, None]]],
    ) -> List[Dict[str, Union[str, int, float, bool, None]]]:
        """Simplifies the results list, extracting main fields.

        Args:
            results (List[Dict[str, Union[str, int, float, bool, None]]]): List of raw SearXNG results.

        Returns:
            List[Dict[str, Union[str, int, float, bool, None]]]: Simplified list of results,
            containing 'url', 'title', 'content', 'score', 'publishedDate', and 'other_info'.
        """
        logging.debug("Entering simplify_results")
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
        logging.debug("Exiting simplify_results")
        return simplified_results

    @staticmethod
    def convert_to_dataframe(
        results: List[Dict[str, Union[str, int, float, bool, None]]],
    ) -> pd.DataFrame:
        """Converts the SearXNG results list to a pandas DataFrame.

        Args:
            results (List[Dict[str, Union[str, int, float, bool, None]]]): List of SearXNG results.

        Returns:
            pd.DataFrame: DataFrame containing the search results, with columns 'url', 'title', 'content', 'score', 'publishedDate', and 'other_info'.
        """
        logging.debug("Entering convert_to_dataframe")
        df = pd.DataFrame(
            columns=["url", "title", "content", "score", "publishedDate", "other_info"]
        )
        if results:
            results_list = SearXNGUtils.simplify_results(results)
            df = pd.DataFrame.from_dict(results_list, orient="columns")
        logging.debug("Exiting convert_to_dataframe")
        return df


class SearXNGTool:
    """
    Tool for searching using the SearXNG REST API.

    Integrates with the SearXNG API to perform programmatic searches.
    Supports different search categories, languages, and safety levels.
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

    def __init__(
        self, base_url: str = None, api_key: str = None, verify_ssl: bool = False
    ):
        """Initializes the SearXNGTool.

        Args:
            base_url (str, optional): Base URL of the SearXNG API.
                If not provided, uses the 'FBPY_SEARXNG_BASE_URL' environment variable or 'https://searxng.site' as default.
            api_key (str, optional): API key for SearXNG authentication.
                If not provided, uses the 'SEARXNG_API_KEY' environment variable.
            verify_ssl (bool, optional): Verifies the SSL certificate of the base URL.
                Defaults to False.
        """
        logging.info("Initializing SearXNGTool")
        self.base_url = base_url or os.getenv(
            "FBPY_SEARXNG_BASE_URL", "https://searxng.site"
        )
        self.api_key = api_key or os.getenv("FBPY_SEARXNG_API_KEY", None)
        self.verify_ssl = verify_ssl or "https://" in self.base_url
        self.http_client = HTTPClient(
            base_url=self.base_url,
            headers=self._build_headers(),
            verify_ssl=self.verify_ssl,
        )  # Inicializa HTTPClient com headers
        logging.info(
            f"SearXNGTool initialized with base_url={self.base_url}, api_key={'PROVIDED' if self.api_key else 'NOT PROVIDED'} and verify_ssl={self.verify_ssl}"
        )

    def _build_headers(self) -> Dict[str, str]:
        """Builds default HTTP headers for requests."""
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
        """Validates the search parameters."""
        if method not in ("GET", "POST"):
            logging.error(f"Invalid HTTP method: {method}")
            raise ValueError(f"Invalid method: {method}. Use 'GET' or 'POST'.")
        if language not in self.LANGUAGES and language != "auto":
            logging.error(f"Invalid language: {language}")
            raise ValueError(
                f"Invalid language: {language}. Use 'auto' or a valid ISO 639-1 code."
            )
        if safesearch not in (
            self.SAFESEARCH_NONE,
            self.SAFESEARCH_MODERATE,
            self.SAFESEARCH_STRICT,
        ):
            logging.error(f"Invalid safe search level: {safesearch}")
            raise ValueError(
                f"Invalid safe search level: {safesearch}. Use SAFESEARCH_NONE(0), SAFESEARCH_MODERATE(1), or SAFESEARCH_STRICT(2)."
            )

    def _prepare_search_params(
        self,
        query: str,
        categories: Optional[Union[str, List[str]]],
        language: str,
        time_range: str,
        safesearch: int,
    ) -> Dict[str, Any]:
        """Prepares the search request parameters."""
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
        logging.debug(f"Request parameters set: {params}")
        return params

    def _handle_http_error(self, e: Exception) -> List[Dict[str, Any]]:
        """Logs the HTTP error and returns an empty list."""
        logging.error(f"Error during SearXNG request: {e}")
        return []

    def search(
        self,
        query: str,
        method: str = "GET",
        categories: Optional[Union[str, List[str]]] = ["general"],
        language: str = "auto",
        time_range: str = None,
        safesearch: int = SAFESEARCH_NONE,
    ) -> List[Dict[str, Any]]:
        """Performs a synchronous search on SearXNG.

        Args:
            query (str): Search term.
            method (str, optional): HTTP method for the request ('GET' or 'POST'). Defaults to 'GET'.
            categories (Optional[Union[str, List[str]]], optional): Search categories (e.g., 'general', 'images', 'news').
                Can be a string or a list of strings. Defaults to ['general'].
            language (str, optional): Search language (ISO 639-1 code, e.g., 'en', 'pt', 'es'). Defaults to 'auto'.
            time_range (str, optional): Time range for the search (e.g., 'day', 'week', 'month', 'year'). Defaults to None.
            safesearch (int, optional): Safe search level.
                Use the constants SAFESEARCH_NONE, SAFESEARCH_MODERATE, or SAFESEARCH_STRICT. Defaults to SAFESEARCH_NONE.

        Returns:
            List[Dict[str, Any]]: List of search results, where each result is a dictionary.
                                Returns an empty list in case of a request error.

        Raises:
            ValueError: If the HTTP method, language, or safe search level is invalid.
            requests.exceptions.RequestException: If an error occurs during the HTTP request.
        """
        logging.info(f"Starting synchronous SearXNG search with query: '{query}'")
        self._validate_search_parameters(method, language, safesearch)
        params = self._prepare_search_params(
            query, categories, language, time_range, safesearch
        )
        url = f"{self.base_url}/search"

        try:
            response = self.http_client.sync_request(
                method=method, endpoint="search", params=params
            )
            response_json = response.json()
            results = response_json.get("results", [])
            logging.info(
                f"Synchronous SearXNG search for query: '{query}' completed successfully. Results found: {len(results)}"
            )
            return results
        except httpx.HTTPError as e:
            return self._handle_http_error(e)
        finally:
            logging.debug(f"Finishing synchronous SearXNG search for query: '{query}'")

    async def async_search(
        self,
        query: str,
        method: str = "GET",
        categories: Optional[Union[str, List[str]]] = ["general"],
        language: str = "auto",
        time_range: str = None,
        safesearch: int = SAFESEARCH_NONE,
    ) -> List[Dict[str, Any]]:
        """Performs an asynchronous search on SearXNG.

        Args:
            query (str): Search term.
            method (str, optional): HTTP method for the request ('GET' or 'POST'). Defaults to 'GET'.
            categories (Optional[Union[str, List[str]]], optional): Search categories (e.g., 'general', 'images', 'news').
                Can be a string or a list of strings. Defaults to ['general'].
            language (str, optional): Search language (ISO 639-1 code, e.g., 'en', 'pt', 'es'). Defaults to 'auto'.
            time_range (str, optional): Time range for the search (e.g., 'day', 'week', 'month', 'year'). Defaults to None.
            safesearch (int, optional): Safe search level.
                Use the constants SAFESEARCH_NONE, SAFESEARCH_MODERATE, or SAFESEARCH_STRICT. Defaults to SAFESEARCH_NONE.

        Returns:
            List[Dict[str, Any]]: List of search results, where each result is a dictionary.
                                Returns an empty list in case of a request error.

        Raises:
            ValueError: If the HTTP method, language, or safe search level is invalid.
            httpx.HTTPError: If an error occurs during the HTTP request.
        """
        logging.info(f"Starting asynchronous SearXNG search with query: '{query}'")
        self._validate_search_parameters(method, language, safesearch)
        params = self._prepare_search_params(
            query, categories, language, time_range, safesearch
        )

        try:
            response = await self.http_client.async_request(
                method=method, endpoint="search", params=params
            )
            response_json = response.json()
            results = response_json.get("results", [])
            logging.info(
                f"Asynchronous SearXNG search for query: '{query}' completed successfully. Results found: {len(results)}"
            )
            return results
        except httpx.HTTPError as e:
            return self._handle_http_error(e)
        finally:
            logging.debug(f"Finishing asynchronous SearXNG search for query: '{query}'")
