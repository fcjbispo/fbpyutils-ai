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
        _headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36', 
            'Content-Type': 'application/json'
        }
        token = token or os.environ.get('FBPY_FIRECRAWL_API_KEY')
        if token is not None and token!= '':
            _headers['Authorization'] = f'Bearer {token}'
        self.session.headers.update(_headers)
        logging.info("Initialized FireCrawlTool with base URL %s", base_url)

    def scrape(self, url: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Scrape a single URL.

        :param url: The URL to scrape.
        :param kwargs: Optional arguments for page scraping, extractor, and timeout.
            : param pageOptions.headers (objeto): Cabeçalhos HTTP para a requisição da página, Default: {}, Obrigatório: Não
            : param pageOptions.includeHtml (boolean): Incluir conteúdo HTML da página, Default: false, Obrigatório: Não
            : param pageOptions.includeRawHtml (boolean): Incluir conteúdo HTML bruto da página, Default: false, Obrigatório: Não
            : param pageOptions.onlyIncludeTags (string[]): Incluir apenas determinados tags, classes e ids, Default: [], Obrigatório: Não
            : param pageOptions.onlyMainContent (boolean): Retornar apenas o conteúdo principal da página, Default: false, Obrigatório: Não
            : param pageOptions.removeTags (string[]): Remover determinados tags, classes e ids, Default: [], Obrigatório: Não
            : param pageOptions.replaceAllPathsWithAbsolutePaths (boolean): Substituir todos os caminhos relativos por caminhos absolutos, Default: false, Obrigatório: Não
            : param pageOptions.screenshot (boolean): Incluir uma captura de tela da parte superior da página, Default: false, Obrigatório: Não
            : param pageOptions.fullPageScreenshot (boolean): Incluir uma captura de tela de toda a página, Default: false, Obrigatório: Não
            : param pageOptions.waitFor (integer): Esperar um tempo específico para a página carregar, Default: 0, Obrigatório: Não
            : param extractorOptions.mode (enum<string>): Modo de extração, Default: "markdown", Obrigatório: Não
            : param extractorOptions.extractionPrompt (string): Prompt para extração de informações com LLM, Default: -, Obrigatório: Não (Obrigatório para `llm-extraction` mode)
            : param extractorOptions.extractionSchema (objeto): Schema para dados a serem extraídos com LLM, Default: -, Obrigatório: Não (Obrigatório para `llm-extraction` mode)
            : param timeout (integer): Tempo de espera para a requisição em milissecos, Default: 30000, Obrigatório: Não
        :return: A dictionary with the scrape results.

        Example:
            scrape(
                url": "http:///example.com",
                pageOptions": {
                    "onlyMainContent": True,
                    "includeHtml": False
                },
                extractorOptions": {
                    "mode": "markdown",
                    "extractionPrompt": "Extract the main content of the page.",
                    "extractionSchema": {}
                },
                timeout=300"
            )
            response: {
                "success": "boolean",
                "data": {
                    "markdown": "string",
                    "content": "string",
                    "html": "string",
                    "metadata": {
                        "title": "string",
                        "description": "string",
                        "language": "string",
                        "sourceURL": "string"
                    }
                }
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
        :param kwargs: Optional arguments for page scraping, extractor, and timeout.
            : param crawlerOptions.includes (string[]): Padrões de URL a serem incluídos no crawling, Default: [], Obrigatório: Não
            : param crawlerOptions.excludes (string[]): Padrões de URL a serem excluídos do crawling, Default: [], Obrigatório: Não
            : param crawlerOptions.generateImgAltText (boolean): Gerar texto alternativo para imagens usando LLMs (requer plano pago), Default: false, Obrigatório: Não
            : param crawlerOptions.returnOnlyUrls (boolean): Retornar apenas URLs encontradas, sem conteúdo, Default: false, Obrigatório: Não
            : param crawlerOptions.maxDepth (integer): Profundidade máxima de crawling a partir da URL base, Default: 123, Obrigatório: Não
            : param crawlerOptions.mode (enum<string>): Modo de crawling: `default` ou `fast` (mais rápido, menos preciso), Default: "default", Obrigatório: Não
            : param crawlerOptions.ignoreSitemap (boolean): Ignorar o sitemap do website, Default: false, Obrigatório: Não
            : param crawlerOptions.limit (integer): Número máximo de páginas a serem crawled, Default: 10000, Obrigatório: Não
            : param crawlerOptions.allowBackwardCrawling (boolean): Permitir crawling para páginas previamente linkadas, Default: false, Obrigatório: Não
            : param crawlerOptions.allowExternalContentLinks (boolean): Permitir seguir links para websites externos, Default: false, Obrigatório: Não
            : param pageOptions.headers (objeto): Cabeçalhos HTTP para as requisições de página, Default: {}, Obrigatório: Não
            : param pageOptions.includeHtml (boolean): Incluir conteúdo HTML das páginas crawled, Default: false, Obrigatório: Não
            : param pageOptions.includeRawHtml (boolean): Incluir HTML bruto das páginas crawled, Default: false, Obrigatório: Não
            : param pageOptions.onlyIncludeTags (): Incluir apenas tags, classes e ids específicos, Default: [], Obrigatório: 0
            : param pageOptions.onlyMainContent (boolean): Retornar apenas o conteúdo principal das páginas, Default: false, Obrigatório: Não
            : param pageOptions.removeTags (string[]): Remover tags, classes e ids específicos das páginas, Default: [], Obrigatório: Não
            : param pageOptions.replaceAllPathsWithAbsolutePaths (boolean): Substituir paths relativos por absolutos nas páginas, Default: false, Obrigatório: Não
            : param pageOptions.screenshot (boolean): Incluir screenshot do topo de cada página crawled, Default: false, Obrigatório: Não
            : param pageOptions.fullPageScreenshot (boolean): Incluir screenshot da página inteira de cada página crawled, Default: false, Obrigatório: Não
            : param pageOptions.waitFor (integer): Tempo para aguardar carregamento de cada página crawled, Default: 0, Obrigatório: Não
        :return: A dictionary with the scrape results.

        Example:
        request_body: {
            "url": "string",
            "crawlerOptions": {
                "includes": ["string"],
                "excludes": ["string"],
                "generateImgAltText": "boolean",
                "returnOnlyUrls": "boolean",
                "maxDepth": "integer",
                "mode": "string",
                "limit": "integer"
            },
            "pageOptions": {
                "onlyMainContent": "boolean",
                "includeHtml": "boolean"
            }
        }
        response: {
            "jobId": "string"
        }
        """
        payload = {'url': url, **kwargs}
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

        Example:
        request_body: {
            "query": "string",
            "pageOptions": {
                "onlyMainContent": "boolean",
                "fetchPageContent": "boolean",
                "includeHtml": "boolean"
            },
            "searchOptions": {
                "limit": "integer"
            }
        }
        response: {
            "success": "boolean",
            "data": [{
                "url": "string",
                "markdown": "string",
                "content": "string",
                "metadata": {
                "title": "string",
                "description": "string",
                "language": "string",
                "sourceURL": "string"
                }
            }]
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