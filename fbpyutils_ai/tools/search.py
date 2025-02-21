import os
import requests
from typing import Dict, Optional, Union, List

from fbpyutils_ai import logging


class SearXNGTool():
    """
    Ferramenta para busca usando a API REST do SearXNG.

    Integração com a API do SearXNG para realizar buscas programáticas.
    Suporta diferentes categorias de busca, idiomas e níveis de segurança.
    """
    SAFESEARCH_NONE = 0
    SAFESEARCH_MODERATE = 1
    SAFESEARCH_STRICT = 2

    CATEGORIES = (
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
    )

    def __init__(self, base_url: str = None, api_key: str = None):
        """
        Inicializa a ferramenta SearXNGTool.

        Args:
            base_url (str, optional): URL base da API do SearXNG.
                Se não fornecido, usa a variável de ambiente 'FBPY_SEARXNG_API_KEY' ou 'https://searxng.site' como padrão.
            api_key (str, optional): Chave de API para autenticação no SearXNG.
                Se não fornecida, usa a variável de ambiente 'SEARXNG_API_KEY'.
        """
        self.base_url = base_url or os.getenv('FBPY_SEARXNG_API_KEY', 'https://searxng.site')
        self.api_key = api_key or os.getenv('SEARXNG_API_KEY', None)
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
        """
        Realiza uma busca no SearXNG.

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
        """
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
            if c.lower() in self.CATEGORIES:
                params[f'category_{c.lower()}'] = 1

        try:
            url = f"{self.base_url}/search"
            logging.debug(f"Parâmetros da busca: query=%s, method=%s, categories=%s, language=%s, safesearch=%s, time_range=%s", query, method, categories, language, safesearch, time_range)
            logging.debug(f"URL da requisição: %s", url)
            verify_ssl = url.startswith('https')
            if method == 'GET':
                method_call = requests.get
            elif method == 'POST':
                method_call = requests.post
            else:
                raise ValueError(f"Método inválido: {method}. Use 'GET' ou 'POST'.")
            response = method_call(url, params=params, headers=self.headers, verify=verify_ssl)
            response.raise_for_status()  # Raise an exception for HTTP errors
            logging.debug(f"Status code da resposta: %s", response.status_code)
            results = response.json().get('results', [])
            return results
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro na requisição ao SearXNG: %s", e) # Log de erro detalhado
            return []
