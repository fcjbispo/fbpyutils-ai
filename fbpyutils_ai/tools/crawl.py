import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
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
        self.base_url = base_url or os.environ.get(
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
            base_url=self.base_url,
            headers=self._headers,
            verify_ssl=verify_ssl
        )
        logging.info("Initialized FireCrawlTool with base URL %s", self.base_url)

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
        jsonOptions: dict | None = None,
        removeBase64Images: bool = False,
        blockAds: bool = False,
        **kwargs: Any, # Catch any other supported parameters
    ) -> Dict[str, Any]:
        """
        Scrape a single URL using the Firecrawl v1 API (Self-Hosted compatible).

        Reference: https://docs.firecrawl.dev/api-reference/endpoint/scrape
        Note: Parameters 'mobile', 'skipTlsVerification', 'actions', 'location', 'proxy', and 'changeTrackingOptions' are not supported in self-hosted mode (without fire-engine) and will be ignored.

        :param url: The URL to scrape. (required)
        :param formats: List of formats to return (e.g., ["markdown", "html"]). Default: ["markdown"].
        :param onlyMainContent: Return only the main content of the page. Default: False.
        :param includeTags: List of CSS selectors to include. Default: None.
        :param excludeTags: List of CSS selectors to exclude. Default: None.
        :param headers: Custom headers for the request. Default: None.
        :param waitFor: Wait time in milliseconds for dynamic content. Default: 0.
        :param timeout: Request timeout in milliseconds. Default: 30000.
        :param jsonOptions: Options for JSON extraction (schema, prompts). Default: None.
        :param removeBase64Images: Remove base64 encoded images. Default: False.
        :param blockAds: Block ads during scraping. Default: False.
        :param kwargs: Additional supported keyword arguments passed directly to the API payload.
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
            "waitFor": waitFor,
            "timeout": timeout,
            "removeBase64Images": removeBase64Images,
            "blockAds": blockAds,
            **kwargs,  # Include any extra kwargs directly
        }

        # Remove unsupported parameters
        unsupported_params = ['mobile', 'skipTlsVerification', 'actions', 'location', 'proxy', 'changeTrackingOptions']
        payload = {k: v for k, v in payload.items() if k not in unsupported_params}

        # Add optional parameters only if they are provided (not None)
        if includeTags is not None:
            payload["includeTags"] = includeTags
        if excludeTags is not None:
            payload["excludeTags"] = excludeTags
        if headers is not None:
            payload["headers"] = headers
        if jsonOptions is not None:
            payload["jsonOptions"] = jsonOptions

        logging.info("Sending v1 scrape request with payload: %s", payload)
        # Use HTTPClient to make the request
        response_data = self.http_client.sync_request(
            "POST",
            "scrape",
            json=payload
        )
        logging.info("Scrape successful for URL %s", url)
        return response_data

    def crawl(self, url: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Initiate a crawl for multiple URLs (Self-Hosted compatible).

        :param url: The starting URL for the crawl. (required)
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
        :raises httpx.HTTPStatusError: If the API returns a 4xx or 5xx status code.
        :raises httpx.RequestError: If a network or other request error occurs.

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

        # Ensure scrapeOptions within pageOptions only contains supported parameters
        if 'scrapeOptions' in payload and isinstance(payload['scrapeOptions'], dict):
            unsupported_scrape_params = ['mobile', 'skipTlsVerification', 'actions', 'location', 'proxy', 'changeTrackingOptions']
            payload['scrapeOptions'] = {
                k: v for k, v in payload['scrapeOptions'].items()
                if k not in unsupported_scrape_params
            }

        logging.info("Sending crawl request with payload: %s", payload)
        # Use HTTPClient to make the request
        response_data = self.http_client.sync_request(
            "POST",
            "crawl",
            json=payload
        )
        logging.info("Crawl initiated for URL %s", url)
        return response_data

    def get_crawl_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a crawl job.

        :param job_id: The ID of the crawl job.
        :return: A dictionary with the crawl status.
        :raises httpx.HTTPStatusError: If the API returns a 4xx or 5xx status code.
        :raises httpx.RequestError: If a network or other request error occurs.

        Example Response:
            {
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
        # Use HTTPClient to make the request
        response_data = self.http_client.sync_request(
            "GET",
            f"crawl/{job_id}",
            params=None,
            data=None,
            json=None,
            stream=False
        )
        logging.info("Crawl status retrieved for job %s", job_id)
        return response_data

    def cancel_crawl(self, job_id: str) -> Dict[str, Any]:
        """
        Cancel a crawl job.

        :param job_id: The ID of the crawl job.
        :return: A dictionary with the cancellation result.
        :raises httpx.HTTPStatusError: If the API returns a 4xx or 5xx status code.
        :raises httpx.RequestError: If a network or other request error occurs.

        Example Response:
            {
                "status": "cancelled"
            }
        """
        logging.info("Cancelling crawl job %s", job_id)
        # Use HTTPClient to make the request
        response_data = self.http_client.sync_request(
            "DELETE",
            f"crawl/cancel/{job_id}",
            params=None,
            data=None,
            json=None,
            stream=False
        )
        logging.info("Crawl job %s cancelled successfully", job_id)
        return response_data

    def get_crawl_errors(self, job_id: str) -> Dict[str, Any]:
        """
        Get the errors for a crawl job.

        :param job_id: The ID of the crawl job.
        :return: A dictionary with the crawl errors and robotsBlocked list.
        :raises httpx.HTTPStatusError: If the API returns a 4xx or 5xx status code.
        :raises httpx.RequestError: If a network or other request error occurs.

        Example Response:
            {
                "errors": [
                    {
                        "id": "string",
                        "timestamp": "string",
                        "url": "string",
                        "error": "string"
                    }
                ],
                "robotsBlocked": ["string"]
            }
        """
        logging.info("Fetching errors for crawl job %s", job_id)
        # Use HTTPClient to make the request
        response_data = self.http_client.sync_request(
            "GET",
            f"crawl/{job_id}/errors",
            params=None,
            data=None,
            json=None,
            stream=False
        )
        logging.info("Crawl errors retrieved for job %s", job_id)
        return response_data

    def get_batch_scrape_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a batch scrape job.

        :param job_id: The ID of the batch scrape job.
        :return: A dictionary with the batch scrape status.
        :raises httpx.HTTPStatusError: If the API returns a 4xx or 5xx status code.
        :raises httpx.RequestError: If a network or other request error occurs.

        Example Response:
            {
                "status": "string",
                "total": "integer",
                "completed": "integer",
                "creditsUsed": "integer",
                "expiresAt": "string",
                "next": "string",
                "data": [{}]
            }
        """
        logging.info("Fetching status for batch scrape job %s", job_id)
        # Use HTTPClient to make the request
        response_data = self.http_client.sync_request(
            "GET",
            f"batch/scrape/{job_id}",
            params=None,
            data=None,
            json=None,
            stream=False
        )
        logging.info("Batch scrape status retrieved for job %s", job_id)
        return response_data

    def get_batch_scrape_errors(self, job_id: str) -> Dict[str, Any]:
        """
        Get the errors for a batch scrape job.

        :param job_id: The ID of the batch scrape job.
        :return: A dictionary with the batch scrape errors and robotsBlocked list.
        :raises httpx.HTTPStatusError: If the API returns a 4xx or 5xx status code.
        :raises httpx.RequestError: If a network or other request error occurs.

        Example Response:
            {
                "errors": [
                    {
                        "id": "string",
                        "timestamp": "string",
                        "url": "string",
                        "error": "string"
                    }
                ],
                "robotsBlocked": ["string"]
            }
        """
        logging.info("Fetching errors for batch scrape job %s", job_id)
        # Use HTTPClient to make the request
        response_data = self.http_client.sync_request(
            "GET",
            f"batch/scrape/{job_id}/errors",
            params=None,
            data=None,
            json=None,
            stream=False
        )
        logging.info("Batch scrape errors retrieved for job %s", job_id)
        return response_data

    def batch_scrape(
        self,
        urls: list[str],
        webhook: dict | None = None,
        ignoreInvalidURLs: bool = False,
        formats: list[str] = ["markdown"],
        onlyMainContent: bool = False,
        includeTags: list[str] | None = None,
        excludeTags: list[str] | None = None,
        headers: dict | None = None,
        waitFor: int = 0,
        timeout: int = 30000,
        jsonOptions: dict | None = None,
        removeBase64Images: bool = False,
        blockAds: bool = False,
        **kwargs: Any, # Catch any other supported parameters
    ) -> Dict[str, Any]:
        """
        Initiate a batch scrape for multiple URLs (Self-Hosted compatible).

        Reference: https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape
        Note: Parameters not supported in self-hosted mode (without fire-engine) are excluded.

        :param urls: The list of URLs to scrape. (required)
        :param webhook: A webhook specification object. Default: None.
        :param ignoreInvalidURLs: If invalid URLs are specified, they will be ignored. Default: False.
        :param formats: List of formats to return (e.g., ["markdown", "html"]). Default: ["markdown"].
        :param onlyMainContent: Return only the main content of the page. Default: False.
        :param includeTags: List of CSS selectors to include. Default: None.
        :param excludeTags: List of CSS selectors to exclude. Default: None.
        :param headers: Custom headers for the request. Default: None.
        :param waitFor: Wait time in milliseconds for dynamic content. Default: 0.
        :param timeout: Request timeout in milliseconds. Default: 30000.
        :param jsonOptions: Options for JSON extraction (schema, prompts). Default: None.
        :param removeBase64Images: Remove base64 encoded images. Default: False.
        :param blockAds: Block ads during scraping. Default: False.
        :param kwargs: Additional supported keyword arguments passed directly to the API payload.
        :return: A dictionary with the batch scrape job ID and invalid URLs.
        :raises httpx.HTTPStatusError: If the API returns a 4xx or 5xx status code.
        :raises httpx.RequestError: If a network or other request error occurs.

        Example Request:
            tool.batch_scrape(
                urls=["https://example.com/page1", "https://example.com/page2"],
                onlyMainContent=True,
                formats=["markdown"]
            )

        Example Response:
            {
              "success": True,
              "id": "<string>",
              "url": "<string>", # Base URL of the batch job status
              "invalidURLs": ["<string>"] # List of URLs that were ignored
            }
        """
        payload = {
            "urls": urls,
            "ignoreInvalidURLs": ignoreInvalidURLs,
            "formats": formats,
            "onlyMainContent": onlyMainContent,
            "waitFor": waitFor,
            "timeout": timeout,
            "removeBase64Images": removeBase64Images,
            "blockAds": blockAds,
            **kwargs,  # Include any extra kwargs directly
        }

        # Remove unsupported parameters
        unsupported_params = ['mobile', 'skipTlsVerification', 'actions', 'location', 'proxy', 'changeTrackingOptions']
        payload = {k: v for k, v in payload.items() if k not in unsupported_params}

        # Add optional parameters only if they are provided (not None)
        if webhook is not None:
            payload["webhook"] = webhook
        if includeTags is not None:
            payload["includeTags"] = includeTags
        if excludeTags is not None:
            payload["excludeTags"] = excludeTags
        if headers is not None:
            payload["headers"] = headers
        if jsonOptions is not None:
            payload["jsonOptions"] = jsonOptions

        logging.info("Sending v1 batch scrape request with payload: %s", payload)
        # Use HTTPClient to make the request
        response_data = self.http_client.sync_request(
            "POST",
            "batch/scrape",
            json=payload
        )
        logging.info("Batch scrape initiated for URLs: %s", urls)
        return response_data

    def get_extract_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of an extract job.

        :param job_id: The ID of the extract job.
        :return: A dictionary with the extract status.
        :raises httpx.HTTPStatusError: If the API returns a 4xx or 5xx status code.
        :raises httpx.RequestError: If a network or other request error occurs.

        Example Response:
            {
                "status": "string",
                "total": "integer",
                "completed": "integer",
                "creditsUsed": "integer",
                "expiresAt": "string",
                "next": "string",
                "data": [{}]
            }
        """
        logging.info("Fetching status for extract job %s", job_id)
        # Use HTTPClient to make the request
        response_data = self.http_client.sync_request(
            "GET",
            f"extract/{job_id}",
            params=None,
            data=None,
            json=None,
            stream=False
        )
        logging.info("Extract status retrieved for job %s", job_id)
        return response_data

    def extract(
        self,
        urls: list[str],
        prompt: str | None = None,
        schema: dict | None = None,
        ignoreSitemap: bool = False,
        includeSubdomains: bool = True,
        showSources: bool = False,
        scrapeOptions: dict | None = None,
        **kwargs: Any, # Catch any other supported parameters
    ) -> Dict[str, Any]:
        """
        Extract structured data from URLs using the Firecrawl v1 API (Self-Hosted compatible).

        Reference: https://docs.firecrawl.dev/api-reference/endpoint/extract
        Note: Parameters not supported in self-hosted mode (without fire-engine) are excluded.

        :param urls: The list of URLs to extract data from. URLs should be in glob format. (required)
        :param prompt: Prompt to guide the extraction process. Default: None.
        :param schema: Schema to define the structure of the extracted data. Default: None.
        :param ignoreSitemap: When true, sitemap.xml files will be ignored during website scanning. Default: False.
        :param includeSubdomains: When true, subdomains of the provided URLs will also be scanned. Default: True.
        :param showSources: When true, the sources used to extract the data will be included in the response. Default: False.
        :param scrapeOptions: Options for scraping the URLs before extraction. Default: None.
        :param kwargs: Additional supported keyword arguments passed directly to the API payload.
        :return: A dictionary with the extract job ID.
        :raises httpx.HTTPStatusError: If the API returns a 4xx or 5xx status code.
        :raises httpx.RequestError: If a network or other request error occurs.

        Example Request:
            tool.extract(
                urls=["https://example.com/product/*"],
                schema={"product_name": "string", "price": "number"}
            )

        Example Response:
            {
              "success": True,
              "id": "<string>"
            }
        """
        payload = {
            "urls": urls,
            "ignoreSitemap": ignoreSitemap,
            "includeSubdomains": includeSubdomains,
            "showSources": showSources,
            **kwargs, # Include any extra kwargs directly
        }

        unsupported_params = ['enableWebSearch']
        payload = {k: v for k, v in payload.items() if k not in unsupported_params}

        # Add optional parameters only if they are provided (not None)
        if prompt is not None:
            payload["prompt"] = prompt
        if schema is not None:
            payload["schema"] = schema
        if scrapeOptions is not None:
             unsupported_scrape_params = ['mobile', 'skipTlsVerification', 'actions', 'location', 'proxy', 'changeTrackingOptions']
             payload['scrapeOptions'] = {
                 k: v for k, v in scrapeOptions.items()
                 if k not in unsupported_scrape_params
             }
        elif 'scrapeOptions' in kwargs: # Handle scrapeOptions passed in kwargs
             unsupported_scrape_params = ['mobile', 'skipTlsVerification', 'actions', 'location', 'proxy', 'changeTrackingOptions']
             payload['scrapeOptions'] = {
                 k: v for k, v in kwargs['scrapeOptions'].items()
                 if k not in unsupported_scrape_params
             }


        logging.info("Sending v1 extract request with payload: %s", payload)
        # Use HTTPClient to make the request
        response_data = self.http_client.sync_request(
            "POST",
            "extract",
            json=payload
        )
        logging.info("Extract initiated for URLs: %s", urls)
        return response_data

    def map(
        self,
        url: str,
        search: str | None = None,
        ignoreSitemap: bool = True,
        sitemapOnly: bool = False,
        includeSubdomains: bool = False,
        limit: int = 5000,
        timeout: int | None = None,
        **kwargs: Any, # Catch any other supported parameters
    ) -> Dict[str, Any]:
        """
        Map a website's links using the Firecrawl v1 API (Self-Hosted compatible).

        Reference: https://docs.firecrawl.dev/api-reference/endpoint/map
        Note: Parameters not supported in self-hosted mode (without fire-engine) are excluded.

        :param url: The base URL to start mapping from. (required)
        :param search: Search query to filter links. Default: None.
        :param ignoreSitemap: Ignore the website sitemap when mapping. Default: True.
        :param sitemapOnly: Only return links found in the website sitemap. Default: False.
        :param includeSubdomains: Include subdomains of the website. Default: False.
        :param limit: Maximum number of links to return. Default: 5000.
        :param timeout: Timeout in milliseconds. Default: None.
        :param kwargs: Additional supported keyword arguments passed directly to the API payload.
        :return: A dictionary with the list of links.
        :raises httpx.HTTPStatusError: If the API returns a 4xx or 5xx status code.
        :raises httpx.RequestError: If a network or other request error occurs.

        Example Request:
            tool.map(
                url="https://example.com",
                search="products"
            )

        Example Response:
            {
              "success": True,
              "links": ["<string>"]
            }
        """
        payload = {
            "url": url,
            "ignoreSitemap": ignoreSitemap,
            "sitemapOnly": sitemapOnly,
            "includeSubdomains": includeSubdomains,
            "limit": limit,
            **kwargs, # Include any extra kwargs directly
        }
        # Add optional parameters only if they are provided (not None)
        if search is not None:
            payload["search"] = search
        if timeout is not None:
            payload["timeout"] = timeout

        logging.info("Sending v1 map request with payload: %s", payload)
        # Use HTTPClient to make the request
        response_data = self.http_client.sync_request(
            "POST",
            "map",
            json=payload
        )
        logging.info("Map successful for URL: %s", url)
        return response_data


    def search(self, query: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Search for a keyword using the API (Self-Hosted compatible).

        :param query: The search query. (required)
        :param kwargs: Optional arguments for search options and scrape options.
            - limit (int): Maximum number of results to return. Default: 5.
            - tbs (str): Time-based search parameter. Default: None.
            - lang (str): Language code for search results. Default: "en".
            - country (str): Country code for search results. Default: "us".
            - timeout (int): Timeout in milliseconds. Default: 60000.
            - scrapeOptions (dict): Options for scraping search results. Default: None.
        :return: A dictionary with the search results.
        :raises httpx.HTTPStatusError: If the API returns a 4xx or 5xx status code.
        :raises httpx.RequestError: If a network or other request error occurs.

        Example Request:
            tool.search(
                query="latest AI news",
                scrapeOptions={
                    "formats": ["markdown"] # Fetch content for search results
                },
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
        # Remove unsupported 'location' parameter for self-hosted
        supported_kwargs = {k: v for k, v in kwargs.items() if k != 'location'}

        payload = {"query": query, **supported_kwargs}

        # Remove unsupported parameters from scrapeOptions
        if 'scrapeOptions' in payload and isinstance(payload['scrapeOptions'], dict):
            unsupported_scrape_params = ['mobile', 'skipTlsVerification', 'actions', 'location', 'proxy', 'changeTrackingOptions']
            payload['scrapeOptions'] = {
                k: v for k, v in payload['scrapeOptions'].items()
                if k not in unsupported_scrape_params
            }

        # Remove unsupported parameters from main payload
        unsupported_params = ['location']
        payload = {k: v for k, v in payload.items() if k not in unsupported_params}

        logging.info("Sending search request with query: %s", payload)
        # Use HTTPClient to make the request
        response_data = self.http_client.sync_request(
            "POST",
            "search",
            json=payload
        )
        logging.info("Search successful for query %s", query)
        return response_data
