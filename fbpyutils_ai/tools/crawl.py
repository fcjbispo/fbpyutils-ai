import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Any, Dict

from fbpyutils_ai import logging


class FireCrawlTool:
    def __init__(self, base_url: str = None, token: str = None):
        """
        Initializes the FireCrawlTool with base URL and token.

        :param base_url: The base URL of the API.
        :param token: The authentication token.
        """
        self.base_url = base_url or os.environ.get(
            "FBPY_FIRECRAWL_BASE_URL", "https://api.firecrawl.dev/v1"  # Updated to v1
        )
        self.session = requests.Session()
        retries = Retry(
            total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self._headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
            "Content-Type": "application/json",
        }
        token = token or os.environ.get("FBPY_FIRECRAWL_API_KEY")
        if token is not None and token != "":
            self._headers["Authorization"] = f"Bearer {token}"
        self.session.headers.update(self._headers)
        logging.info("Initialized FireCrawlTool with base URL %s", base_url)

    def scrape(
        self,
        url: str,
        formats: list[str] = ["markdown"],
        onlyMainContent: bool = False,
        includeTags: list[str] | None = None,
        excludeTags: list[str] | None = None,
        headers: dict | None = None,
        waitFor: int = 0,
        mobile: bool = False,
        skipTlsVerification: bool = False,
        timeout: int = 30000,
        jsonOptions: dict | None = None,
        actions: list[dict] | None = None,
        location: dict | None = None,
        removeBase64Images: bool = False,
        blockAds: bool = False,
        proxy: str | None = None,
        changeTrackingOptions: dict | None = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Scrape a single URL using the Firecrawl v1 API.

        Reference: https://docs.firecrawl.dev/api-reference/endpoint/scrape

        :param url: The URL to scrape.
        :param formats: List of formats to return (e.g., ["markdown", "html"]). Default: ["markdown"].
        :param onlyMainContent: Return only the main content of the page. Default: False.
        :param includeTags: List of CSS selectors to include. Default: None.
        :param excludeTags: List of CSS selectors to exclude. Default: None.
        :param headers: Custom headers for the request. Default: None.
        :param waitFor: Wait time in milliseconds for dynamic content. Default: 0.
        :param mobile: Use a mobile user agent. Default: False.
        :param skipTlsVerification: Skip TLS verification. Default: False.
        :param timeout: Request timeout in milliseconds. Default: 30000.
        :param jsonOptions: Options for JSON extraction (schema, prompts). Default: None.
        :param actions: List of browser actions to perform (wait, click, etc.). Default: None.
        :param location: Geolocation options (country, languages). Default: None.
        :param removeBase64Images: Remove base64 encoded images. Default: False.
        :param blockAds: Block ads during scraping. Default: False.
        :param proxy: Proxy configuration. Default: None.
        :param changeTrackingOptions: Options for tracking content changes. Default: None.
        :param kwargs: Additional keyword arguments passed directly to the API payload.
        :return: A dictionary with the scrape results from the v1 API.

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
                "screenshot": "<string>",
                "links": ["<string>"],
                "actions": { ... },
                "metadata": { ... },
                "llm_extraction": {},
                "warning": "<string>",
                "changeTracking": { ... }
              }
            }
        """
        payload = {
            "url": url,
            "formats": formats,
            "onlyMainContent": onlyMainContent,
            "waitFor": waitFor,
            "mobile": mobile,
            "skipTlsVerification": skipTlsVerification,
            "timeout": timeout,
            "removeBase64Images": removeBase64Images,
            "blockAds": blockAds,
            **kwargs,  # Include any extra kwargs directly
        }
        # Add optional parameters only if they are provided (not None or default)
        if includeTags is not None:
            payload["includeTags"] = includeTags
        if excludeTags is not None:
            payload["excludeTags"] = excludeTags
        if headers is not None:
            payload["headers"] = headers
        if jsonOptions is not None:
            payload["jsonOptions"] = jsonOptions
        if actions is not None:
            payload["actions"] = actions
        if location is not None:
            payload["location"] = location
        if proxy is not None:
            payload["proxy"] = proxy
        if changeTrackingOptions is not None:
            payload["changeTrackingOptions"] = changeTrackingOptions

        logging.info("Sending v1 scrape request with payload: %s", payload)
        # Ensure the endpoint uses the base_url which should now point to v1
        response = self.session.post(f"{self.base_url}/scrape", json=payload)
        try:
            response.raise_for_status()
            result = response.json()
            logging.info("Scrape successful for URL %s", url)
            return result
        except requests.RequestException as e:
            logging.error("Scrape request failed: %s", e)
            raise

    def crawl(self, url: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Initiate a crawl for multiple URLs.

        :param url: The starting URL for the crawl.
        :param kwargs: Optional arguments for crawler and page options.
            - crawlerOptions (dict): Options controlling the crawl behavior.
                - includes (List[str]): URL patterns to include in the crawl. Default: []. Optional: Yes.
                - excludes (List[str]): URL patterns to exclude from the crawl. Default: []. Optional: Yes.
                - generateImgAltText (bool): Generate alt text for images using LLMs (requires paid plan). Default: false. Optional: Yes.
                - returnOnlyUrls (bool): Return only found URLs, without content. Default: false. Optional: Yes.
                - maxDepth (int): Maximum crawl depth from the base URL. Default: 123. Optional: Yes.
                - mode (str): Crawling mode: `default` or `fast` (faster, less accurate). Default: "default". Optional: Yes.
                - ignoreSitemap (bool): Ignore the website's sitemap. Default: false. Optional: Yes.
                - limit (int): Maximum number of pages to crawl. Default: 10000. Optional: Yes.
                - allowBackwardCrawling (bool): Allow crawling to previously linked pages. Default: false. Optional: Yes.
                - allowExternalContentLinks (bool): Allow following links to external websites. Default: false. Optional: Yes.
            - pageOptions (dict): Options applied to each crawled page (same as `scrape` method's pageOptions). Default: {}. Optional: Yes.
        :return: A dictionary containing the `jobId` for the initiated crawl.

        Example Request:
            tool.crawl(
                url="http://example.com",
                crawlerOptions={
                    "excludes": ["/login"],
                    "limit": 10
                },
                pageOptions={
                    "onlyMainContent": True
                }
            )

        Example Response:
            {
                "jobId": "some-unique-job-id-string"
            }
        """
        payload = {"url": url, **kwargs}

        page_options = payload.get("pageOptions", {})
        page_options["headers"] = self._headers
        payload["pageOptions"] = page_options

        logging.info("Sending crawl request with payload: %s", payload)
        response = self.session.post(f"{self.base_url}/crawl", json=payload)
        try:
            response.raise_for_status()
            result = response.json()
            logging.info("Crawl initiated for URL %s", url)
            return result
        except requests.RequestException as e:
            logging.error("Crawl request failed: %s", e)
            raise

    def get_crawl_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a crawl job.

        :param job_id: The ID of the crawl job.
        :return: A dictionary with the crawl status.

        Example:
        response: {
            "status": "string",
            "current": "integer",
            "current_url": "string",
            "current_step": "string",
            "total": "integer",
            "data": [{}],
            "partial_data": [{}]
        }
        """
        logging.info("Fetching status for crawl job %s", job_id)
        response = self.session.get(f"{self.base_url}/crawl/status/{job_id}")
        try:
            response.raise_for_status()
            result = response.json()
            logging.info("Crawl status retrieved for job %s", job_id)
            return result
        except requests.RequestException as e:
            logging.error("Failed to fetch crawl status: %s", e)
            raise

    def cancel_crawl(self, job_id: str) -> Dict[str, Any]:
        """
        Cancel a crawl job.

        :param job_id: The ID of the crawl job.
        :return: A dictionary with the cancellation result.

        Example:
        response: {
            "status": "cancelled"
        }
        """
        logging.info("Cancelling crawl job %s", job_id)
        response = self.session.delete(f"{self.base_url}/crawl/cancel/{job_id}")
        try:
            response.raise_for_status()
            result = response.json()
            logging.info("Crawl job %s cancelled successfully", job_id)
            return result
        except requests.RequestException as e:
            logging.error("Failed to cancel crawl job: %s", e)
            raise

    def search(self, query: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Search for a keyword using the API.

        :param query: The search query.
        :param kwargs: Optional arguments for page scraping, extractor, and timeout.
        :return: A dictionary with the search results.

        Example Request:
            tool.search(
                query="latest AI news",
                pageOptions={
                    "fetchPageContent": True # Fetch content for search results
                },
                searchOptions={
                    "limit": 5
                }
            )

        Example Response:
            {
                "success": True,
                "data": [
                    {
                        "url": "https://example-news.com/ai-article",
                        "markdown": "...", # If fetchPageContent is True
                        "content": "...",  # If fetchPageContent is True
                        "metadata": {
                            "title": "Latest AI News",
                            "description": "...",
                            "language": "en",
                            "sourceURL": "https://example-news.com/ai-article"
                        }
                    },
                    # ... more results up to the limit
                ]
            }
        """
        payload = {"query": query, **kwargs}
        logging.info("Sending search request with query: %s", query)
        response = self.session.post(f"{self.base_url}/search", json=payload)
        try:
            response.raise_for_status()
            result = response.json()
            logging.info("Search successful for query %s", query)
            return result
        except requests.RequestException as e:
            logging.error("Search request failed: %s", e)
            raise
