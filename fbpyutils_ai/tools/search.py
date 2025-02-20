from abc import ABC, abstractmethod
from typing import Dict, Optional, Union, List
import requests
import logging

logging.basicConfig(level=logging.DEBUG)  # Configuração básica de logging

class SearchTool(ABC):
    """Classe abstrata para ferramentas de busca."""

    @abstractmethod
    def __init__(self, base_url: str, **kwargs):
        """Inicializa a ferramenta de busca.

        Args:
            base_url (str): URL base da API de busca.
            **kwargs: Argumentos adicionais para configuração.
        """
        self.base_url = base_url
        self.config = kwargs

    @abstractmethod
    def search(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Realiza uma busca.

        Args:
            query (str): Termo de busca.
            params (Optional[Dict]): Parâmetros adicionais da API.

        Returns:
            List[Dict]: Lista de resultados da busca.
        """
        pass


class SearXNGTool(SearchTool):
    """Ferramenta para busca usando a API REST do SearXNG."""

    def __init__(self, base_url: str, **kwargs):
        """Inicializa a ferramenta SearXNG.

        Args:
            base_url (str): URL base do serviço SearXNG.
            **kwargs: Argumentos adicionais para configuração.
        """
        super().__init__(base_url, **kwargs)

    def search(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Realiza uma busca no SearXNG.

        Args:
            query (str): Termo de busca.
            params (Optional[Dict]): Parâmetros de busca do SearXNG.
                                     Consulte a documentação da API para opções.

        Returns:
            List[Dict]: Lista de resultados da busca formatados.
        """
        default_params = {
            'q': query,
            'format': 'json'
        }
        all_params = default_params.copy()
        if params:
            all_params.update(params)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            logging.debug(f"URL da requisição: {self.base_url}") # Log da URL
            response = requests.get(self.base_url, params=all_params, headers=headers, verify=False) # Desabilitar verificação SSL
            response.raise_for_status()  # Raise an exception for HTTP errors
            logging.debug(f"Status code da resposta: {response.status_code}") # Log do status code
            logging.debug(f"Conteúdo da resposta: {response.text}") # Log do conteúdo da resposta
            results = response.json().get('results', [])
            return results
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro na requisição ao SearXNG: {e}") # Log de erro detalhado
            return []
