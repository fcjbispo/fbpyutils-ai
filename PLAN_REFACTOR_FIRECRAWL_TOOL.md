# Plano de Refatoração da Classe `FireCrawlTool`

**Objetivo:** Refatorar a classe `FireCrawlTool` em `fbpyutils_ai/tools/crawl.py` para manter apenas os métodos `scrape` e `search`, removendo métodos e funções utilitárias não utilizados, e atualizar a documentação e testes unitários correspondentes, preservando os arquivos de especificação.

**Passos:**

1.  **Modificação do Código (`fbpyutils_ai/tools/crawl.py`)**:
    *   **Ação:** Editar o arquivo `fbpyutils_ai/tools/crawl.py`.
    *   **Detalhes:**
        *   Remover as definições completas dos seguintes métodos da classe `FireCrawlTool`: `crawl`, `get_crawl_status`, `cancel_crawl`, `get_crawl_errors`, `get_batch_scrape_status`, `get_batch_scrape_errors`, `batch_scrape`, `get_extract_status`, `extract`, `map`.
        *   Remover as definições completas das seguintes funções utilitárias (métodos privados): `_format_metadata_md`, `_format_links_md`, `_format_scrape_result_md`, `scrape_formatted`, `scrape_multiple`.
        *   Remover a função `scrape_and_store` (se existir como função separada ou dentro de `scrape_multiple`).
        *   Remover os imports não utilizados no início do arquivo: `requests`, `requests.adapters`, `urllib3.util.retry`, `concurrent.futures`.
        *   Manter intactos o método `__init__`, o método `scrape` e o método `search`.
        *   **Verificação:** Garantir que a sintaxe Python esteja correta após as remoções e que os métodos `scrape` e `search` permaneçam funcionalmente inalterados em sua lógica interna e chamadas ao `HTTPClient`.

2.  **Atualização da Documentação**:
    *   **Ação:** Editar o arquivo `DOC.md`.
    *   **Detalhes:**
        *   Revisar a seção referente à classe `FireCrawlTool`.
        *   Remover a documentação e exemplos de uso para os métodos `crawl`, `get_crawl_status`, `cancel_crawl`, `get_crawl_errors`, `get_batch_scrape_status`, `get_batch_scrape_errors`, `batch_scrape`, `get_extract_status`, `extract`, `map`, `scrape_formatted`, `scrape_multiple`.
        *   Manter e, se necessário, refinar a documentação para os métodos `__init__`, `scrape` e `search`, garantindo que descrevam com precisão a funcionalidade atual.
    *   **Ação:** Editar o arquivo `README.md`.
    *   **Detalhes:**
        *   Revisar o conteúdo para identificar e remover quaisquer menções diretas ou exemplos de uso dos métodos removidos.
        *   Manter menções gerais à capacidade de "scrape" e "search" se apropriado.
    *   **Ação:** Manter a pasta `specs/` e todos os seus arquivos intactos.
    *   **Detalhes:** Não realizar nenhuma operação de remoção ou arquivamento nos arquivos dentro de `specs/`.

3.  **Atualização dos Testes Unitários**:
    *   **Ação:** Identificar e remover arquivos de teste.
    *   **Detalhes:**
        *   Remover os seguintes arquivos da pasta `tests/tools/crawl/`: `test_batch_scrape.py`, `test_cancel_crawl.py`, `test_crawl.py`, `test_extract.py`, `test_get_batch_scrape_errors.py`, `test_get_batch_scrape_status.py`, `test_get_crawl_errors.py`, `test_get_crawl_status.py`, `test_get_extract_status.py`, `test_map.py`.
    *   **Ação:** Revisar arquivos de teste existentes.
    *   **Detalhes:**
        *   Revisar o arquivo `tests/tools/crawl/test_scrape.py` para garantir que todos os testes sejam relevantes e funcionais para o método `scrape` remanescente. Remover testes que dependam de funcionalidades removidas.
        *   Revisar o arquivo `tests/tools/crawl/test_search.py` para garantir que todos os testes sejam relevantes e funcionais para o método `search` remanescente. Remover testes que dependam de funcionalidades removidas.
        *   Revisar o arquivo `tests/tools/test_tools.py` e `tests/servers/mcp_scrape_server.py` (e outros arquivos de teste de servidor/integração se aplicável) para remover ou ajustar testes que dependam dos métodos removidos da classe `FireCrawlTool`.
    *   **Verificação:** Garantir que os testes restantes passem após as modificações.

4.  **Verificação Final e Cobertura de Código**:
    *   **Ação:** Executar todos os testes unitários restantes.
    *   **Detalhes:** Utilizar o comando `uv run pytest -s -vv --cov=fbpyutils_ai.tools.crawl --cov-report=xml:coverage.xml --cov-report=html:coverage_html --cov-fail-under=90 tests/tools/crawl/test_scrape.py tests/tools/crawl/test_search.py` (ou um comando similar que execute apenas os testes relevantes) para verificar se os testes passam e se a cobertura de código para o arquivo `crawl.py` atende ao requisito de >= 90%.
    *   **Ação:** Revisar o relatório de cobertura (`coverage_html/index.html`) para identificar áreas não testadas nos métodos `scrape` e `search` e, se necessário, adicionar testes.

## Diagrama (Antes e Depois)

```mermaid
graph TD
    A[FireCrawlTool (Antes)] --> B[__init__]
    A --> C[scrape]
    A --> D[crawl]
    A --> E[get_crawl_status]
    A --> F[cancel_crawl]
    A --> G[get_crawl_errors]
    A --> H[get_batch_scrape_status]
    A --> I[get_batch_scrape_errors]
    A --> J[batch_scrape]
    A --> K[get_extract_status]
    A --> L[extract]
    A --> M[map]
    A --> N[_format_metadata_md]
    A --> O[_format_links_md]
    A --> P[_format_scrape_result_md]
    A --> Q[scrape_formatted]
    A --> R[scrape_multiple]

    S[FireCrawlTool (Depois)] --> B
    S --> C
    S --> T[search]
