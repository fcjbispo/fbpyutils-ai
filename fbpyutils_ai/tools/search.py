import os
import requests
from urllib.parse import urlencode
from typing import Dict, Optional, Union, List

from fbpyutils_ai import logging


class SearXNGTool():
    """Ferramenta para busca usando a API REST do SearXNG."""
    SAFESEARCH_NONE = 0
    SAFESEARCH_MODERATE = 1
    SAFESEARCH_STRICT = 2

    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.getenv('TOOL_SEARXNG_API_BASE_URL', 'https://searxng.site')
        self.api_key = api_key or os.getenv('TOOL_SEARXNG_API_KEY', None)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            "Content-Type": "application/json",
        }
        if self.api_key:
            self.headers['Authorization'] = f'Bearer {self.api_key}'
        logging.info(f"Inicializando SearXNGTool com base_url={self.base_url} e api_key={self.api_key}")

    def search(
            self, 
            query: str,
            method: str = 'GET',
            categories: Optional[Union[str, List[str]]] = ['general'],
            language: str = 'auto',
            time_range: str = None,
            safesearch: int = SAFESEARCH_NONE
    ) -> List[Dict]:
        method = method or 'GET'
        if method not in ('GET', 'POST'):
            raise ValueError(f"Método inválido: {method}. Use 'GET' ou 'POST'.")
        if len(categories) == 0:
            categories = ['general']
        language = language or 'auto'
        if language not in ('auto', 'en', 'pt', 'es', 'fr', 'de', 'it', 'ru', 'nl', 'pl', 'vi', 'id', 'ar', 'th', 'zh-cn', 'ja', 'ko', 'tr', 'cs', 'da', 'fi', 'hu', 'no', 'sv', 'uk'):
            raise ValueError(f"Idioma inválido: {language}. Use 'auto' ou um código ISO 639-1 válido.")
        safesearch = safesearch or self.SAFESEARCH_NONE
        if safesearch not in (self.SAFESEARCH_NONE, self.SAFESEARCH_MODERATE, self.SAFESEARCH_STRICT):
            raise ValueError(f"Nível de segurança inválido: {safesearch}. Use 'SAFESEARCH_NONE|0', 'SAFESEARCH_MODERATE|1' ou 'SAFESEARCH_STRICT|2'.")

        params = {
            'q': query,
            'format': 'json',
            'language': language,
            'safesearch': safesearch,
            'time_range': time_range,
            'pageno': 1
        }

        for c in categories:
            if c.lower() in (
                'general',
                'images',
                'videos',
                'news',
                'map',
                'music',
                'it',
                'science',
                'files',
                'social media',
            ):
                params[f'category_{c.lower()}'] = 1

        try:
            url = self.base_url
            verify_ssl = url.startswith('https')
            if method == 'GET':
                method_call = requests.get
            elif method == 'POST':
                method_call = requests.post
            else:
                raise ValueError(f"Método inválido: {method}. Use 'GET' ou 'POST'.")
            response = method_call(url, params=params, headers=self.headers, verify=verify_ssl) # Desabilitar verificação SSL
            response.raise_for_status()  # Raise an exception for HTTP errors
            results = response.json().get('results', [])
            return results
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro na requisição ao SearXNG: {e}") # Log de erro detalhado
            return []
