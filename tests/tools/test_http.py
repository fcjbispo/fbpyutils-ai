import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fbpyutils_ai.tools import HTTPClient
import httpx
import logging


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
    client = HTTPClient(base_url="https://api.example.com")
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
    mock_sync_client.request.side_effect = httpx.HTTPError(  # corrigir instanciação de HTTPError
        "HTTP Error",
        request=httpx.Request("GET", "https://api.example.com/invalid"),
        response=httpx.Response(404)
    )

    with HTTPClient(base_url="https://api.example.com") as client:
        with pytest.raises(httpx.HTTPError) as exc_info:  # mudar para httpx.HTTPError
            client.sync_request("GET", "invalid")

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
    with HTTPClient(base_url="https://api.example.com") as client:
        caplog.set_level(logging.DEBUG)
        client.sync_request("GET", "data", verify_ssl=False)
        mock_sync_client.get.assert_called_with(  # mudar para mock_sync_client.get
            'https://api.example.com/data',
            params=None,
            verify=False  # verifica se verify=False foi passado
        )  # assert_called_with para get


@pytest.mark.asyncio
async def test_async_request_verify_ssl_false(mock_async_client, caplog):
    """Testa requisição assíncrona com verify_ssl=False"""
    async with HTTPClient(base_url="https://api.example.com") as client:
        caplog.set_level(logging.DEBUG)
        await client.async_request("GET", "data", verify_ssl=False)
        mock_async_client.request.assert_called_with(
            method='GET', url='https://api.example.com/data',
            params=None, data=None, json=None,
            verify=False  # Verifica se verify=False foi passado
        )


def test_sync_request_verify_ssl_true(mock_sync_client, caplog):
    """Testa requisição síncrona com verify_ssl=True (explícito)"""
    with HTTPClient(base_url="https://api.example.com") as client:
        caplog.set_level(logging.DEBUG)
        client.sync_request("GET", "data", verify_ssl=True)
        mock_sync_client.get.assert_called_with(  # mudar para mock_sync_client.get
            'https://api.example.com/data',
            params=None,
            verify=True  # verifica se verify=True foi passado
        )  # assert_called_with para get


@pytest.mark.asyncio
async def test_async_request_verify_ssl_true(mock_async_client, caplog):
    """Testa requisição assíncrona com verify_ssl=True (explícito)"""
    async with HTTPClient(base_url="https://api.example.com") as client:
        caplog.set_level(logging.DEBUG)
        await client.async_request("GET", "data", verify_ssl=True)
        mock_async_client.request.assert_called_with(
            method='GET', url='https://api.example.com/data',
            params=None, data=None, json=None,
            verify=True  # Verifica se verify=True foi passado
        )
