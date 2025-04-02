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
        self.base_url = base_url or os.environ.get('FBPY_FIRECRAWL_BASE_URL', 'https://api.firecrawl.dev/v0')
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self._headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36', 
            'Content-Type': 'application/json'
        }
        token = token or os.environ.get('FBPY_FIRECRAWL_API_KEY')
        if token is not None and token!= '':
            self._headers['Authorization'] = f'Bearer {token}'
        self.session.headers.update(self._headers)
        logging.info("Initialized FireCrawlTool with base URL %s", base_url)

    def scrape(self, url: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Scrape a single URL.

        :param url: The URL to scrape.
        :param kwargs: Optional arguments for page scraping, extractor, and timeout.
            - pageOptions (dict): Options for page interaction.
                - headers (dict): HTTP headers for the page request. Default: {}. Optional: Yes.
                - includeHtml (bool): Include HTML content of the page. Default: false. Optional: Yes.
                - includeRawHtml (bool): Include raw HTML content of the page. Default: false. Optional: Yes.
                - onlyIncludeTags (List[str]): Include only specific tags, classes, and ids. Default: []. Optional: Yes.
                - onlyMainContent (bool): Return only the main content of the page. Default: false. Optional: Yes.
                - removeTags (List[str]): Remove specific tags, classes, and ids. Default: []. Optional: Yes.
                - replaceAllPathsWithAbsolutePaths (bool): Replace all relative paths with absolute paths. Default: false. Optional: Yes.
                - screenshot (bool): Include a screenshot of the top of the page. Default: false. Optional: Yes.
                - fullPageScreenshot (bool): Include a screenshot of the entire page. Default: false. Optional: Yes.
                - waitFor (int): Wait a specific time for the page to load (in ms). Default: 0. Optional: Yes.
            - extractorOptions (dict): Options for content extraction.
                - mode (str): Extraction mode ('markdown', 'llm-extraction'). Default: "markdown". Optional: Yes.
                - extractionPrompt (str): Prompt for LLM information extraction. Default: None. Optional: Yes (Required for `llm-extraction` mode).
                - extractionSchema (dict): Schema for data to be extracted with LLM. Default: None. Optional: Yes (Required for `llm-extraction` mode).
            - timeout (int): Request timeout in milliseconds. Default: 30000. Optional: Yes.
        :return: A dictionary with the scrape results.

        Example Request:
            tool.scrape(
                url="http://example.com",
                pageOptions={
                    "onlyMainContent": True,
                    "includeHtml": False
                },
                extractorOptions={
                    "mode": "markdown"
                },
                timeout=30000
            )

        Example Response:
            {
                "success": True,
                "data": {
                    "markdown": "...",
                    "content": "...",
                    "metadata": {
                        "title": "Example Domain",
                        "description": "...",
                        "language": "en",
                        "sourceURL": "http://example.com"
                    },
                    # ... other fields like html, linksOnPage etc. depending on options
                },
                "returnCode": 200 # or other status codes
            }
        """
        payload = {'url': url, **kwargs}
        logging.info("Sending scrape request with payload: %s", payload)
        response = self.session.post(f'{self.base_url}/scrape', json=payload)
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
        payload = {'url': url, **kwargs}

        page_options = payload.get('pageOptions', {})
        page_options['headers'] = self._headers
        payload['pageOptions'] = page_options

        logging.info("Sending crawl request with payload: %s", payload)
        response = self.session.post(f'{self.base_url}/crawl', json=payload)
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
        response = self.session.get(f'{self.base_url}/crawl/status/{job_id}')
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
        response = self.session.delete(f'{self.base_url}/crawl/cancel/{job_id}')
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
        payload = {'query': query, **kwargs}
        logging.info("Sending search request with query: %s", query)
        response = self.session.post(f'{self.base_url}/search', json=payload)
        try:
            response.raise_for_status()
            result = response.json()
            logging.info("Search successful for query %s", query)
            return result
        except requests.RequestException as e:
            logging.error("Search request failed: %s", e)
            raise
