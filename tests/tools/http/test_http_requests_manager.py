import io
import gzip
import json
import pytest
import requests
import logging
from unittest.mock import patch, MagicMock
from requests.exceptions import Timeout, RequestException, HTTPError
import tenacity
from requests.adapters import HTTPAdapter

from fbpyutils_ai.tools.http import RequestsManager

# --- Fixtures ---

@pytest.fixture
def mock_session():
    """Fixture para mockar requests.Session e seus métodos GET e POST."""
    with patch('requests.Session') as mock_factory:
        mock_instance = mock_factory.return_value
        # Configurar mocks para GET e POST
        mock_instance.get = MagicMock()
        mock_instance.post = MagicMock()
        yield mock_instance

# --- Helper Functions ---

def create_requests_mock_response(status_code, json_data=None, text_data=None, content_bytes=None, headers=None, encoding='utf-8'):
    """Cria um objeto requests.Response mockado."""
    mock_resp = MagicMock(spec=requests.Response)
    mock_resp.status_code = status_code
    mock_resp.request = MagicMock(spec=requests.PreparedRequest) # Mock request attribute

    final_headers = {'Content-Type': 'application/json'} if json_data else {'Content-Type': 'text/plain'}
    if headers:
        final_headers.update(headers)
    mock_resp.headers = final_headers

    content_to_use = content_bytes
    if content_to_use is None:
        if json_data is not None:
            content_to_use = json.dumps(json_data).encode(encoding)
        elif text_data is not None:
            content_to_use = text_data.encode(encoding)
        else:
            content_to_use = b''

    mock_resp.content = content_to_use
    # requests infere encoding, mas podemos mocká-lo se necessário
    mock_resp.encoding = encoding
    # .text property decodifica content
    mock_resp.text = content_to_use.decode(encoding, errors='ignore')

    # Mock .json()
    if json_data is not None and status_code < 300:
        mock_resp.json.return_value = json_data
    else:
        # Simular erro se .json() for chamado em resposta não-JSON ou erro
        mock_resp.json.side_effect = json.JSONDecodeError("Simulated decode error", "", 0)

    # Mock raise_for_status
    if status_code >= 400:
        mock_resp.raise_for_status.side_effect = HTTPError(f"{status_code} Error", response=mock_resp)
    else:
        mock_resp.raise_for_status.return_value = None

    # Mock iter_lines para streaming
    mock_resp.iter_lines.return_value = iter([line + b'\n' for line in content_to_use.splitlines()])

    return mock_resp

def gzip_content(data: Union[dict, str]) -> bytes:
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

def test_make_request_success_post(mock_session):
    """Testa POST bem-sucedido com resposta normal."""
    mock_response = create_requests_mock_response(200, json_data={"success": True, "data": "test_data"})
    mock_session.post.return_value = mock_response

    result = RequestsManager.make_request(
        session=mock_session,
        url="https://test.com/api",
        headers={"Custom-Header": "value"}, # Test custom header
        json_data={"test": "data"},
        timeout=10,
        method="POST",
        stream=False
    )

    expected_headers = {"Custom-Header": "value", 'Accept-Encoding': 'gzip'}
    mock_session.post.assert_called_once_with(
        "https://test.com/api",
        headers=expected_headers,
        json={"test": "data"},
        timeout=(10, 10),
        stream=False # Adicionado para clareza
    )
    assert result == {"success": True, "data": "test_data"}

def test_make_request_success_get(mock_session):
    """Testa GET bem-sucedido com resposta normal."""
    mock_response = create_requests_mock_response(200, json_data={"success": True, "data": "test_data"})
    mock_session.get.return_value = mock_response

    result = RequestsManager.make_request(
        session=mock_session,
        url="https://test.com/api",
        headers={"Custom-Header": "value"},
        json_data={"param1": "value1"}, # GET usa isso como params
        timeout=10,
        method="GET", # Explicitamente GET
        stream=False
    )

    expected_headers = {"Custom-Header": "value", 'Accept-Encoding': 'gzip'}
    mock_session.get.assert_called_once_with(
        "https://test.com/api",
        headers=expected_headers,
        params={"param1": "value1"},
        timeout=(10, 10)
    )
    assert result == {"success": True, "data": "test_data"}

def test_make_request_streaming_post(mock_session):
    """Testa POST bem-sucedido com resposta streaming."""
    stream_data = [
        b'data: {"id": 1, "content": "first chunk"}',
        b'data: {"id": 2, "content": "second chunk"}',
        b'data: [DONE]'
    ]
    # Juntar as linhas para simular o content bruto
    raw_content = b'\n'.join(stream_data)
    mock_response = create_requests_mock_response(200, content_bytes=raw_content, headers={'Content-Type': 'text/event-stream'})
    # Mock iter_lines especificamente
    mock_response.iter_lines.return_value = iter(stream_data)
    mock_session.post.return_value = mock_response

    stream_generator = RequestsManager.make_request(
        session=mock_session,
        url="https://test.com/api/stream",
        headers={"Accept": "text/event-stream"},
        json_data={"prompt": "stream this"},
        timeout=30,
        method="POST",
        stream=True
    )

    expected_headers = {"Accept": "text/event-stream", 'Accept-Encoding': 'gzip'}
    mock_session.post.assert_called_once_with(
        "https://test.com/api/stream",
        headers=expected_headers,
        json={"prompt": "stream this"},
        timeout=(30, 30),
        stream=True
    )

    results = list(stream_generator)
    assert len(results) == 2
    assert results[0] == {"id": 1, "content": "first chunk"}
    assert results[1] == {"id": 2, "content": "second chunk"}

def test_make_request_streaming_get_fails(mock_session):
    """Testa que streaming com GET levanta ValueError."""
    with pytest.raises(ValueError) as excinfo:
        RequestsManager.make_request(
            session=mock_session,
            url="https://test.com/api/stream",
            headers={},
            json_data={},
            timeout=10,
            method="GET",
            stream=True
        )
    assert "Streaming is only supported for POST requests" in str(excinfo.value)

def test_make_request_timeout_get(mock_session):
    """Testa GET que falha com Timeout."""
    mock_session.get.side_effect = Timeout("Request timed out")

    with pytest.raises(tenacity.RetryError) as excinfo:
        RequestsManager.make_request(
            session=mock_session, url="https://test.com/api", headers={}, json_data={}, timeout=5, method="GET"
        )
    assert isinstance(excinfo.value.__cause__, Timeout)

def test_make_request_timeout_post(mock_session):
    """Testa POST que falha com Timeout."""
    mock_session.post.side_effect = Timeout("Request timed out")

    with pytest.raises(tenacity.RetryError) as excinfo:
        RequestsManager.make_request(
            session=mock_session, url="https://test.com/api", headers={}, json_data={}, timeout=5, method="POST"
        )
    assert isinstance(excinfo.value.__cause__, Timeout)

def test_make_request_request_exception_post(mock_session):
    """Testa POST que falha com RequestException."""
    mock_session.post.side_effect = RequestException("Connection failed")

    with pytest.raises(tenacity.RetryError) as excinfo:
        RequestsManager.make_request(
            session=mock_session, url="https://test.com/api", headers={}, json_data={}, timeout=10, method="POST"
        )
    assert isinstance(excinfo.value.__cause__, RequestException)

def test_make_request_request_exception_get(mock_session):
    """Testa GET que falha com RequestException."""
    mock_session.get.side_effect = RequestException("Connection failed")

    with pytest.raises(tenacity.RetryError) as excinfo:
        RequestsManager.make_request(
            session=mock_session, url="https://test.com/api", headers={}, json_data={}, timeout=10, method="GET"
        )
    assert isinstance(excinfo.value.__cause__, RequestException)

def test_retry_logic_post(mock_session):
    """Testa lógica de retry para POST."""
    mock_response = create_requests_mock_response(200, json_data={"success": True})
    mock_session.post.side_effect = [
        RequestException("First failure"),
        RequestException("Second failure"),
        mock_response
    ]

    result = RequestsManager.make_request(
        session=mock_session, url="https://test.com/api", headers={}, json_data={}, timeout=10, method="POST"
    )
    assert result == {"success": True}
    assert mock_session.post.call_count == 3

def test_retry_logic_get(mock_session):
    """Testa lógica de retry para GET."""
    mock_response = create_requests_mock_response(200, json_data={"success": True})
    mock_session.get.side_effect = [
        RequestException("First failure"),
        RequestException("Second failure"),
        mock_response
    ]

    result = RequestsManager.make_request(
        session=mock_session, url="https://test.com/api", headers={}, json_data={}, timeout=10, method="GET"
    )
    assert result == {"success": True}
    assert mock_session.get.call_count == 3

@pytest.mark.parametrize("invalid_method", ["PUT", "DELETE", "PATCH", "HEAD"])
def test_invalid_method(mock_session, invalid_method):
    """Testa métodos HTTP inválidos."""
    with pytest.raises(ValueError) as excinfo:
        RequestsManager.make_request(
            session=mock_session, url="https://test.com/api", headers={}, json_data={}, timeout=10, method=invalid_method
        )
    assert f"Unsupported HTTP method: {invalid_method}" in str(excinfo.value)

def test_create_session():
    """Testa se create_session retorna uma Session configurada."""
    # Usar patch real aqui para verificar a montagem do adapter
    with patch('requests.adapters.HTTPAdapter') as mock_adapter_class:
        mock_adapter_instance = MagicMock()
        mock_adapter_class.return_value = mock_adapter_instance

        session = RequestsManager.create_session(max_retries=3, bearer_token="test_token", verify_ssl=False)

        assert isinstance(session, requests.Session)
        mock_adapter_class.assert_called_once_with(max_retries=3)
        assert session.mount.call_count == 2 # http e https
        assert session.headers['Authorization'] == "Bearer test_token"
        assert session.verify is False

def test_request_convenience_method(caplog):
    """Testa o método de conveniência `request`."""
    # Mock make_request e create_session dentro do RequestsManager
    with patch.object(RequestsManager, '_execute_request_with_retry') as mock_execute, \
         patch.object(RequestsManager, 'create_session') as mock_create_session:

        mock_session_instance = MagicMock()
        mock_create_session.return_value = mock_session_instance
        mock_execute.return_value = {"convenience": "works"}

        result = RequestsManager.request(
            url="https://convenience.com/api",
            headers={"X-Test": "header"},
            json_data={"payload": "data"},
            timeout=20,
            method="POST",
            stream=False,
            max_retries=4,
            bearer_token="abc"
        )

        mock_create_session.assert_called_once_with(
            max_retries=4, auth=None, bearer_token="abc", verify_ssl=True
        )
        expected_headers = {"X-Test": "header", 'Accept-Encoding': 'gzip'}
        mock_execute.assert_called_once_with(
            session=mock_session_instance,
            url="https://convenience.com/api",
            headers=expected_headers,
            json_data={"payload": "data"},
            timeout=(20, 20),
            method="POST",
            stream=False
        )
        assert result == {"convenience": "works"}

# --- Novos Testes para Gzip e JSON Fallback ---

def test_make_request_gzip_json_success(mock_session, caplog):
    """Testa requisição com Gzip e JSON válido."""
    json_data = {"compressed": True}
    # requests lida com descompressão automaticamente se Content-Encoding estiver presente
    mock_response = create_requests_mock_response(
        200, json_data=json_data, headers={'Content-Encoding': 'gzip'}
    )
    mock_session.get.return_value = mock_response

    with caplog.at_level(logging.DEBUG):
        result = RequestsManager.make_request(
            session=mock_session, url="https://test.com/gzip", headers={}, json_data={}, method="GET"
        )

    assert result == json_data
    mock_session.get.assert_called_once()
    call_args, call_kwargs = mock_session.get.call_args
    assert call_kwargs.get('headers', {}).get('Accept-Encoding') == 'gzip'
    # Verificar que não há logs de erro de parsing
    assert "Failed to parse response" not in caplog.text

def test_make_request_json_parse_fail_fallback_success(mock_session, caplog):
    """Testa falha em response.json() mas sucesso com json.loads(response.text)."""
    valid_json_str = '{"key": "value"}'
    mock_response = create_requests_mock_response(200, text_data=valid_json_str)
    # Simular falha no método .json()
    mock_response.json.side_effect = json.JSONDecodeError("Mocked json() failure", "", 0)
    mock_session.get.return_value = mock_response

    with caplog.at_level(logging.WARNING):
        result = RequestsManager.make_request(
            session=mock_session, url="https://test.com/fallback", headers={}, json_data={}, method="GET"
        )

    assert result == {"key": "value"} # Deve parsear com sucesso no fallback
    assert "Failed to parse response with response.json()" in caplog.text # Log de aviso da primeira falha
    assert "Failed to parse response as JSON with json.loads" not in caplog.text # Não deve logar a segunda falha

def test_make_request_json_parse_fail_both(mock_session, caplog):
    """Testa falha em response.json() e json.loads(response.text)."""
    invalid_json_text = '{"key": "value", invalid}'
    mock_response = create_requests_mock_response(200, text_data=invalid_json_text)
    # Simular falha no método .json()
    mock_response.json.side_effect = json.JSONDecodeError("Mocked json() failure", "", 0)
    mock_session.get.return_value = mock_response

    with caplog.at_level(logging.WARNING):
        result = RequestsManager.make_request(
            session=mock_session, url="https://test.com/double_fail", headers={}, json_data={}, method="GET"
        )

    assert isinstance(result, dict)
    assert result['content'] == invalid_json_text
    assert "Failed to parse response as JSON" in result['message']
    assert "Failed to parse response with response.json()" in caplog.text # Log da primeira falha
    assert "Failed to parse response as JSON with json.loads" in caplog.text # Log da segunda falha (erro)

def test_make_request_http_error_with_json_body(mock_session, caplog):
    """Testa erro HTTP com corpo JSON."""
    error_json = {"error": "Bad Request", "details": "Invalid parameter"}
    mock_response = create_requests_mock_response(400, json_data=error_json)
    # Configurar o side_effect para levantar HTTPError
    mock_session.get.side_effect = HTTPError("400 Client Error", response=mock_response)

    with caplog.at_level(logging.WARNING):
        # A exceção HTTPError é capturada internamente e o JSON do erro é retornado
        result = RequestsManager.make_request(
            session=mock_session, url="https://test.com/error_json", headers={}, json_data={}, method="GET"
        )

    assert result == error_json
    assert "HTTP Error 400" in caplog.text
    assert "Could not parse HTTP error response as JSON" not in caplog.text # Deve ter parseado com sucesso

def test_make_request_http_error_no_json_body(mock_session, caplog):
    """Testa erro HTTP sem corpo JSON."""
    error_text = "Internal Server Error"
    mock_response = create_requests_mock_response(500, text_data=error_text, headers={'Content-Type': 'text/plain'})
    # Configurar o side_effect para levantar HTTPError
    mock_session.get.side_effect = HTTPError("500 Server Error", response=mock_response)

    with caplog.at_level(logging.WARNING):
        # A exceção HTTPError é capturada, mas o parsing JSON falha
        result = RequestsManager.make_request(
            session=mock_session, url="https://test.com/error_no_json", headers={}, json_data={}, method="GET"
        )

    assert isinstance(result, dict)
    assert result['content'] == error_text
    assert result['status_code'] == 500
    assert "HTTP Error: 500" in result['message']
    assert "HTTP Error 500" in caplog.text
    assert "Could not parse HTTP error response as JSON" in caplog.text # Log de falha no parsing
