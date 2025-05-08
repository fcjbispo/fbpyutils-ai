
import os
from typing import Any, Dict

from fbpyutils_ai import logging


from fbpyutils_ai.tools.http import HTTPClient

class FireCrawlTool:
    def __init__(self, base_url: str = None, token: str = None, verify_ssl: bool = True):
        """
        Initializes the FireCrawlTool with base URL, token, and SSL verification setting.

        :param base_url: The base URL of the Firecrawl API. Defaults to self-hosted URL.
        :param token: The authentication token. Optional for self-hosted.
        :param verify_ssl: Whether to verify SSL certificates. Defaults to True.
        """
        self._base_url = base_url or os.environ.get(
            "FBPY_FIRECRAWL_BASE_URL", "http://localhost:3005/v1"  # Default to self-hosted v1
        )
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
            "Content-Type": "application/json",
        }
        token = token or os.environ.get("FBPY_FIRECRAWL_API_KEY")
        if token is not None and token != "":
            self._headers["Authorization"] = f"Bearer {token}"

        self.http_client = HTTPClient(
            base_url=self._base_url,
            headers=self._headers,
            verify_ssl=verify_ssl
        )
        logging.info("Initialized FireCrawlTool with base URL %s", self._base_url)

    def scrape(
        self,
        url: str,
        formats: list[str] = ["markdown"],
        onlyMainContent: bool = False,
        includeTags: list[str] | None = None,
        excludeTags: list[str] | None = None,
        headers: dict | None = None,
        waitFor: int = 0,
        timeout: int = 30000,
        removeBase64Images: bool = False,
    ) -> Dict[str, Any]:
        """
        Scrape a single URL using the Firecrawl v1 API (Self-Hosted compatible).
        This version is adjusted for self-hosted instances without fire-engine, supporting a limited set of parameters.

        Reference: https://docs.firecrawl.dev/api-reference/endpoint/scrape

        :param url: The URL to scrape. (required)
        :param formats: List of formats to return (e.g., ["markdown", "html"]). Default: ["markdown"].
        :param onlyMainContent: Return only the main content of the page. Default: False.
        :param includeTags: List of CSS selectors to include. Default: None.
        :param excludeTags: List of CSS selectors to exclude. Default: None.
        :param headers: Custom headers for the request. Default: None.
        :param waitFor: Wait time in milliseconds for dynamic content. Default: 0.
        :param timeout: Request timeout in milliseconds. Default: 30000.
        :param removeBase64Images: Remove base64 encoded images. Default: False.
        :return: A dictionary with the scrape results from the v1 API.
        :raises httpx.HTTPStatusError: If the API returns a 4xx or 5xx status code.
        :raises httpx.RequestError: If a network or other request error occurs.

        Example Request:
            tool.scrape(
                url="https://example.com",
                onlyMainContent=True,
                formats=["markdown"]
            )

        Example Response (v1 structure):
            {
              "success": True,
              "data": {
                "markdown": "<string>",
                "html": "<string>",
                "rawHtml": "<string>",
                "screenshot": "<string>", # Only if supported and requested
                "links": ["<string>"],
                "metadata": { ... },
                "llm_extraction": {}, # Only if supported and requested
                "warning": "<string>",
                "changeTracking": { ... } # Only if supported and requested
              }
            }
        """
        payload = {
            "url": url,
            "formats": formats,
            "onlyMainContent": onlyMainContent,
            "includeTags": includeTags,
            "excludeTags": excludeTags,
            "headers": headers,
            "waitFor": waitFor,
            "timeout": timeout,
            "removeBase64Images": removeBase64Images,
        }

        # Remove None values from payload
        payload = {k: v for k, v in payload.items() if v is not None}

        logging.info("Sending v1 scrape request with payload: %s", payload)
        # Use HTTPClient to make the request
        response = self.http_client.sync_request(
            "POST",
            "scrape",
            json=payload
        )
        response_data = response.json()
        logging.info("Scrape successful for URL %s", url)
        return response_data
















    def search(
        self,
        query: str,
        limit: int = 5,
        tbs: str | None = None,
        lang: str = "en",
        country: str = "us",
        timeout: int = 60000,
        formats: list[str] = ["markdown"],
        onlyMainContent: bool = False,
        includeTags: list[str] | None = None,
        excludeTags: list[str] | None = None,
        headers: dict | None = None,
        waitFor: int = 0,
        removeBase64Images: bool = False,
    ) -> Dict[str, Any]:
        """
        Search for a keyword using the API (Self-Hosted compatible).

        Reference: https://docs.firecrawl.dev/api-reference/endpoint/search

        :param query: The search query. (required)
        :param limit: Maximum number of results to return. Default: 5.
        :param tbs: Time-based search parameter. Default: None.
        :param lang: Language code for search results. Default: "en".
        :param country: Country code for search results. default: "us".
        :param timeout: Timeout in milliseconds. Default: 60000.
        :param formats: List of formats to return for each scraped search result. Default: ["markdown"].
        :param onlyMainContent: Return only the main content of each scraped search result. Default: False.
        :param includeTags: List of CSS selectors to include for each scraped search result. Default: None.
        :param excludeTags: List of CSS selectors to exclude for each scraped search result. Default: None.
        :param headers: Custom headers for the request to each scraped search result. Default: None.
        :param waitFor: Wait time in milliseconds for dynamic content on each scraped search result. Default: 0.
        :param removeBase64Images: Remove base64 encoded images from each scraped search result. Default: False.
        :return: A dictionary with the search results.
        :raises httpx.HTTPStatusError: If the API returns a 4xx or 5xx status code.
        :raises httpx.RequestError: If a network or other request error occurs.

        Example Request:
            tool.search(
                query="latest AI news",
                formats=["markdown"], # Fetch content for search results
                limit=5
            )

        Example Response:
            {
                "success": True,
                "data": [
                    {
                        "title": "<string>",
                        "description": "<string>",
                        "url": "<string>",
                        "markdown": "<string>", # If markdown format requested
                        "html": "<string>", # If html format requested
                        "rawHtml": "<string>", # If rawHtml format requested
                        "links": ["<string>"], # If links format requested
                        "screenshot": "<string>", # If screenshot format requested
                        "metadata": { ... }
                    },
                    # ... more results up to the limit
                ],
                "warning": "<string>"
            }
        """
        payload = {
            "query": query,
            "limit": limit,
            "tbs": tbs,
            "lang": lang,
            "country": country,
            "timeout": timeout,
            "scrapeOptions": {
                "formats": formats,
                "onlyMainContent": onlyMainContent,
                "includeTags": includeTags,
                "excludeTags": excludeTags,
                "headers": headers,
                "waitFor": waitFor,
                "removeBase64Images": removeBase64Images,
            },
        }

        # Remove None values from payload, including nested dictionaries
        payload = {k: v for k, v in payload.items() if v is not None}
        if "searchOptions" in payload:
            payload["searchOptions"] = {
                k: v for k, v in payload["searchOptions"].items() if v is not None
            }
        if "scrapeOptions" in payload:
            payload["scrapeOptions"] = {
                k: v for k, v in payload["scrapeOptions"].items() if v is not None
            }

        logging.info("Sending v1 search request with payload: %s", payload)
        # Use HTTPClient to make the request
        response_data = self.http_client.sync_request(
            "POST",
            "search",
            json=payload
        )
        logging.info("Search successful for query: %s", query)
        return response_data
