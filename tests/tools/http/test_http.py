import pytest
import httpx
import logging
from unittest.mock import patch, AsyncMock, MagicMock
import typing # Adicionado import
from fbpyutils_ai.tools.http import HTTPClient


@pytest.fixture
def mock_sync_client():
    with patch('httpx.Client') as mock_client:  # Mudar para httpx.Client
        mock_instance = mock_client.return_value
        response = httpx.Response(
            status_code=200,
            json={"key": "value"},
            request=httpx.Request("GET", "https://api.example.com/data")
        )

        mock_instance.request = MagicMock(return_value=response) # Mock httpx.Client.request
        mock_instance.get = MagicMock(return_value=response) # Mock httpx.Client.get
        mock_instance.post = MagicMock(return_value=response) # Mock httpx.Client.post
        mock_instance.put = MagicMock(return_value=response) # Mock httpx.Client.put
        mock_instance.delete = MagicMock(return_value=response) # Mock httpx.Client.delete
        yield mock_instance


@pytest.fixture
def mock_async_client():
    """Fixture para mockar httpx.AsyncClient e seus métodos."""
    with patch('httpx.AsyncClient') as mock_factory:
        mock_instance = mock_factory.return_value

        # Mock base response para métodos não-streaming
        base_response = httpx.Response(
            status_code=200,
            json={"async_key": "async_value"},
            request=httpx.Request("GET", "https://api.example.com/data") # Request genérico
        )

        # Mockar métodos específicos com AsyncMock
        mock_instance.get = AsyncMock(return_value=base_response)
        mock_instance.post = AsyncMock(return_value=base_response)
        mock_instance.put = AsyncMock(return_value=base_response)
        mock_instance.delete = AsyncMock(return_value=base_response)

        # Mock para fechamento
        mock_instance.aclose = AsyncMock()
        yield mock_instance


def test_http_client_initialization_valid():
    """Testa inicialização com URL válida"""
    client = HTTPClient(base_url="https://api.example.com", verify_ssl=True)
    assert client.base_url == "https://api.example.com"
    assert isinstance(client._sync_client, httpx.Client)
    assert isinstance(client._async_client, httpx.AsyncClient)


def test_http_client_initialization_invalid():
    """Testa inicialização com URL inválida"""
    with pytest.raises(ValueError) as exc_info:
        HTTPClient(base_url="invalid_url")
    assert "base_url must include protocol (http/https)" in str(exc_info.value)


def test_sync_request_success(mock_sync_client, caplog):
    """Testa requisição síncrona bem-sucedida"""
    with HTTPClient(base_url="https://api.example.com") as client:
        caplog.set_level(logging.DEBUG)
        response = client.sync_request("GET", "data", params={"page": 1})

        assert response == {"key": "value"}
        assert "Starting synchronous request" in caplog.text # Corrigido: Mensagem de log real
        assert "Synchronous request completed" in caplog.text # Corrigido: Mensagem de log real


@pytest.mark.asyncio
async def test_async_request_success(mock_async_client, caplog):
    """Testa requisição assíncrona bem-sucedida (POST)"""
    async with HTTPClient(base_url="https://api.example.com") as client:
        # Injeta o mock no cliente assíncrono
        client._async_client = mock_async_client
        caplog.set_level(logging.DEBUG)
        json_payload = {"test": "data"}
        response = await client.async_request("POST", "data", json=json_payload)

        assert response == {"async_key": "async_value"}
        mock_async_client.post.assert_awaited_once_with(
            "https://api.example.com/data", params=None, data=None, json=json_payload
        )
        assert "Starting asynchronous request: POST" in caplog.text # Ajuste na msg de log
        assert "Asynchronous request completed" in caplog.text # Ajuste na msg de log


def test_sync_request_http_error(mock_sync_client, caplog):  # manter mock_sync_client
    """Testa tratamento de erro HTTP em requisição síncrona"""
    # Cria a exceção e atribui os atributos necessários
    error = httpx.HTTPError("HTTP Error")
    error.request = httpx.Request("GET", "https://api.example.com/invalid")
    error.response = httpx.Response(404)
    
    # Corrige: aplica o side_effect no método GET, que é o que o HTTPClient utiliza para requisições GET
    mock_sync_client.get.side_effect = error

    # Certifique-se de que o mock não foi chamado ainda
    mock_sync_client.get.assert_not_called()

    with HTTPClient(base_url="https://api.example.com") as client:
        # Injeta o mock no cliente síncrono do HTTPClient
        client._sync_client = mock_sync_client
        
        with pytest.raises(httpx.HTTPError) as exc_info:
            client.sync_request("GET", "invalid")
    
    # Verifica se os logs e a mensagem da exceção estão corretos
    assert "Error in synchronous request" in caplog.text # Corrigido: Mensagem de log real
    assert "HTTP Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_request_http_error(mock_async_client, caplog):
    """Testa tratamento de erro HTTP em requisição assíncrona (GET)"""
    mock_request = httpx.Request("GET", "https://api.example.com/error")
    error_response = httpx.Response(
        status_code=500, text="Internal Server Error", request=mock_request
    )
    # Configura o side_effect no método GET mockado
    mock_async_client.get.side_effect = httpx.HTTPStatusError(
        "Server Error", request=mock_request, response=error_response
    )

    async with HTTPClient(base_url="https://api.example.com") as client:
        # Injeta o mock
        client._async_client = mock_async_client
        caplog.set_level(logging.ERROR) # Focar nos logs de erro
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.async_request("GET", "error")

        assert exc_info.value.response.status_code == 500
        # Verifica se o método GET foi chamado
        mock_async_client.get.assert_awaited_once_with("https://api.example.com/error", params=None)
        assert "Error 500 in GET https://api.example.com/error" in caplog.text # Verificar log de erro


def test_context_management_sync():
    """Testa gerenciamento de contexto síncrono"""
    with HTTPClient(base_url="https://api.example.com") as client:
        assert client._sync_client.is_closed is False

    assert client._sync_client.is_closed is True


@pytest.mark.asyncio
async def test_context_management_async():
    """Testa gerenciamento de contexto assíncrono"""
    async with HTTPClient(base_url="https://api.example.com") as client:
        assert client._async_client.is_closed is False

    assert client._async_client.is_closed is True


def test_logging_performance_metrics(mock_sync_client, caplog):
    """Testa registro de métricas de desempenho nos logs"""
    with HTTPClient(base_url="https://api.example.com") as client:
        caplog.set_level(logging.DEBUG)
        client.sync_request("GET", "data")

        assert "completed in" in caplog.text # Corrigido: Parte da mensagem de log real
        assert "bytes" in caplog.text


@pytest.mark.parametrize(
    "method,endpoint",
    [
        ("GET", "data"),
        ("POST", "submit"),
        ("PUT", "update/1"),
        ("DELETE", "delete/1"),
    ],
)
def test_all_http_methods_sync(mock_sync_client, method, endpoint):
    """Testa todos os métodos HTTP síncronos"""
    with HTTPClient(base_url="https://api.example.com") as client:
        response = client.sync_request(method, endpoint)
        assert response == {"key": "value"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,endpoint",
    [
        ("GET", "data"),
        ("POST", "submit"),
        ("PUT", "update/1"),
        ("DELETE", "delete/1"),
    ],
)
async def test_all_http_methods_async(mock_async_client, method, endpoint):
    """Testa todos os métodos HTTP assíncronos"""
    async with HTTPClient(base_url="https://api.example.com") as client:
        # Injeta o mock
        client._async_client = mock_async_client
        response = await client.async_request(method, endpoint)
        assert response == {"async_key": "async_value"}

        # Verifica se o método mockado correspondente foi chamado
        mock_method = getattr(mock_async_client, method.lower())
        expected_url = f"https://api.example.com/{endpoint}"
        # Ajusta a verificação da chamada para corresponder aos parâmetros padrão
        if method == "GET":
             mock_method.assert_awaited_once_with(expected_url, params=None)
        else:
             mock_method.assert_awaited_once_with(expected_url, params=None, data=None, json=None)


def test_sync_request_verify_ssl_false(mock_sync_client, caplog):
    """Testa requisição síncrona com verify_ssl=False"""
    with HTTPClient(base_url="https://api.example.com", verify_ssl=False) as client:
        caplog.set_level(logging.DEBUG)
        client.sync_request("GET", "data")
        mock_sync_client.get.assert_called_with(
            'https://api.example.com/data',
            params=None
        )  # assert_called_with para get


@pytest.mark.asyncio
async def test_async_request_verify_ssl_false(mock_async_client, caplog):
    """Testa requisição assíncrona com verify_ssl=False"""
    # A verificação SSL é feita na inicialização do cliente httpx,
    # não em cada chamada de método. O mock já está configurado.
    # Apenas verificamos se o método correto é chamado.
    async with HTTPClient(base_url="https://api.example.com", verify_ssl=False) as client:
        client._async_client = mock_async_client # Injeta o mock
        caplog.set_level(logging.DEBUG)
        await client.async_request("GET", "data")
        mock_async_client.get.assert_awaited_once_with(
            'https://api.example.com/data', params=None
        )


def test_sync_request_verify_ssl_true(mock_sync_client, caplog):
    """Testa requisição síncrona com verify_ssl=True (explícito)"""
    with HTTPClient(base_url="https://api.example.com", verify_ssl=True) as client:
        caplog.set_level(logging.DEBUG)
        client.sync_request("GET", "data")
        mock_sync_client.get.assert_called_with(  # mudar para mock_sync_client.get
            'https://api.example.com/data',
            params=None
        )  # assert_called_with para get


@pytest.mark.asyncio
async def test_async_request_verify_ssl_true(mock_async_client, caplog):
    """Testa requisição assíncrona com verify_ssl=True (explícito)"""
    # Similar ao teste com verify_ssl=False, verificamos a chamada do método.
    async with HTTPClient(base_url="https://api.example.com", verify_ssl=True) as client:
        client._async_client = mock_async_client # Injeta o mock
        caplog.set_level(logging.DEBUG)
        await client.async_request("GET", "data")
        mock_async_client.get.assert_awaited_once_with(
            'https://api.example.com/data', params=None
        )


@pytest.mark.asyncio
# Classe auxiliar para mockar stream assíncrono
class MockAsyncStream(httpx.AsyncByteStream):
    def __init__(self, content: typing.List[bytes]):
        self._content = content
        self._iter = iter(self._content)

    async def __aiter__(self) -> typing.AsyncIterator[bytes]:
        for chunk in self._iter:
            # Simular algum comportamento assíncrono se necessário, ex: await asyncio.sleep(0)
            yield chunk

@pytest.mark.asyncio
async def test_async_request_stream_true(mock_async_client):
    """Testa requisição assíncrona com stream=True"""
    mock_request_obj = httpx.Request("GET", "https://api.example.com/stream_endpoint")
    stream_content = [b"line1\n", b"line2\n"]
    mock_stream = MockAsyncStream(stream_content) # Usar a classe auxiliar

    mock_response = httpx.Response(
        status_code=200,
        stream=mock_stream, # Usar a instância da classe auxiliar
        request=mock_request_obj
    )
    mock_async_client.get.return_value = mock_response # Mockar o método GET

    async with HTTPClient(base_url="https://api.example.com") as client:
        client._async_client = mock_async_client # Injetar mock
        response = await client.async_request("GET", "/stream_endpoint", stream=True)

        assert isinstance(response, httpx.Response) # Deve retornar o objeto Response
        assert response.status_code == 200
        mock_async_client.get.assert_awaited_once_with("https://api.example.com/stream_endpoint", params=None)

        # Iterar sobre a resposta mockada
        received_lines = []
        async for line in response.aiter_lines():
            received_lines.append(line)

        assert received_lines == ["line1", "line2"] # Verificar linhas decodificadas

@pytest.mark.asyncio
async def test_async_request_stream_false(mock_async_client):
    """Testa requisição assíncrona com stream=False"""
    # O mock padrão já retorna um JSON, apenas verificamos a chamada
    mock_async_client.get.return_value = httpx.Response(
        status_code=200,
        json={"key": "value"},
        request=httpx.Request("GET", "https://api.example.com/non_stream_endpoint")
    )

    async with HTTPClient(base_url="https://api.example.com") as client:
        client._async_client = mock_async_client # Injetar mock
        response = await client.async_request("GET", "/non_stream_endpoint", stream=False)

        assert isinstance(response, dict) # Deve retornar dict porque .json() é chamado
        assert response == {"key": "value"}
        mock_async_client.get.assert_awaited_once_with("https://api.example.com/non_stream_endpoint", params=None)

def test_sync_request_stream_true(mock_sync_client):
    """Testa requisição síncrona com stream=True"""
    mock_request_obj = httpx.Request("GET", "https://api.example.com/stream_endpoint") # Cria obj httpx.Request
    # Corrigido: Aplicar mock ao método 'get' que é usado por sync_request
    mock_sync_client.get.return_value = httpx.Response(
        status_code=200,
        stream=httpx.ByteStream(b"line1\nline2\n"), # Usar ByteStream com conteúdo iterável
        request=mock_request_obj
    )
    with HTTPClient(base_url="https://api.example.com") as client:
        response = client.sync_request("GET", "/stream_endpoint", stream=True)
        assert isinstance(response, httpx.Response)
        assert response.status_code == 200
        for line in response.iter_lines():
            assert line in ["line1", "line2"] # Corrigido: iter_lines decodifica para string

def test_sync_request_stream_false(mock_sync_client):
    """Testa requisição síncrona com stream=False"""
    mock_request_obj = httpx.Request("GET", "https://api.example.com/non_stream_endpoint") # Cria obj httpx.Request
    mock_sync_client.request = MagicMock(return_value=httpx.Response(
        status_code=200,
        json={"key": "value"},
        request=mock_request_obj # Define o request mockado
    ))
    with HTTPClient(base_url="https://api.example.com") as client:
        response = client.sync_request("GET", "/non_stream_endpoint", stream=False)
        assert isinstance(response, dict)
        assert response == {"key": "value"}
