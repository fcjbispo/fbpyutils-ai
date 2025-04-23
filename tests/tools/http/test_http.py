import pytest
import httpx
import logging
import io
import gzip
import json
import pytest
import httpx
import logging
from unittest.mock import patch, AsyncMock, MagicMock, PropertyMock
import typing
from fbpyutils_ai.tools.http import HTTPClient

# --- Fixtures ---

@pytest.fixture
def mock_sync_client():
    """Fixture para mockar httpx.Client e seus métodos GET e POST."""
    with patch('httpx.Client') as mock_factory:
        mock_instance = mock_factory.return_value
        # Configurar mocks para GET e POST
        mock_instance.get = MagicMock()
        mock_instance.post = MagicMock()
        # Configurar mock para close
        mock_instance.close = MagicMock()
        # Configurar is_closed property
        type(mock_instance).is_closed = PropertyMock(return_value=False)

        # Resposta padrão (pode ser sobrescrita nos testes)
        default_response = httpx.Response(
            status_code=200,
            json={"key": "value"},
            request=httpx.Request("GET", "https://api.example.com/data"),
            headers={'Content-Type': 'application/json'}
        )
        mock_instance.get.return_value = default_response
        mock_instance.post.return_value = default_response

        yield mock_instance


@pytest.fixture
def mock_async_client():
    """Fixture para mockar httpx.AsyncClient e seus métodos GET e POST."""
    with patch('httpx.AsyncClient') as mock_factory:
        mock_instance = mock_factory.return_value

        # Mockar métodos GET e POST com AsyncMock
        mock_instance.get = AsyncMock()
        mock_instance.post = AsyncMock()
        # Mock para fechamento
        mock_instance.aclose = AsyncMock()
        # Configurar is_closed property
        type(mock_instance).is_closed = PropertyMock(return_value=False)

        # Resposta padrão assíncrona (pode ser sobrescrita nos testes)
        default_response = httpx.Response(
            status_code=200,
            json={"async_key": "async_value"},
            request=httpx.Request("GET", "https://api.example.com/data"),
            headers={'Content-Type': 'application/json'}
        )
        # Configurar aread mock para resposta padrão
        default_response.aread = AsyncMock(return_value=json.dumps({"async_key": "async_value"}).encode('utf-8'))

        mock_instance.get.return_value = default_response
        mock_instance.post.return_value = default_response

        yield mock_instance

# --- Helper Functions ---

def create_mock_response(status_code, json_data=None, text_data=None, content_bytes=None, headers=None, request_url="https://api.example.com/data", encoding='utf-8'):
    """Cria um objeto httpx.Response mockado."""
    req = httpx.Request("GET", request_url) # Request genérico
    final_headers = {'Content-Type': 'application/json'} if json_data else {'Content-Type': 'text/plain'}
    if headers:
        final_headers.update(headers)

    content_to_use = content_bytes
    if content_to_use is None:
        if json_data is not None:
            content_to_use = json.dumps(json_data).encode(encoding)
        elif text_data is not None:
            content_to_use = text_data.encode(encoding)
        else:
            content_to_use = b''

    response = httpx.Response(
        status_code=status_code,
        request=req,
        headers=final_headers,
        content=content_to_use # Definir content diretamente
    )
    # Mockar .json() se necessário
    if json_data is not None and status_code < 300:
         response.json = MagicMock(return_value=json_data)
    else:
         # Simular erro se .json() for chamado em resposta não-JSON ou erro
         response.json = MagicMock(side_effect=json.JSONDecodeError("Simulated decode error", "", 0))

    # Mockar .text
    response.text = text_data if text_data is not None else content_to_use.decode(encoding, errors='ignore')

    # Mockar aread() para testes assíncronos
    response.aread = AsyncMock(return_value=content_to_use)

    return response

def gzip_content(data: typing.Union[dict, str]) -> bytes:
    """Compacta dados (dict ou str) usando Gzip."""
    if isinstance(data, dict):
        content_bytes = json.dumps(data).encode('utf-8')
    else:
        content_bytes = data.encode('utf-8')

    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode='wb') as f:
        f.write(content_bytes)
    return out.getvalue()

# --- Test Cases ---


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
        json_payload_data = {"test": "data"}
        # Configurar resposta mock para POST
        mock_response = create_mock_response(200, json_data={"async_key": "async_value"})
        mock_async_client.post.return_value = mock_response

        response = await client.async_request("POST", "data", json_payload=json_payload_data)

        assert response == {"async_key": "async_value"}
        mock_async_client.post.assert_awaited_once()
        call_args, call_kwargs = mock_async_client.post.call_args
        assert call_args[0] == "https://api.example.com/data"
        assert call_kwargs.get('json') == json_payload_data
        assert call_kwargs.get('headers', {}).get('Accept-Encoding') == 'gzip' # Verificar header
        assert "Starting asynchronous request: POST" in caplog.text
        assert "Asynchronous request completed" in caplog.text


def test_sync_request_http_status_error_no_json(mock_sync_client, caplog):
    """Testa erro HTTP 404 síncrono sem corpo JSON."""
    error_response = create_mock_response(404, text_data="Not Found", headers={'Content-Type': 'text/plain'})
    mock_sync_client.get.side_effect = httpx.HTTPStatusError(
        "Not Found", request=error_response.request, response=error_response
    )

    with HTTPClient(base_url="https://api.example.com") as client:
        client._sync_client = mock_sync_client
        caplog.set_level(logging.WARNING)
        # A exceção não deve ser levantada, a função deve retornar o dict de erro
        response = client.sync_request("GET", "invalid")

    assert isinstance(response, dict)
    assert response['status_code'] == 404
    assert response['content'] == "Not Found"
    assert "HTTP Error 404" in caplog.text
    assert "Could not parse HTTP error response as JSON" in caplog.text # Verifica log de fallback


@pytest.mark.asyncio
async def test_async_request_http_status_error_no_json(mock_async_client, caplog):
    """Testa erro HTTP 500 assíncrono sem corpo JSON."""
    error_response = create_mock_response(500, text_data="Server Error", headers={'Content-Type': 'text/plain'})
    mock_async_client.get.side_effect = httpx.HTTPStatusError(
        "Server Error", request=error_response.request, response=error_response
    )

    async with HTTPClient(base_url="https://api.example.com") as client:
        client._async_client = mock_async_client
        caplog.set_level(logging.WARNING)
        # A exceção não deve ser levantada, a função deve retornar o dict de erro
        response = await client.async_request("GET", "error")

    assert isinstance(response, dict)
    # O manipulador de erro assíncrono tenta analisar o corpo, então esperamos o dict de falha de análise
    assert response['content'] == "Server Error"
    assert "Failed to parse response as JSON" in response['message']
    assert "HTTP Error 500" in caplog.text
    assert "Returning parsed error response" in caplog.text # Log indicando que tentou analisar


def test_context_management_sync():
    """Testa gerenciamento de contexto síncrono"""
    client = HTTPClient(base_url="https://api.example.com")
    # Mockar o cliente interno para verificar is_closed e close
    client._sync_client = mock_sync_client() # Chamar a fixture para obter o mock
    type(client._sync_client).is_closed = PropertyMock(side_effect=[False, True]) # Simular mudança de estado

    with client:
        assert client._sync_client.is_closed is False

    assert client._sync_client.is_closed is True
    client._sync_client.close.assert_called_once() # Verificar se close foi chamado


@pytest.mark.asyncio
async def test_context_management_async():
    """Testa gerenciamento de contexto assíncrono"""
    client = HTTPClient(base_url="https://api.example.com")
    # Mockar o cliente interno para verificar is_closed e aclose
    client._async_client = mock_async_client() # Chamar a fixture para obter o mock
    type(client._async_client).is_closed = PropertyMock(side_effect=[False, True]) # Simular mudança de estado

    async with client:
        assert client._async_client.is_closed is False

    assert client._async_client.is_closed is True
    client._async_client.aclose.assert_awaited_once() # Verificar se aclose foi chamado


def test_logging_performance_metrics_sync(mock_sync_client, caplog):
    """Testa registro de métricas de desempenho nos logs síncronos"""
    mock_response = create_mock_response(200, json_data={"key": "value"}, content_bytes=b'{"key": "value"}')
    mock_sync_client.get.return_value = mock_response

    with HTTPClient(base_url="https://api.example.com") as client:
        client._sync_client = mock_sync_client
        caplog.set_level(logging.DEBUG)
        client.sync_request("GET", "data")

    assert "Synchronous request completed in" in caplog.text
    assert "Content-Length: 15" in caplog.text # Verificar tamanho do conteúdo mockado


@pytest.mark.asyncio
async def test_logging_performance_metrics_async(mock_async_client, caplog):
    """Testa registro de métricas de desempenho nos logs assíncronos"""
    mock_response = create_mock_response(200, json_data={"async_key": "async_value"}, content_bytes=b'{"async_key": "async_value"}')
    mock_async_client.get.return_value = mock_response

    async with HTTPClient(base_url="https://api.example.com") as client:
        client._async_client = mock_async_client
        caplog.set_level(logging.DEBUG)
        await client.async_request("GET", "data")

    assert "Asynchronous request completed in" in caplog.text
    assert "Content-Length: 28" in caplog.text # Verificar tamanho do conteúdo mockado


@pytest.mark.parametrize(
    "method,endpoint,payload",
    [
        ("GET", "data", {"param": "1"}), # GET usa payload como params
        ("POST", "submit", {"data": "value"}), # POST usa payload como json_payload
    ],
)
def test_supported_http_methods_sync(mock_sync_client, method, endpoint, payload):
    """Testa os métodos HTTP síncronos suportados (GET, POST)"""
    mock_response = create_mock_response(200, json_data={"key": f"value_{method}"})
    if method == "GET":
        mock_sync_client.get.return_value = mock_response
    else: # POST
        mock_sync_client.post.return_value = mock_response

    with HTTPClient(base_url="https://api.example.com") as client:
        client._sync_client = mock_sync_client
        if method == "GET":
            response = client.sync_request(method, endpoint, params=payload)
        else: # POST
            response = client.sync_request(method, endpoint, json_payload=payload)

        assert response == {"key": f"value_{method}"}
        # Verificar chamada do mock
        mock_method = getattr(mock_sync_client, method.lower())
        mock_method.assert_called_once()
        call_args, call_kwargs = mock_method.call_args
        assert call_args[0] == f"https://api.example.com/{endpoint}"
        if method == "GET":
            assert call_kwargs.get('params') == payload
        else: # POST
            assert call_kwargs.get('json') == payload
        assert call_kwargs.get('headers', {}).get('Accept-Encoding') == 'gzip' # Verificar header


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,endpoint,payload",
    [
        ("GET", "data", {"param": "1"}), # GET usa payload como params
        ("POST", "submit", {"data": "value"}), # POST usa payload como json_payload
    ],
)
async def test_supported_http_methods_async(mock_async_client, method, endpoint, payload):
    """Testa os métodos HTTP assíncronos suportados (GET, POST)"""
    mock_response = create_mock_response(200, json_data={"async_key": f"value_{method}"})
    if method == "GET":
        mock_async_client.get.return_value = mock_response
    else: # POST
        mock_async_client.post.return_value = mock_response

    async with HTTPClient(base_url="https://api.example.com") as client:
        client._async_client = mock_async_client
        if method == "GET":
            response = await client.async_request(method, endpoint, params=payload)
        else: # POST
            response = await client.async_request(method, endpoint, json_payload=payload)

        assert response == {"async_key": f"value_{method}"}
        # Verificar chamada do mock
        mock_method = getattr(mock_async_client, method.lower())
        mock_method.assert_awaited_once()
        call_args, call_kwargs = mock_method.call_args
        assert call_args[0] == f"https://api.example.com/{endpoint}"
        if method == "GET":
            assert call_kwargs.get('params') == payload
        else: # POST
            assert call_kwargs.get('json') == payload
        assert call_kwargs.get('headers', {}).get('Accept-Encoding') == 'gzip' # Verificar header


def test_sync_request_verify_ssl_false(mock_sync_client):
    """Testa requisição síncrona com verify_ssl=False (verifica header)"""
    # A verificação SSL é feita na inicialização do httpx.Client,
    # o teste principal é verificar se a requisição é feita corretamente.
    mock_response = create_mock_response(200, json_data={"key": "value"})
    mock_sync_client.get.return_value = mock_response

    with HTTPClient(base_url="https://api.example.com", verify_ssl=False) as client:
        client._sync_client = mock_sync_client
        client.sync_request("GET", "data")
        mock_sync_client.get.assert_called_once()
        call_args, call_kwargs = mock_sync_client.get.call_args
        assert call_kwargs.get('headers', {}).get('Accept-Encoding') == 'gzip'


@pytest.mark.asyncio
async def test_async_request_verify_ssl_false(mock_async_client):
    """Testa requisição assíncrona com verify_ssl=False (verifica header)"""
    mock_response = create_mock_response(200, json_data={"async_key": "async_value"})
    mock_async_client.get.return_value = mock_response

    async with HTTPClient(base_url="https://api.example.com", verify_ssl=False) as client:
        client._async_client = mock_async_client
        await client.async_request("GET", "data")
        mock_async_client.get.assert_awaited_once()
        call_args, call_kwargs = mock_async_client.get.call_args
        assert call_kwargs.get('headers', {}).get('Accept-Encoding') == 'gzip'


def test_sync_request_verify_ssl_true(mock_sync_client):
    """Testa requisição síncrona com verify_ssl=True (verifica header)"""
    mock_response = create_mock_response(200, json_data={"key": "value"})
    mock_sync_client.get.return_value = mock_response

    with HTTPClient(base_url="https://api.example.com", verify_ssl=True) as client:
        client._sync_client = mock_sync_client
        client.sync_request("GET", "data")
        mock_sync_client.get.assert_called_once()
        call_args, call_kwargs = mock_sync_client.get.call_args
        assert call_kwargs.get('headers', {}).get('Accept-Encoding') == 'gzip'


@pytest.mark.asyncio
async def test_async_request_verify_ssl_true(mock_async_client):
    """Testa requisição assíncrona com verify_ssl=True (verifica header)"""
    mock_response = create_mock_response(200, json_data={"async_key": "async_value"})
    mock_async_client.get.return_value = mock_response

    async with HTTPClient(base_url="https://api.example.com", verify_ssl=True) as client:
        client._async_client = mock_async_client
        await client.async_request("GET", "data")
        mock_async_client.get.assert_awaited_once()
        call_args, call_kwargs = mock_async_client.get.call_args
        assert call_kwargs.get('headers', {}).get('Accept-Encoding') == 'gzip'


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
        # Verificar chamada do mock e header
        mock_async_client.get.assert_awaited_once()
        call_args, call_kwargs = mock_async_client.get.call_args
        assert call_args[0] == "https://api.example.com/stream_endpoint"
        assert call_kwargs.get('headers', {}).get('Accept-Encoding') == 'gzip'

        # Iterar sobre a resposta mockada
        received_content = b""
        async for chunk in response.aiter_bytes():
            received_content += chunk

        assert received_content == b"line1\nline2\n" # Verificar bytes brutos

@pytest.mark.asyncio
async def test_async_request_stream_false(mock_async_client):
    """Testa requisição assíncrona com stream=False"""
    # Configurar mock para retornar JSON válido
    mock_response = create_mock_response(200, json_data={"key": "value"})
    mock_async_client.get.return_value = mock_response

    async with HTTPClient(base_url="https://api.example.com") as client:
        client._async_client = mock_async_client # Injetar mock
        response = await client.async_request("GET", "/non_stream_endpoint", stream=False)

        assert isinstance(response, dict) # Deve retornar dict
        assert response == {"key": "value"}
        # Verificar chamada do mock e header
        mock_async_client.get.assert_awaited_once()
        call_args, call_kwargs = mock_async_client.get.call_args
        assert call_args[0] == "https://api.example.com/non_stream_endpoint"
        assert call_kwargs.get('headers', {}).get('Accept-Encoding') == 'gzip'

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
        client._sync_client = mock_sync_client # Injetar mock
        response = client.sync_request("GET", "/stream_endpoint", stream=True)
        assert isinstance(response, httpx.Response)
        assert response.status_code == 200
        # Verificar chamada do mock e header
        mock_sync_client.get.assert_called_once()
        call_args, call_kwargs = mock_sync_client.get.call_args
        assert call_args[0] == "https://api.example.com/stream_endpoint"
        assert call_kwargs.get('headers', {}).get('Accept-Encoding') == 'gzip'

        # Verificar conteúdo do stream
        assert response.content == b"line1\nline2\n"

def test_sync_request_stream_false(mock_sync_client):
    """Testa requisição síncrona com stream=False"""
    mock_request_obj = httpx.Request("GET", "https://api.example.com/non_stream_endpoint") # Cria obj httpx.Request
    # Configurar mock para retornar JSON válido
    mock_response = create_mock_response(200, json_data={"key": "value"})
    mock_sync_client.get.return_value = mock_response

    with HTTPClient(base_url="https://api.example.com") as client:
        client._sync_client = mock_sync_client # Injetar mock
        response = client.sync_request("GET", "/non_stream_endpoint", stream=False)
        assert isinstance(response, dict)
        assert response == {"key": "value"}
        # Verificar chamada do mock e header
        mock_sync_client.get.assert_called_once()
        call_args, call_kwargs = mock_sync_client.get.call_args
        assert call_args[0] == "https://api.example.com/non_stream_endpoint"
        assert call_kwargs.get('headers', {}).get('Accept-Encoding') == 'gzip'

# --- Novos Testes para Gzip e JSON Fallback ---

def test_sync_request_gzip_json_success(mock_sync_client, caplog):
    """Testa requisição síncrona com Gzip e JSON válido."""
    json_data = {"compressed": True}
    gzipped_content = gzip_content(json_data)
    mock_response = create_mock_response(
        200, content_bytes=gzipped_content, headers={'Content-Encoding': 'gzip', 'Content-Type': 'application/json'}
    )
    mock_sync_client.get.return_value = mock_response

    with HTTPClient(base_url="https://api.example.com") as client:
        client._sync_client = mock_sync_client
        caplog.set_level(logging.DEBUG)
        response = client.sync_request("GET", "gzipped_data")

    assert response == json_data
    assert "Decompressing Gzip content" in caplog.text
    mock_sync_client.get.assert_called_once()
    call_args, call_kwargs = mock_sync_client.get.call_args
    assert call_kwargs.get('headers', {}).get('Accept-Encoding') == 'gzip'

@pytest.mark.asyncio
async def test_async_request_gzip_json_success(mock_async_client, caplog):
    """Testa requisição assíncrona com Gzip e JSON válido."""
    json_data = {"async_compressed": True}
    gzipped_content = gzip_content(json_data)
    mock_response = create_mock_response(
        200, content_bytes=gzipped_content, headers={'Content-Encoding': 'gzip', 'Content-Type': 'application/json'}
    )
    # Mockar aread para retornar conteúdo gzippado
    mock_response.aread = AsyncMock(return_value=gzipped_content)
    mock_async_client.get.return_value = mock_response

    async with HTTPClient(base_url="https://api.example.com") as client:
        client._async_client = mock_async_client
        caplog.set_level(logging.DEBUG)
        response = await client.async_request("GET", "gzipped_data")

    assert response == json_data
    assert "Decompressing Gzip content" in caplog.text
    mock_async_client.get.assert_awaited_once()
    call_args, call_kwargs = mock_async_client.get.call_args
    assert call_kwargs.get('headers', {}).get('Accept-Encoding') == 'gzip'


def test_sync_request_json_parse_fail(mock_sync_client, caplog):
    """Testa requisição síncrona com JSON inválido."""
    invalid_json_content = b'{"key": "value", invalid}'
    mock_response = create_mock_response(
        200, content_bytes=invalid_json_content, headers={'Content-Type': 'application/json'}
    )
    mock_sync_client.get.return_value = mock_response

    with HTTPClient(base_url="https://api.example.com") as client:
        client._sync_client = mock_sync_client
        caplog.set_level(logging.WARNING)
        response = client.sync_request("GET", "invalid_json")

    assert isinstance(response, dict)
    assert response['content'] == invalid_json_content.decode('utf-8')
    assert "Failed to parse response as JSON" in response['message']
    assert "Failed to parse response as JSON with json.loads" in caplog.text

@pytest.mark.asyncio
async def test_async_request_json_parse_fail(mock_async_client, caplog):
    """Testa requisição assíncrona com JSON inválido."""
    invalid_json_content = b'{"async_key": "value", invalid}'
    mock_response = create_mock_response(
        200, content_bytes=invalid_json_content, headers={'Content-Type': 'application/json'}
    )
    mock_response.aread = AsyncMock(return_value=invalid_json_content) # Mock aread
    mock_async_client.get.return_value = mock_response

    async with HTTPClient(base_url="https://api.example.com") as client:
        client._async_client = mock_async_client
        caplog.set_level(logging.WARNING)
        response = await client.async_request("GET", "invalid_json")

    assert isinstance(response, dict)
    assert response['content'] == invalid_json_content.decode('utf-8')
    assert "Failed to parse response as JSON" in response['message']
    assert "Failed to parse response as JSON with json.loads" in caplog.text


def test_sync_request_gzip_json_parse_fail(mock_sync_client, caplog):
    """Testa requisição síncrona com Gzip e JSON inválido."""
    invalid_json_str = '{"compressed": true, invalid}'
    gzipped_content = gzip_content(invalid_json_str)
    mock_response = create_mock_response(
        200, content_bytes=gzipped_content, headers={'Content-Encoding': 'gzip', 'Content-Type': 'application/json'}
    )
    mock_sync_client.get.return_value = mock_response

    with HTTPClient(base_url="https://api.example.com") as client:
        client._sync_client = mock_sync_client
        caplog.set_level(logging.WARNING)
        response = client.sync_request("GET", "gzipped_invalid_json")

    assert isinstance(response, dict)
    assert response['content'] == invalid_json_str # Conteúdo descompactado
    assert "Failed to parse response as JSON" in response['message']
    assert "Decompressing Gzip content" in caplog.text
    assert "Failed to parse response as JSON with json.loads" in caplog.text

@pytest.mark.asyncio
async def test_async_request_gzip_json_parse_fail(mock_async_client, caplog):
    """Testa requisição assíncrona com Gzip e JSON inválido."""
    invalid_json_str = '{"async_compressed": true, invalid}'
    gzipped_content = gzip_content(invalid_json_str)
    mock_response = create_mock_response(
        200, content_bytes=gzipped_content, headers={'Content-Encoding': 'gzip', 'Content-Type': 'application/json'}
    )
    mock_response.aread = AsyncMock(return_value=gzipped_content) # Mock aread
    mock_async_client.get.return_value = mock_response

    async with HTTPClient(base_url="https://api.example.com") as client:
        client._async_client = mock_async_client
        caplog.set_level(logging.WARNING)
        response = await client.async_request("GET", "gzipped_invalid_json")

    assert isinstance(response, dict)
    assert response['content'] == invalid_json_str # Conteúdo descompactado
    assert "Failed to parse response as JSON" in response['message']
    assert "Decompressing Gzip content" in caplog.text
    assert "Failed to parse response as JSON with json.loads" in caplog.text

def test_sync_request_http_error_with_json_body(mock_sync_client, caplog):
    """Testa erro HTTP síncrono com corpo JSON."""
    error_json = {"error": "Bad Request", "details": "Invalid parameter"}
    error_response = create_mock_response(400, json_data=error_json)
    mock_sync_client.get.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=error_response.request, response=error_response
    )

    with HTTPClient(base_url="https://api.example.com") as client:
        client._sync_client = mock_sync_client
        caplog.set_level(logging.WARNING)
        response = client.sync_request("GET", "error_json")

    assert response == error_json # Deve retornar o JSON do erro
    assert "HTTP Error 400" in caplog.text
    assert "Returning parsed error response" in caplog.text # Verifica log de sucesso na análise do erro

@pytest.mark.asyncio
async def test_async_request_http_error_with_json_body(mock_async_client, caplog):
    """Testa erro HTTP assíncrono com corpo JSON."""
    error_json = {"error": "Unauthorized", "details": "Missing token"}
    error_response = create_mock_response(401, json_data=error_json)
    # Mock aread para o corpo do erro
    error_response.aread = AsyncMock(return_value=json.dumps(error_json).encode('utf-8'))
    mock_async_client.get.side_effect = httpx.HTTPStatusError(
        "Unauthorized", request=error_response.request, response=error_response
    )

    async with HTTPClient(base_url="https://api.example.com") as client:
        client._async_client = mock_async_client
        caplog.set_level(logging.WARNING)
        response = await client.async_request("GET", "error_json")

    assert response == error_json # Deve retornar o JSON do erro
    assert "HTTP Error 401" in caplog.text
    assert "Returning parsed error response" in caplog.text # Verifica log de sucesso na análise do erro

def test_unsupported_method_sync(mock_sync_client):
    """Testa método HTTP não suportado (PUT) síncrono."""
    with HTTPClient(base_url="https://api.example.com") as client:
        client._sync_client = mock_sync_client
        with pytest.raises(ValueError) as exc_info:
            client.sync_request("PUT", "unsupported")
        assert "Unsupported HTTP method: PUT" in str(exc_info.value)

@pytest.mark.asyncio
async def test_unsupported_method_async(mock_async_client):
    """Testa método HTTP não suportado (DELETE) assíncrono."""
    async with HTTPClient(base_url="https://api.example.com") as client:
        client._async_client = mock_async_client
        with pytest.raises(ValueError) as exc_info:
            await client.async_request("DELETE", "unsupported")
        assert "Unsupported HTTP method: DELETE" in str(exc_info.value)
