import pytest
import httpx
import logging
from unittest.mock import patch, AsyncMock, MagicMock
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
    with patch('httpx.AsyncClient') as mock_client:
        mock_instance = mock_client.return_value
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url = "https://api.example.com/data"

        response = httpx.Response(
            status_code=200,
            json={"async_key": "async_value"},
            request=mock_request
        )
        mock_instance.request = AsyncMock(return_value=response)
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
    assert "base_url deve incluir protocolo" in str(exc_info.value)


def test_sync_request_success(mock_sync_client, caplog):
    """Testa requisição síncrona bem-sucedida"""
    with HTTPClient(base_url="https://api.example.com") as client:
        caplog.set_level(logging.DEBUG)
        response = client.sync_request("GET", "data", params={"page": 1})

        assert response == {"key": "value"}
        assert "Iniciando requisição síncrona" in caplog.text
        assert "Requisição síncrona concluída" in caplog.text


@pytest.mark.asyncio
async def test_async_request_success(mock_async_client, caplog):
    """Testa requisição assíncrona bem-sucedida"""
    async with HTTPClient(base_url="https://api.example.com") as client:
        caplog.set_level(logging.DEBUG)
        response = await client.async_request("POST", "data", json={"test": "data"})

        assert response == {"async_key": "async_value"}
        assert "Iniciando requisição assíncrona" in caplog.text
        assert "Requisição assíncrona concluída" in caplog.text


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
    assert "Erro na requisição síncrona" in caplog.text
    assert "HTTP Error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_async_request_http_error(mock_async_client, caplog):
    """Testa tratamento de erro HTTP em requisição assíncrona"""
    mock_request = MagicMock()
    mock_request.method = "GET"
    mock_request.url = "https://api.example.com/error"
    mock_async_client.request.return_value = httpx.Response(
        status_code=500, text="Internal Server Error", request=mock_request
    )

    async with HTTPClient(base_url="https://api.example.com") as client:
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await client.async_request("GET", "error")

        assert exc_info.value.response.status_code == 500
        assert "Erro 500" in caplog.text


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

        assert "concluída em" in caplog.text
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
        response = await client.async_request(method, endpoint)
        assert response == {"async_key": "async_value"}


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
    async with HTTPClient(base_url="https://api.example.com", verify_ssl=False) as client:
        caplog.set_level(logging.DEBUG)
        await client.async_request("GET", "data")
        mock_async_client.request.assert_called_with(
            method='GET', url='https://api.example.com/data',
            params=None, data=None, json=None
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
    async with HTTPClient(base_url="https://api.example.com", verify_ssl=True) as client:
        caplog.set_level(logging.DEBUG)
        await client.async_request("GET", "data")
        mock_async_client.request.assert_called_with(
            method='GET', url='https://api.example.com/data',
            params=None, data=None, json=None
        )


async def test_async_request_stream_true(mock_async_client):
    """Testa requisição assíncrona com stream=True"""
    mock_request_obj = httpx.Request("GET", "https://api.example.com/stream_endpoint") # Cria obj httpx.Request
    mock_async_client.request.return_value = httpx.Response( # Corrigido: usar return_value
        status_code=200,
        content=b"line1\\nline2\\n", # Simula resposta de streaming
        request=mock_request_obj # Define o request mockado
    )
    async with HTTPClient(base_url="https://api.example.com") as client:
        response = await client.async_request("GET", "/stream_endpoint", stream=True)
        assert isinstance(response, httpx.Response)
        assert response.status_code == 200
        logging.debug(f"Async stream test - response.request: {response._request}") # Log de debug
        async for line in response.aiter_lines():
            assert b"line1\\nline2\\n" in [line] # Ajusta a asserção para string de conteúdo bruto

async def test_async_request_stream_false(mock_async_client):
    """Testa requisição assíncrona com stream=False"""
    mock_async_client.request = AsyncMock(return_value=httpx.Response(
        status_code=200,
        json={"key": "value"}
    ))
    async with HTTPClient(base_url="https://api.example.com") as client:
        response = await client.async_request("GET", "/non_stream_endpoint", stream=False)
        assert isinstance(response, dict)
        assert response == {"key": "value"}

def test_sync_request_stream_true(mock_sync_client):
    """Testa requisição síncrona com stream=True"""
    mock_request_obj = httpx.Request("GET", "https://api.example.com/stream_endpoint") # Cria obj httpx.Request
    mock_sync_client.request = MagicMock(return_value=httpx.Response(
        status_code=200,
        content=b"line1\\nline2\\n", # Simula resposta de streaming
        request=mock_request_obj # Define o request mockado
    ))
    with HTTPClient(base_url="https://api.example.com") as client:
        response = client.sync_request("GET", "/stream_endpoint", stream=True)
        assert isinstance(response, httpx.Response)
        assert response.status_code == 200
        for line in response.iter_lines():
            assert line in [b'line1', b'line2']

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
