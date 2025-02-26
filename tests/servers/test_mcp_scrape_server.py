import pytest
import asyncio
from typing import List
from fbpyutils_ai.servers.mcp_scrape_tools import scrape_n

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