# Plano para Atualizar FireCrawlTool para API v1 (Self-Hosted) e Suporte MCP

Este documento detalha o plano para atualizar a classe `FireCrawlTool` no arquivo `fbpyutils_ai/tools/crawl.py` para:
1.  Utilizar a v1 da API do Firecrawl em um ambiente self-hosted.
2.  "Achatar" (flatten) os métodos que utilizam `kwargs`, transformando parâmetros aninhados em parâmetros diretos.
3.  Adicionar métodos para suportar a funcionalidade do servidor MCP `mcp_scrape_server.py`.
4.  Atualizar a documentação e testes correspondentes.

## Requisitos Iniciais

*   Atualizar a classe `FireCrawlTool` para utilizar a v1 da API do serviço firecrawl.dev disponibilizado localmente via SELF HOSTING em um docker container service (fbnet-tools-firecrawl) acessível através das variáveis de ambiente `FBPY_FIRECRAWL_BASE_URL` e `FBPY_FIRECRAWL_API_KEY`.
*   Implementar os serviços `scrape`, `crawl`, `extract`, `map`, `search` e métodos auxiliares (`get_status`, `get_errors`, `cancel`) usando a documentação da API v1 e o `HTTPClient`.
*   **"Achatar" (Flatten) os métodos:** Modificar os métodos `scrape`, `crawl`, `batch_scrape`, `extract`, `map`, `search` para remover o uso de `**kwargs` e dicionários aninhados (como `pageOptions`, `crawlerOptions`, `searchOptions`, `scrapeOptions`). Expor os parâmetros relevantes diretamente na assinatura do método com valores padrão apropriados.
*   **Restrições Self-Hosted:** Garantir que apenas os argumentos suportados pelo modo self-hosted (conforme `specs/SELF_HOST_UNSUPPORTED_PARAMS.md` e `specs/SELF_HOST.md`) sejam utilizados e enviados para a API. Remover parâmetros não suportados ou prover alternativas (ex: `verify_ssl` no `__init__` para `skipTlsVerification`).
*   **Suporte MCP:** Implementar novos métodos (`scrape_formatted`, `scrape_multiple`) na classe `FireCrawlTool` que repliquem a funcionalidade de formatação e processamento paralelo do script `fbpyutils_ai/servers/mcp_scrape_server.py`.
*   **Retorno:** Certificar-se de retornar sempre um JSON de resposta, mesmo em caso de erros.
*   **Qualidade:** Utilizar as recomendações em `VIBE.md` (SOLID, tipos, logs, documentação em inglês, evitar comentários desnecessários).
*   **Testes:** Atualizar/criar testes unitários para todos os métodos modificados e adicionados. A cobertura de 90% é desejável, mas não estritamente obrigatória nesta fase inicial.
*   **Documentação:** Atualizar este plano (`PLAN_UPDATE_FIRECRAWL_V1.md`), `DOC.md`, `README.md`, `TOOLS.md`, e `TODO.md` conforme o progresso.

## Passos Detalhados

A implementação seguirá o ciclo TDD (Test-Driven Development) sempre que possível.

1.  **Refinar `__init__`:**
    *   Confirmar leitura de `FBPY_FIRECRAWL_BASE_URL` (padrão `http://localhost:3005/v1`) e `FBPY_FIRECRAWL_API_KEY` (opcional).
    *   Garantir que `verify_ssl` seja passado e utilizado pelo `HTTPClient`.

2.  **Implementar/Verificar Métodos Auxiliares:**
    *   Implementar/Revisar `get_crawl_status`, `cancel_crawl`, `get_crawl_errors`, `get_batch_scrape_status`, `get_batch_scrape_errors`, `get_extract_status` usando TDD e `HTTPClient`.

3.  **"Flatterizar" Métodos Principais:**
    *   Para cada método (`scrape`, `batch_scrape`, `crawl`, `extract`, `map`, `search`):
        *   Modificar a assinatura para remover `**kwargs` e expor parâmetros relevantes diretamente.
        *   Manter apenas parâmetros suportados pelo self-hosted.
        *   Atualizar docstring (em inglês).
        *   Atualizar/criar testes unitários (`tests/tools/crawl/test_*.py`).
        *   Refatorar o corpo do método para construir o payload v1 correto e usar `HTTPClient`.

4.  **Implementar Suporte MCP - `scrape_formatted`:**
    *   Criar método `scrape_formatted(url: str, tags_to_remove: list[str] = [], timeout: int = 30000, ...) -> str`.
    *   Internamente, chamar o método `scrape` (já "achatado").
    *   Implementar a lógica de formatação Markdown (similar a `_scrape_result_to_markdown`, `_metadata_to_markdown`, `_links_to_markdown` do servidor MCP, possivelmente como métodos privados `_format_metadata_md`, `_format_links_md`, `_format_scrape_result_md`).
    *   Criar testes unitários para `scrape_formatted`.

5.  **Implementar Suporte MCP - `scrape_multiple`:**
    *   Criar método `scrape_multiple(urls: list[str], tags_to_remove: list[str] = [], timeout: int = 30000, ...) -> list[str]`.
    *   Implementar paralelização *síncrona* (ex: `concurrent.futures.ThreadPoolExecutor`) para chamar `scrape_formatted` para cada URL na lista.
    *   Retornar a lista de strings Markdown formatadas.
    *   Criar testes unitários para `scrape_multiple`.

6.  **Atualizar Documentação Final:**
    *   Revisar e atualizar `README.md`, `DOC.md`, `TOOLS.md` e `TODO.md` para refletir todas as mudanças na classe `FireCrawlTool`.
    *   Atualizar este arquivo (`PLAN_UPDATE_FIRECRAWL_V1.md`) se necessário.

## Diagrama do Fluxo Atualizado

::: mermaid
graph TD
    A[Iniciar Tarefa] --> B{Análise Docs & Restrições Self-Hosted & MCP Server}
    B --> C[Refinar __init__]
    C --> D[Implementar/Verificar Métodos Auxiliares com TDD]
    D --> E[Flatterizar e Implementar scrape com TDD]
    E --> F[Flatterizar e Implementar batch_scrape com TDD]
    F --> G[Flatterizar e Implementar crawl com TDD]
    G --> H[Flatterizar e Implementar extract com TDD]
    H --> I[Flatterizar e Implementar map com TDD]
    I --> J[Flatterizar e Implementar search com TDD]
    J --> K[Implementar scrape_formatted (MCP Support) com TDD]
    K --> L[Implementar scrape_multiple (MCP Support) com TDD]
    L --> M[Atualizar Documentação (README, DOC, TOOLS, TODO)]
    M --> N[Atualizar PLAN_UPDATE_FIRECRAWL_V1.md]
    N --> O{Revisão do Plano com o Usuário}
    O -- Aprovar --> P[Implementação Modo Código]
    O -- Modificar --> B
    P --> Q[Fim]
:::
