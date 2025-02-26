import os
import base64
import requests
import threading
from typing import List, Optional, Dict, Any
from requests.adapters import HTTPAdapter
from tenacity import retry, wait_random_exponential, stop_after_attempt
import tiktoken  # Biblioteca para tokenização compatível com os modelos da OpenAI

from fbpyutils_ai import logging


class OpenAITool():
    _request_semaphore = threading.Semaphore(4)

    def __init__(
        self, 
        model: str, 
        api_key: str = None, 
        api_base: str = None, 
        embed_model: str = None, 
        api_embed_base: str = None, 
        api_embed_key: str = None,
        api_vision_base: str = None,
        api_vision_key: str = None,
        vision_model: str = None,
        timeout: int = 300, 
        session_retries: int = 3
    ):
        """
        Inicializa a ferramenta OpenAITool com os modelos e chaves de API para diversas funcionalidades.

        Args:
            model (str): O modelo a ser usado para gerar textos.
            api_key (Optional[str], optional): A chave de API para autenticação. Se não fornecida, 
                tenta obtê-la da variável de ambiente "FBPY_OPENAI_API_KEY". Se ainda não for encontrada, 
                uma exceção é levantada.
            api_base (str, optional): A URL base para a API. Se não fornecida, utiliza o valor da variável de 
                ambiente "FBPY_OPENAI_API_BASE" ou "https://api.openai.com" como padrão.
            embed_model (str, optional): O modelo a ser usado para gerar embeddings. Padrão é o valor de `model`.
            api_embed_base (str, optional): A URL base para a API de embeddings. Padrão é o valor de `api_base`.
            api_embed_key (str, optional): A chave de API para o modelo de embeddings. Padrão é o valor de `api_key`.
            api_vision_base (str, optional): A URL base para a API de visão. Se não fornecida, utiliza o valor de `api_base`.
            api_vision_key (str, optional): A chave de API para a API de visão. Se não fornecida, utiliza o valor de `api_key`.
            vision_model (str, optional): O modelo a ser usado para a API de visão. Se não fornecido, utiliza o valor de `model`.
            timeout (int, optional): Timeout para as requisições. Padrão é 300.
            session_retries (int, optional): Número de tentativas para a sessão. Padrão é 3.

        Raises:
            ValueError: Se a chave de API não for fornecida nem encontrada na variável de ambiente.
        """
        # Verifica e atribui a chave de API
        if not api_key:
            api_key = os.environ.get("FBPY_OPENAI_API_KEY")
            if not api_key:
                raise ValueError("API key is required and was not provided!")
        self.api_key = api_key

        # Configura o modelo e os endpoints
        self.model = model
        self.embed_model = embed_model or self.model
        self.api_base = api_base or os.environ.get("FBPY_OPENAI_API_BASE") or "https://api.openai.com"
        self.api_embed_base = api_embed_base or self.api_base
        self.api_embed_key = api_embed_key or self.api_key

        # Configura os parâmetros para a API de visão
        self.api_vision_base = api_vision_base or self.api_base
        self.api_vision_key = api_vision_key or self.api_key
        self.vision_model = vision_model or self.model

        _adapter = HTTPAdapter(max_retries=session_retries)
        self.session = requests.Session()
        self.timeout = timeout or 300
        self.retries = session_retries or 3
        self.session.mount("http://", _adapter)
        self.session.mount("https://", _adapter)

    @retry(wait=wait_random_exponential(multiplier=1, max=30), stop=stop_after_attempt(3))
    def _make_request(self, url: str, headers: Dict[str, str], json_data: Dict[str, Any]) -> Any:
        """
        Realiza uma requisição POST à API com tratamento de erros e múltiplas tentativas.

        Args:
            url (str): A URL para onde a requisição será enviada.
            headers (Dict[str, str]): Cabeçalhos HTTP para a requisição.
            json_data (Dict[str, Any]): Dados em JSON a serem enviados.

        Returns:
            Any: Resposta da API em formato JSON.
        """
        with OpenAITool._request_semaphore:
            try:
                response = self.session.post(url, headers=headers, json=json_data, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.Timeout as e:
                print(f"Request timed out: {e}")
                raise
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                raise

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Gera um embedding para um dado texto utilizando a API da OpenAI.

        Args:
            text (str): Texto para o qual o embedding será gerado.

        Returns:
            Optional[List[float]]: Lista de floats representando o embedding ou None em caso de erro.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_embed_key}",
        }
        data = {"model": self.embed_model, "input": text}
        try:
            result = self._make_request(f"{self.api_embed_base}/embeddings", headers, data)
            return result["data"][0]["embedding"]
        except (KeyError, IndexError) as e:
            print(f"Error parsing OpenAI response: {e}")
            return None

    def generate_text(self, prompt: str, max_tokens: int = 300, temperature: int = 0.8) -> str:
        """
        Gera um texto a partir de um prompt utilizando a API da OpenAI.

        Args:
            prompt (str): O prompt enviado para a geração do texto.
            max_tokens (int, optional): Número máximo de tokens a serem gerados. Padrão é 300.
            temperature (int, optional): Temperatura da geração de texto. Padrão é 0.8.

        Returns:
            str: Texto gerado pela API.
        """
        tokens = max_tokens or 300
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {"model": self.model, "prompt": prompt, "max_tokens": tokens, "temperature": temperature}
        try:
            result = self._make_request(f"{self.api_base}/completions", headers, data)
            return result["choices"][0]["text"].strip()
        except (KeyError, IndexError) as e:
            print(f"Error parsing OpenAI response: {e}")
            return ""

    def generate_completions(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> str:
        """
        Gera uma resposta de chat a partir de uma lista de mensagens utilizando a API da OpenAI.

        Args:
            messages (List[Dict[str, str]]): Lista de mensagens que compõem a conversa.
            model (str, optional): Modelo a ser utilizado. Se não fornecido, utiliza o valor padrão.
            **kwargs: Parâmetros adicionais para a requisição.

        Returns:
            str: Resposta gerada pela API.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {"model": model or self.model, "messages": messages, **kwargs}
        try:
            result = self._make_request(f"{self.api_base}/chat/completions", headers, data)
            if (result["choices"] and len(result["choices"]) > 0 and 
                "message" in result["choices"][0] and "content" in result["choices"][0]["message"]):
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"Error parsing OpenAI response: {result}")
                return ""
        except (KeyError, IndexError) as e:
            print(f"Error parsing OpenAI response: {e}")
            return ""

    def generate_tokens(self, text: str) -> List[int]:
        """
        Gera a lista de tokens a partir de um texto utilizando a biblioteca tiktoken,
        de forma compatível com os modelos da OpenAI.

        Args:
            text (str): O texto a ser tokenizado.
            model (Optional[str], optional): O modelo para o qual a tokenização será realizada.
                Se não fornecido, utiliza `self.model`.

        Returns:
            List[int]: Lista de tokens gerados a partir do texto.
        """
        model_to_use = self.model
        try:
            encoding = tiktoken.encoding_for_model(model_to_use)
        except Exception:
            # Caso o modelo não seja reconhecido, usar um encoding padrão
            encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return tokens

    def describe_image(self, image: str, prompt: str, max_tokens: int = 300, temperature: int = 0.4) -> str:
        """
        Descreve uma imagem utilizando a API da OpenAI, combinando um prompt com o conteúdo da imagem.
        A imagem pode ser fornecida como:
            - Caminho para um arquivo local,
            - URL remota,
            - ou uma string já codificada em base64.

        O método converte a imagem para base64 (quando necessário) e adiciona essa informação ao prompt,
        que é enviado para o modelo configurado para gerar uma descrição.

        Args:
            image (str): Caminho para o arquivo local, URL remota ou conteúdo em base64 da imagem.
            prompt (str): Prompt que orienta a descrição da imagem.
            max_tokens (int, optional): Número máximo de tokens a serem gerados. Padrão é 300.
            temperature (int, optional): Temperatura da geração de texto. Padrão é 0.4.

        Returns:
            str: Descrição gerada pela API da OpenAI para a imagem.
        """
        # Verifica se a imagem é um arquivo local
        if os.path.exists(image):
            with open(image, "rb") as img_file:
                image_bytes = img_file.read()
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        # Se a imagem for uma URL remota
        elif image.startswith("http://") or image.startswith("https://"):
            try:
                response = requests.get(image, timeout=self.timeout)
                response.raise_for_status()
                image_bytes = response.content
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            except Exception as e:
                print(f"Erro ao baixar a imagem: {e}")
                return ""
        else:
            # Assume que o conteúdo já está em base64
            image_base64 = image

        # Monta o prompt incluindo a informação da imagem codificada em base64
        full_prompt = (
            f"{prompt}\n\n"
            "A seguir, a imagem codificada em base64:\n"
            f"{image_base64}\n\n"
            "Forneça uma descrição detalhada da imagem."
        )

        # Utiliza o método generate_text para obter a descrição da imagem
        description = self.generate_text(full_prompt, max_tokens=max_tokens, temperature=temperature)
        return description
