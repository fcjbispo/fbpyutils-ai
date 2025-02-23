import os
import requests
from typing import Dict, Optional, Union, List
import logging  # Mantendo o import padrão do logging, mas usaremos fbpyutils_ai.logging

from fbpyutils_ai import logging  # Usando o logger configurado do projeto
import pandas as pd


class SearXNGUtils:
    """Utilitários para processamento de resultados do SearXNG."""

    @staticmethod
    def simplify_results(
        results: List[Dict[str, Union[str, int, float, None]]]
    ) -> List[Dict[str, Union[str, int, float, None]]]:
        """Simplifica a lista de resultados, extraindo campos principais.

        Args:
            results (List[Dict[str, Union[str, int, float, None]]]): Lista de resultados brutos do SearXNG.

        Returns:
            List[Dict[str, Union[str, int, float, None]]]: Lista de resultados simplificados,
            contendo 'url', 'title', 'content' e 'other_info'.
        """
        logging.debug("Entrando em simplify_results") # Log de entrada da função
        simplified_results = []
        if results:
            key_columns = ["url", "title", "content"]
            for result in results:
                result_record = {}
                for key in key_columns:
                    result_record[key] = result.get(key)
                other_keys = [k for k in result.keys() if k not in key_columns]
                result_record["other_info"] = {k: result[k] for k in other_keys}
                simplified_results.append(result_record)
        logging.debug("Saindo de simplify_results") # Log de saída da função
        return simplified_results

    @staticmethod
    def convert_to_dataframe(
        results: List[Dict[str, Union[str, int, float, None]]]
    ) -> pd.DataFrame:
        """Converte a lista de resultados do SearXNG em um DataFrame do pandas.

        Args:
            results (List[Dict[str, Union[str, int, float, None]]]): Lista de resultados do SearXNG.

        Returns:
            pd.DataFrame: DataFrame contendo os resultados da busca, com colunas 'url', 'title', 'content' e 'other_info'.
        """
        logging.debug("Entrando em convert_to_dataframe") # Log de entrada da função
        # Cria um dataframe vazio com as colunas desejadas
        df = pd.DataFrame(columns=["url", "title", "content", "other_info"])

        # Se houver resultados, preenche os valores nas colunas
        if results:
            results_list = SearXNGUtils.simplify_results(results)
            df = pd.DataFrame.from_dict(results_list, orient="columns")
        logging.debug("Saindo de convert_to_dataframe") # Log de saída da função
        return df


class SearXNGTool:
    """
    Ferramenta para busca usando a API REST do SearXNG.

    Integração com a API do SearXNG para realizar buscas programáticas.
    Suporta diferentes categorias de busca, idiomas e níveis de segurança.
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

    def __init__(self, base_url: str = None, api_key: str = None):
        """Inicializa a ferramenta SearXNGTool.

        Args:
            base_url (str, optional): URL base da API do SearXNG.
                Se não fornecido, usa a variável de ambiente 'FBPY_SEARXNG_BASE_URL' ou 'https://searxng.site' como padrão.
            api_key (str, optional): Chave de API para autenticação no SearXNG.
                Se não fornecida, usa a variável de ambiente 'SEARXNG_API_KEY'.
        """
        logging.info("Inicializando SearXNGTool") # Log de inicialização da ferramenta
        self.base_url = base_url or os.getenv(
            "FBPY_SEARXNG_BASE_URL", "https://searxng.site"
        )
        self.api_key = api_key or os.getenv("FBPY_SEARXNG_API_KEY", None)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppdeWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Content-Type": "application/json",  # Content-Type correto para JSON
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        logging.info(
            f"SearXNGTool inicializado com base_url={self.base_url} e api_key={'PROVIDED' if self.api_key else 'NOT PROVIDED'}"
        ) # Log com informações de inicialização

    def search(
        self,
        query: str,
        method: str = "GET",
        categories: Optional[Union[str, List[str]]] = ["general"],
        language: str = "auto",
        time_range: str = None,
        safesearch: int = SAFESEARCH_NONE,
    ) -> List[Dict]:
        """Realiza uma busca no SearXNG.

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

        Raises:
            ValueError: Se o método HTTP for inválido, o idioma for inválido ou o nível de segurança for inválido.
            requests.exceptions.RequestException: Se ocorrer algum erro durante a requisição HTTP.
        """
        logging.info(f"Iniciando busca no SearXNG com query: '{query}'") # Log de início da busca
        method = method or "GET"  # Define o método como GET se não for fornecido
        logging.debug(f"Método de busca definido como: {method}") # Log do método de busca
        if method not in ("GET", "POST"):
            logging.error(f"Método HTTP inválido: {method}") # Log de erro para método inválido
            raise ValueError(f"Método inválido: {method}. Use 'GET' ou 'POST'.")

        if not categories:  # Verifica se a lista de categorias está vazia
            categories = ["general"]
        logging.debug(f"Categorias de busca definidas como: {categories}") # Log das categorias de busca

        language = language or "auto"  # Define o idioma como auto se não for fornecido
        logging.debug(f"Idioma de busca definido como: {language}") # Log do idioma de busca
        if language not in self.LANGUAGES and language != "auto":
            logging.error(f"Idioma inválido: {language}") # Log de erro para idioma inválido
            raise ValueError(
                f"Idioma inválido: {language}. Use 'auto' ou um código ISO 639-1 válido."
            )

        safesearch = safesearch or self.SAFESEARCH_NONE  # Define safesearch para NONE se não for fornecido
        logging.debug(f"Nível de safesearch definido como: {safesearch}") # Log do nível de safesearch
        if safesearch not in (
            self.SAFESEARCH_NONE,
            self.SAFESEARCH_MODERATE,
            self.SAFESEARCH_STRICT,
        ):
            logging.error(f"Nível de segurança inválido: {safesearch}") # Log de erro para nível de segurança inválido
            raise ValueError(
                f"Nível de segurança inválido: {safesearch}. Use 'SAFESEARCH_NONE|0', 'SAFESEARCH_MODERATE|1' ou 'SAFESEARCH_STRICT|2'."
            )

        params = {
            "q": query,
            "format": "json",
            "language": language,
            "safesearch": safesearch,
            "time_range": time_range,
            "pageno": 1,  # Página inicial de resultados
        }

        # Adiciona categorias aos parâmetros da requisição
        for c in categories:
            if c.lower() in self.CATEGORIES:
                params[f"category_{c.lower()}"] = 1
        logging.debug(f"Parâmetros da requisição definidos: {params}") # Log dos parâmetros da requisição

        try:
            url = f"{self.base_url}/search"
            logging.debug(f"URL da requisição: {url}") # Log da URL da requisição
            verify_ssl = url.startswith("https")  # Verifica se a URL começa com HTTPS para ativar a verificação SSL
            logging.debug(f"Verificação SSL habilitada: {verify_ssl}") # Log da verificação SSL

            if method == "GET":
                method_call = requests.get
            elif method == "POST":
                method_call = requests.post
            else:
                # Este caso não deve ocorrer devido à validação anterior, mas é incluído para segurança
                logging.error(f"Método HTTP inválido: {method}") # Log de erro para método inválido (novamente, por segurança)
                raise ValueError(f"Método inválido: {method}. Use 'GET' ou 'POST'.")

            logging.info(f"Executando requisição {method.upper()} para: {url}") # Log de execução da requisição
            response = method_call(
                url, params=params, headers=self.headers, verify=verify_ssl
            )
            response.raise_for_status()  # Raise an exception for HTTP errors
            logging.debug(f"Resposta recebida com status code: {response.status_code}") # Log do status code da resposta
            results = response.json().get("results", [])  # Extrai os resultados do JSON da resposta
            logging.info(f"Busca no SearXNG para query: '{query}' completada com sucesso. Resultados encontrados: {len(results)}") # Log de sucesso da busca e número de resultados
            return results
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro na requisição ao SearXNG: {e}")  # Log de erro detalhado da requisição
            return []
        finally:
            logging.debug(f"Finalizando busca no SearXNG para query: '{query}'") # Log de finalização da busca
