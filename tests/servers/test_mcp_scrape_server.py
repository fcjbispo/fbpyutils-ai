import pytest
import asyncio
from typing import List, AsyncGenerator, Union # Adicionado Union e AsyncGenerator para clareza
from fbpyutils_ai.servers.mcp_scrape_server import scrape, scrape_n # Adicionado import de scrape

# URLs de teste
TEST_URLS = [
    'https://www.python.org',
    'https://docs.python.org/3/',
    'https://pypi.org'
]

@pytest.mark.asyncio
async def test_scrape_n_normal_mode():
    """Testa o modo normal da função scrape_n que retorna uma lista completa."""
    # Executa scrape com timeout reduzido
    results = await scrape_n(TEST_URLS, timeout=10000)
    
    # Verifica se retornou uma lista
    assert isinstance(results, list), "Resultado deve ser uma lista"
    
    # Verifica se retornou o número correto de resultados
    assert len(results) == len(TEST_URLS), f"Esperado {len(TEST_URLS)} resultados, obtido {len(results)}"
    
    # Verifica se cada resultado é uma string não vazia
    for result in results:
        assert isinstance(result, str), "Cada resultado deve ser uma string"
        assert result.strip(), "Resultado não deve ser vazio"
        assert "# Page Contents:" in result, "Resultado deve conter o cabeçalho esperado"

@pytest.mark.asyncio
async def test_scrape_n_stream_mode():
    """Testa o modo streaming da função scrape_n que retorna resultados incrementalmente."""
    results: List[str] = []
    
    # Obtém o generator de streaming
    stream_gen = await scrape_n(TEST_URLS, timeout=10000, stream=True)
    
    # Coleta resultados do generator
    async for result in stream_gen:
        assert isinstance(result, str), "Cada resultado deve ser uma string"
        assert result.strip(), "Resultado não deve ser vazio"
        assert "# Page Contents:" in result, "Resultado deve conter o cabeçalho esperado"
        results.append(result)
    
    # Verifica se recebemos todos os resultados
    assert len(results) == len(TEST_URLS), f"Esperado {len(TEST_URLS)} resultados, obtido {len(results)}"

@pytest.mark.asyncio
async def test_scrape_n_empty_urls():
    """Testa o comportamento da função scrape_n com lista vazia de URLs."""
    # Testa modo normal
    results = await scrape_n([])
    assert isinstance(results, list), "Resultado deve ser uma lista"
    assert len(results) == 0, "Lista deve estar vazia"
    
    # Testa modo streaming
    stream_gen = await scrape_n([], stream=True)
    results = [r async for r in stream_gen]
    assert len(results) == 0, "Lista deve estar vazia"

@pytest.mark.asyncio
async def test_scrape_n_invalid_urls():
    """Testa o comportamento da função scrape_n com URLs inválidas."""
    invalid_urls = ['http://invalid-url-for-test.xyz']
    
    # Testa modo normal
    results = await scrape_n(invalid_urls, timeout=5000)
    assert len(results) == 1, "Deve retornar um resultado mesmo para URL inválida"
    assert "Error scraping" in results[0], "Deve conter mensagem de erro"
    
    # Testa modo streaming
    stream_gen = await scrape_n(invalid_urls, timeout=5000, stream=True)
    results = [r async for r in stream_gen]
    assert len(results) == 1, "Deve retornar um resultado mesmo para URL inválida"
    assert "Error scraping" in results[0], "Deve conter mensagem de erro"

@pytest.mark.asyncio
async def test_scrape_n_mixed_urls():
    """Testa o comportamento da função scrape_n com mix de URLs válidas e inválidas."""
    mixed_urls = [
        'https://www.python.org',
        'http://invalid-url-for-test.xyz',
        'https://pypi.org'
    ]
    
    # Testa modo normal
    results = await scrape_n(mixed_urls, timeout=10000)
    assert len(results) == len(mixed_urls), "Deve retornar resultado para cada URL"
    
    valid_results = [r for r in results if "Error scraping" not in r]
    error_results = [r for r in results if "Error scraping" in r]
    
    assert len(valid_results) >= 1, "Deve ter pelo menos um resultado válido"
    assert len(error_results) >= 1, "Deve ter pelo menos um erro"
    
    # Testa modo streaming
    stream_gen = await scrape_n(mixed_urls, timeout=10000, stream=True)
    results = [r async for r in stream_gen]
    
    assert len(results) == len(mixed_urls), "Deve retornar resultado para cada URL"
    
    valid_results = [r for r in results if "Error scraping" not in r]
    error_results = [r for r in results if "Error scraping" in r]
    
    assert len(valid_results) >= 1, "Deve ter pelo menos um resultado válido"
    assert len(error_results) >= 1, "Deve ter pelo menos um erro"


@pytest.mark.asyncio
async def test_scrape_single_valid_url():
    """Testa a função scrape com uma URL válida."""
    url = 'https://www.python.org'
    # Executa scrape com timeout reduzido
    result = await scrape(url, timeout=10000)

    # Verifica se o resultado é uma string não vazia e contém o conteúdo esperado
    assert isinstance(result, str), "Resultado deve ser uma string"
    assert result.strip(), "Resultado não deve ser vazio"
    assert "# Page Contents:" in result, "Resultado deve conter o cabeçalho esperado"
    assert "Error scraping" not in result, "Não deve conter mensagem de erro de scraping"
    assert "Error processing scrape result" not in result, "Não deve conter mensagem de erro de processamento"

@pytest.mark.asyncio
async def test_scrape_single_invalid_url():
    """Testa a função scrape com uma URL inválida."""
    url = 'http://invalid-url-for-test.xyz'
    # Executa scrape com timeout reduzido
    result = await scrape(url, timeout=5000)

    # Verifica se o resultado é uma string e contém uma mensagem de erro
    assert isinstance(result, str), "Resultado deve ser uma string"
    # O erro pode vir do Firecrawl ou do processamento interno
    assert "Error scraping" in result or "Error processing scrape result" in result or "No content found" in result, \
           "Resultado deve conter uma mensagem de erro ou 'No content found'"
