
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures
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
        includeHtml: bool = False,
        includeRawHtml: bool = False,
        replaceAllPathsWithAbsolutePaths: bool = True,
        mode: str = "markdown",
    ) -> Dict[str, Any]:
        """
        Scrape a single URL using the Firecrawl v1 API (Self-Hosted compatible).

        Reference: https://docs.firecrawl.dev/api-reference/endpoint/scrape

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
        :param includeHtml: Include the full HTML content in the response. Default: False.
        :param includeRawHtml: Include the raw HTML content in the response. Default: False.
        :param replaceAllPathsWithAbsolutePaths: Replace all relative paths with absolute paths. Default: True.
        :param mode: Extraction mode (e.g., "markdown", "text", "html"). Default: "markdown".
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
            "jsonOptions": jsonOptions,
            "removeBase64Images": removeBase64Images,
            "blockAds": blockAds,
            "includeHtml": includeHtml,
            "includeRawHtml": includeRawHtml,
            "replaceAllPathsWithAbsolutePaths": replaceAllPathsWithAbsolutePaths,
            "mode": mode,
        }

        # Remove None values from payload
        payload = {k: v for k, v in payload.items() if v is not None}

        logging.info("Sending v1 scrape request with payload: %s", payload)
        # Use HTTPClient to make the request
        response_data = self.http_client.sync_request(
            "POST",
            "scrape",
            json=payload
        )
        logging.info("Scrape successful for URL %s", url)
        return response_data

    def crawl(
        self,
        url: str,
        includes: list[str] | None = None,
        excludes: list[str] | None = None,
        generateImgAltText: bool = False,
        returnOnlyUrls: bool = False,
        maxDepth: int = 123,
        mode: str = "default",
        ignoreSitemap: bool = False,
        limit: int = 10000,
        allowBackwardCrawling: bool = False,
        allowExternalContentLinks: bool = False,
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
        includeHtml: bool = False,
        includeRawHtml: bool = False,
        replaceAllPathsWithAbsolutePaths: bool = True,
    ) -> Dict[str, Any]:
        """
        Initiate a crawl for multiple URLs using the Firecrawl v1 API (Self-Hosted compatible).

        Reference: https://docs.firecrawl.dev/api-reference/endpoint/crawl

        :param url: The starting URL for the crawl. (required)
        :param includes: URL patterns to include in the crawl. Default: None.
        :param excludes: URL patterns to exclude from the crawl. Default: None.
        :param generateImgAltText: Generate alt text for images using LLMs (requires paid plan). Default: False.
        :param returnOnlyUrls: Return only found URLs, without content. Default: False.
        :param maxDepth: Maximum crawl depth from the base URL. Default: 123.
        :param mode: Crawling mode: `default` or `fast` (faster, less accurate). Default: "default".
        :param ignoreSitemap: Ignore the website's sitemap. Default: False.
        :param limit: Maximum number of pages to crawl. Default: 10000.
        :param allowBackwardCrawling: Allow crawling to previously linked pages. Default: False.
        :param allowExternalContentLinks: Allow following links to external websites. Default: False.
        :param formats: List of formats to return for each scraped page. Default: ["markdown"].
        :param onlyMainContent: Return only the main content of each scraped page. Default: False.
        :param includeTags: List of CSS selectors to include for each scraped page. Default: None.
        :param excludeTags: List of CSS selectors to exclude for each scraped page. Default: None.
        :param headers: Custom headers for the request to each scraped page. Default: None.
        :param waitFor: Wait time in milliseconds for dynamic content on each scraped page. Default: 0.
        :param timeout: Request timeout in milliseconds for each scraped page. Default: 30000.
        :param jsonOptions: Options for JSON extraction on each scraped page. Default: None.
        :param removeBase64Images: Remove base64 encoded images from each scraped page. Default: False.
        :param blockAds: Block ads during scraping of each page. Default: False.
        :param includeHtml: Include the full HTML content for each scraped page. Default: False.
        :param includeRawHtml: Include the raw HTML content for each scraped page. Default: False.
        :param replaceAllPathsWithAbsolutePaths: Replace all relative paths with absolute paths for each scraped page. Default: True.
        :return: A dictionary containing the `jobId` for the initiated crawl.
        :raises httpx.HTTPStatusError: If the API returns a 4xx or 5xx status code.
        :raises httpx.RequestError: If a network or other request error occurs.

        Example Request:
            tool.crawl(
                url="http://example.com",
                excludes=["/login"],
                limit=10,
                onlyMainContent=True
            )

        Example Response:
            {
                "jobId": "some-unique-job-id-string"
            }
        """
        payload = {
            "url": url,
            "crawlerOptions": {
                "includes": includes,
                "excludes": excludes,
                "generateImgAltText": generateImgAltText,
                "returnOnlyUrls": returnOnlyUrls,
                "maxDepth": maxDepth,
                "mode": mode,
                "ignoreSitemap": ignoreSitemap,
                "limit": limit,
                "allowBackwardCrawling": allowBackwardCrawling,
                "allowExternalContentLinks": allowExternalContentLinks,
            },
            "pageOptions": {
                "formats": formats,
                "onlyMainContent": onlyMainContent,
                "includeTags": includeTags,
                "excludeTags": excludeTags,
                "headers": headers,
                "waitFor": waitFor,
                "timeout": timeout,
                "jsonOptions": jsonOptions,
                "removeBase64Images": removeBase64Images,
                "blockAds": blockAds,
                "includeHtml": includeHtml,
                "includeRawHtml": includeRawHtml,
                "replaceAllPathsWithAbsolutePaths": replaceAllPathsWithAbsolutePaths,
            },
        }

        # Remove None values from payload, including nested dictionaries
        payload = {k: v for k, v in payload.items() if v is not None}
        if "crawlerOptions" in payload:
            payload["crawlerOptions"] = {
                k: v for k, v in payload["crawlerOptions"].items() if v is not None
            }
        if "pageOptions" in payload:
            payload["pageOptions"] = {
                k: v for k, v in payload["pageOptions"].items() if v is not None
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
        includeHtml: bool = False,
        includeRawHtml: bool = False,
        replaceAllPathsWithAbsolutePaths: bool = True,
        mode: str = "markdown",
    ) -> Dict[str, Any]:
        """
        Initiate a batch scrape for multiple URLs using the Firecrawl v1 API (Self-Hosted compatible).

        Reference: https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape

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
        :param includeHtml: Include the full HTML content in the response. Default: False.
        :param includeRawHtml: Include the raw HTML content in the response. Default: False.
        :param replaceAllPathsWithAbsolutePaths: Replace all relative paths with absolute paths. Default: True.
        :param mode: Extraction mode (e.g., "markdown", "text", "html"). Default: "markdown".
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
            "webhook": webhook,
            "ignoreInvalidURLs": ignoreInvalidURLs,
            "pageOptions": {  # Nest page options under 'pageOptions' key
                "formats": formats,
                "onlyMainContent": onlyMainContent,
                "includeTags": includeTags,
                "excludeTags": excludeTags,
                "headers": headers,
                "waitFor": waitFor,
                "timeout": timeout,
                "jsonOptions": jsonOptions,
                "removeBase64Images": removeBase64Images,
                "blockAds": blockAds,
                "includeHtml": includeHtml,
                "includeRawHtml": includeRawHtml,
                "replaceAllPathsWithAbsolutePaths": replaceAllPathsWithAbsolutePaths,
                "mode": mode,
            }
        }

        # Remove None values from payload
        payload = {k: v for k, v in payload.items() if v is not None}

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
        includeHtml: bool = False,
        includeRawHtml: bool = False,
        replaceAllPathsWithAbsolutePaths: bool = True,
        mode: str = "markdown",
    ) -> Dict[str, Any]:
        """
        Extract structured data from URLs using the Firecrawl v1 API (Self-Hosted compatible).

        Reference: https://docs.firecrawl.dev/api-reference/endpoint/extract

        :param urls: The list of URLs to extract data from. URLs should be in glob format. (required)
        :param prompt: The prompt to use for extraction. Default: None.
        :param schema: The JSON schema to use for extraction. Default: None.
        :param ignoreSitemap: Ignore the website's sitemap. Default: False.
        :param includeSubdomains: Include subdomains in the extraction. Default: True.
        :param showSources: Include the source URLs in the response. Default: False.
        :param formats: List of formats to return for each scraped page. Default: ["markdown"].
        :param onlyMainContent: Return only the main content of each scraped page. Default: False.
        :param includeTags: List of CSS selectors to include for each scraped page. Default: None.
        :param excludeTags: List of CSS selectors to exclude for each scraped page. Default: None.
        :param headers: Custom headers for the request to each scraped page. Default: None.
        :param waitFor: Wait time in milliseconds for dynamic content on each scraped page. Default: 0.
        :param timeout: Request timeout in milliseconds for each scraped page. Default: 30000.
        :param jsonOptions: Options for JSON extraction on each scraped page. Default: None.
        :param removeBase64Images: Remove base64 encoded images from each scraped page. Default: False.
        :param blockAds: Block ads during scraping of each page. Default: False.
        :param includeHtml: Include the full HTML content for each scraped page. Default: False.
        :param includeRawHtml: Include the raw HTML content for each scraped page. Default: False.
        :param replaceAllPathsWithAbsolutePaths: Replace all relative paths with absolute paths for each scraped page. Default: True.
        :param mode: Extraction mode (e.g., "markdown", "text", "html"). Default: "markdown".
        :return: A dictionary with the extraction results.
        :raises httpx.HTTPStatusError: If the API returns a 4xx or 5xx status code.
        :raises httpx.RequestError: If a network or other request error occurs.

        Example Request:
            tool.extract(
                urls=["https://example.com/*"],
                prompt="Extract the main article content.",
                schema={"type": "object", "properties": {"content": {"type": "string"}}}
            )

        Example Response:
            {
              "success": True,
              "data": [
                {
                  "url": "<string>",
                  "content": "<string>",
                  "source": "<string>" # Only if showSources is True
                }
              ]
            }
        """
        payload = {
            "urls": urls,
            "prompt": prompt,
            "schema": schema,
            "ignoreSitemap": ignoreSitemap,
            "includeSubdomains": includeSubdomains,
            "showSources": showSources,
            "scrapeOptions": {
                "formats": formats,
                "onlyMainContent": onlyMainContent,
                "includeTags": includeTags,
                "excludeTags": excludeTags,
                "headers": headers,
                "waitFor": waitFor,
                "timeout": timeout,
                "jsonOptions": jsonOptions,
                "removeBase64Images": removeBase64Images,
                "blockAds": blockAds,
                "includeHtml": includeHtml,
                "includeRawHtml": includeRawHtml,
                "replaceAllPathsWithAbsolutePaths": replaceAllPathsWithAbsolutePaths,
                "mode": mode,
            },
        }

        # Remove None values from payload, including nested scrapeOptions
        payload = {k: v for k, v in payload.items() if v is not None}
        if "scrapeOptions" in payload:
            payload["scrapeOptions"] = {
                k: v for k, v in payload["scrapeOptions"].items() if v is not None
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
    ) -> Dict[str, Any]:
        """
        Map a website's links using the Firecrawl v1 API (Self-Hosted compatible).

        Reference: https://docs.firecrawl.dev/api-reference/endpoint/map

        :param url: The base URL to start mapping from. (required)
        :param search: Search query to filter links. Default: None.
        :param ignoreSitemap: Ignore the website sitemap when mapping. Default: True.
        :param sitemapOnly: Only return links found in the website sitemap. Default: False.
        :param includeSubdomains: Include subdomains of the website. Default: False.
        :param limit: Maximum number of links to return. Default: 5000.
        :param timeout: Timeout in milliseconds. Default: None.
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
            "search": search,
            "ignoreSitemap": ignoreSitemap,
            "sitemapOnly": sitemapOnly,
            "includeSubdomains": includeSubdomains,
            "limit": limit,
            "timeout": timeout,
        }

        # Remove None values from payload
        payload = {k: v for k, v in payload.items() if v is not None}

        logging.info("Sending v1 map request with payload: %s", payload)
        # Use HTTPClient to make the request
        response_data = self.http_client.sync_request(
            "POST",
            "map",
            json=payload
        )
        logging.info("Map initiated for URL: %s", url)
        return response_data
# <<< NEW METHOD START >>>
    def _format_metadata_md(self, metadata: Dict[str, Any]) -> str:
        """Converts metadata dictionary to a Markdown formatted string."""
        # Logic from mcp_scrape_server._metadata_to_markdown
        title = metadata.get("title") or metadata.get("ogTitle") or "Sem Título"
        description = (
            metadata.get("description") or metadata.get("ogDescription") or "Sem descrição"
        )
        url = (
            metadata.get("url") or metadata.get("ogUrl") or metadata.get("sourceURL") or ""
        )
        language = metadata.get("language") or "N/A"
        # Simplified author and tags for brevity, can be expanded if needed
        author = metadata.get("author") or "Desconhecido"
        tags = metadata.get("tags") or ""
        favicon = metadata.get("favicon")
        og_image = metadata.get("ogImage") or metadata.get("og:image")

        markdown_lines = [
            "# Page Metadata",
            "",
            f"**Title**: {title}",
            "",
            f"**Description**: {description}",
            "",
        ]
        if url:
            markdown_lines.append(f"**URL**: [{url}]({url})")
            markdown_lines.append("")
        markdown_lines.append(f"**Language**: {language}")
        markdown_lines.append("")
        markdown_lines.append(f"**Author**: {author}")
        markdown_lines.append("")
        if tags:
            markdown_lines.append(f"**Tags**: {tags}") # Assuming tags is a string here
            markdown_lines.append("")
        if favicon:
            markdown_lines.append(f"**Favicon**: ![Favicon]({favicon})")
            markdown_lines.append("")
        if og_image:
            markdown_lines.append(f"**Image**: ![Image]({og_image})")
            markdown_lines.append("")

        return "\n".join(markdown_lines)

    def _format_links_md(self, links: list[str]) -> str:
        """Converts a list of links to a Markdown formatted list."""
        # Logic from mcp_scrape_server._links_to_markdown
        if not links:
            return "# Page Links\n\nNo links found."
        markdown_lines = ["# Page Links", ""]
        for link in links:
            markdown_lines.append(f"- [{link}]({link})")
        return "\n".join(markdown_lines)

    def _format_scrape_result_md(self, scrape_result: Dict[str, Any]) -> str:
        """Converts the full scrape result dictionary to Markdown format."""
        # Logic from mcp_scrape_server._scrape_result_to_markdown
        try:
            if not isinstance(scrape_result, dict):
                return f"# Error: Invalid scrape result type: {type(scrape_result)}"

            if not scrape_result.get("success"):
                 error_message = scrape_result.get("error", "Unknown error during scrape.")
                 return f"# Scrape Failed\nError: {error_message}"

            data = scrape_result.get("data", {})
            if not isinstance(data, dict):
                 # Handle cases where data might be missing or not a dict even if success is true
                 return "# Error: Missing or invalid 'data' field in successful scrape result."

            # Extract relevant parts, default to empty values if keys are missing
            markdown_content = data.get("markdown", "")
            metadata_dict = data.get("metadata", {})
            links_list = data.get("links", []) # Assuming 'links' key based on v1 scrape response

            if not markdown_content and not metadata_dict and not links_list:
                 return "# No content, metadata, or links found in scrape data."

            # Format sections
            formatted_metadata = self._format_metadata_md(metadata_dict) if metadata_dict else "# Page Metadata\n\nNo metadata found."
            formatted_links = self._format_links_md(links_list) if links_list else "# Page Links\n\nNo links found."
            formatted_content = f"# Page Contents\n\n{markdown_content}" if markdown_content else "# Page Contents\n\nNo main content found."


            return f"""{formatted_content}
---
{formatted_metadata}
---
{formatted_links}"""
        except Exception as e:
            logging.error("Error processing scrape result for Markdown formatting: %s", e, exc_info=True)
            return f"# Error processing scrape result\nError: {str(e)}"

    def scrape_formatted(
        self,
        url: str,
        tags_to_remove: list[str] = [],
        timeout: int = 30000,
        # Include other relevant flattened params from scrape if needed by users of this method
        onlyMainContent: bool = True, # Defaulting to True as in MCP server
        mode: str = "markdown", # Defaulting to markdown
        # Add other params like waitFor, headers etc. if they should be configurable here
    ) -> str:
        """
        Scrapes a webpage, extracts key information, and returns it as a formatted Markdown string.
        Mimics the behavior of the scrape tool in the MCP server.

        :param url: The URL of the webpage to scrape.
        :param tags_to_remove: A list of HTML tags/selectors to remove (e.g., ['script', '.ad']). Defaults to an empty list, but common nuisance tags might be added internally if desired.
        :param timeout: Maximum time in milliseconds to wait for scraping. Defaults to 30000.
        :param onlyMainContent: Extract only the main content. Defaults to True.
        :param mode: Extraction mode. Defaults to "markdown".
        :return: A Markdown string containing the formatted page content, metadata, and links, or an error message.
        """
        # Add default tags to remove if not provided, similar to MCP server?
        # Example: effective_tags_to_remove = tags_to_remove or []
        # for t in ["script", ".ad", "#footer"]:
        #     if t not in effective_tags_to_remove:
        #         effective_tags_to_remove.append(t)
        # For now, we'll use exactly what's passed or the default empty list.

        logging.info("Initiating formatted scrape for URL: %s", url)
        try:
            # Call the internal scrape method with appropriate parameters
            scrape_result = self.scrape(
                url=url,
                formats=[mode], # Ensure the requested mode is fetched
                onlyMainContent=onlyMainContent,
                excludeTags=tags_to_remove, # Map tags_to_remove to excludeTags
                timeout=timeout,
                mode=mode,
                # Pass other parameters if added to the signature
            )
            # Format the result using the helper method
            formatted_markdown = self._format_scrape_result_md(scrape_result)
            logging.info("Formatted scrape successful for URL: %s", url)
            return formatted_markdown
        except Exception as e:
            # Catch exceptions during the scrape call itself or formatting
            logging.error("Error during formatted scrape for URL %s: %s", url, e, exc_info=True)
            return f"# Error scraping {url}\nError: {str(e)}"
    # <<< NEW METHOD END >>>

    def scrape_multiple(
        self,
        urls: list[str],
        tags_to_remove: list[str] = [],
        timeout: int = 30000,
        onlyMainContent: bool = True,
        mode: str = "markdown",
        max_workers: int | None = None # Allow configuring max workers
    ) -> list[str]:
        """
        Scrapes multiple webpages in parallel using threads, extracts key information,
        and returns a list of formatted Markdown strings.

        Uses ThreadPoolExecutor for synchronous parallel execution.

        :param urls: List of URLs to scrape.
        :param tags_to_remove: A list of HTML tags/selectors to remove for all URLs.
        :param timeout: Maximum time in milliseconds to wait for each scrape.
        :param onlyMainContent: Extract only the main content for all URLs.
        :param mode: Extraction mode for all URLs.
        :param max_workers: Maximum number of threads to use. Defaults to None (Python's default).
        :return: A list of Markdown strings (one per URL, in the original order) containing formatted content or error messages.
        """
        if not urls:
            return []

        results = [""] * len(urls) # Pre-allocate list to store results in order
        url_to_index = {url: i for i, url in enumerate(urls)} # Map URL to original index

        # Define a wrapper function to pass arguments and store result at correct index
        def scrape_and_store(url: str):
            try:
                result_md = self.scrape_formatted(
                    url=url,
                    tags_to_remove=tags_to_remove,
                    timeout=timeout,
                    onlyMainContent=onlyMainContent,
                    mode=mode
                )
                index = url_to_index[url]
                results[index] = result_md
            except Exception as e:
                logging.error("Exception in scrape_and_store thread for %s: %s", url, e, exc_info=True)
                index = url_to_index[url]
                results[index] = f"# Error scraping {url}\nError: {str(e)}"

        logging.info("Starting parallel scrape for %d URLs", len(urls))
        # Use ThreadPoolExecutor for parallel execution
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_url = {executor.submit(scrape_and_store, url): url for url in urls}

            # Wait for all futures to complete (gather results implicitly via scrape_and_store)
            for future in concurrent.futures.as_completed(future_to_url):
                url_done = future_to_url[future]
                try:
                    # We don't need the result from future.result() as it's stored directly
                    future.result() # Still call result() to raise exceptions if any occurred within the thread task itself
                    logging.debug("Scrape task completed for URL: %s", url_done)
                except Exception as exc:
                    # This catches exceptions raised *by the future itself*,
                    # though scrape_and_store should handle most scrape errors.
                    logging.error("Exception raised by future for URL %s: %s", url_done, exc, exc_info=True)
                    # Ensure an error message is stored if not already handled
                    index = url_to_index[url_done]
                    if not results[index].startswith("# Error"):
                         results[index] = f"# Error during future execution for {url_done}\nError: {str(exc)}"

        logging.info("Parallel scrape finished for %d URLs", len(urls))
        return results

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
        jsonOptions: dict | None = None,
        removeBase64Images: bool = False,
        blockAds: bool = False,
        includeHtml: bool = False,
        includeRawHtml: bool = False,
        replaceAllPathsWithAbsolutePaths: bool = True,
        mode: str = "markdown",
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
        :param jsonOptions: Options for JSON extraction on each scraped search result. Default: None.
        :param removeBase64Images: Remove base64 encoded images from each scraped search result. Default: False.
        :param blockAds: Block ads during scraping of each search result. Default: False.
        :param includeHtml: Include the full HTML content for each scraped search result. Default: False.
        :param includeRawHtml: Include the raw HTML content for each scraped search result. Default: False.
        :param replaceAllPathsWithAbsolutePaths: Replace all relative paths with absolute paths for each scraped search result. Default: True.
        :param mode: Extraction mode for each scraped search result (e.g., "markdown", "text", "html"). Default: "markdown".
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
            "searchOptions": {
                "limit": limit,
                "tbs": tbs,
                "lang": lang,
                "country": country,
                "timeout": timeout,
            },
            "scrapeOptions": {
                "formats": formats,
                "onlyMainContent": onlyMainContent,
                "includeTags": includeTags,
                "excludeTags": excludeTags,
                "headers": headers,
                "waitFor": waitFor,
                "jsonOptions": jsonOptions,
                "removeBase64Images": removeBase64Images,
                "blockAds": blockAds,
                "includeHtml": includeHtml,
                "includeRawHtml": includeRawHtml,
                "replaceAllPathsWithAbsolutePaths": replaceAllPathsWithAbsolutePaths,
                "mode": mode,
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
