# Plano de Release v0.1.2: Remoção de Implementações MCP

**Objetivo:** Remover todas as implementações e referências ao Model Context Protocol (MCP) do projeto `FBPyUtils-AI`, preparando-o para uma futura implementação em um projeto dedicado.

**Passos:**

1.  **Remoção de Módulos MCP:**
    *   Excluir o diretório `fbpyutils_ai/servers/` e todo o seu conteúdo (`__init__.py`, `mcp_scrape_server.py`, `mcp_search_server.py`, `mcp_servers.py`).

2.  **Atualização de Arquivos Python:**
    *   Remover importações e chamadas relacionadas a MCP em `tests_integration/test_scrape_server_integration.py`.
    *   Remover quaisquer outras referências a MCP em arquivos `.py` que possam ter sido identificadas (ex: `.sandbox.py` se for um arquivo de código ativo).

3.  **Atualização da Documentação (Memory Bank e outros arquivos `.md`):**
    *   **`TREE.md`**: Remover as entradas para os arquivos MCP em `fbpyutils_ai/servers/`.
    *   **`TODO.md`**: Remover ou atualizar itens de tarefa relacionados a MCP (ex: "Internet Search Tool", "Web Content Extraction Tool" que mencionam MCP).
    *   **`README.md`**: Remover as seções "Web Scraping Server", "Web Search Server" e "MCP Server Entrypoint", e quaisquer outras menções a MCP.
    *   **`PLAN_004_REFACTOR_FIRECRAWL_TOOL.md` e `PLAN_003_UPDATE_FIRECRAWL_V1.md`**: Remover ou ajustar referências a MCP e `mcp_scrape_server.py`.
    *   **`PLAN.md`**: Atualizar a descrição dos planos anteriores para remover menções a MCP, se houver.
    *   **`memory_bank/techContext.md`**: Remover referências a `pandas` e `duckdb` se a única razão para sua inclusão era o `mcp_search_server.py`. Remover a instrução para iniciar o servidor MCP.
    *   **`memory_bank/systemPatterns.md`**: Remover a seção "MCP Servers" e quaisquer outras menções a MCP, incluindo dependências e padrões de design relacionados.
    *   **`memory_bank/projectbrief.md`**: Remover a menção a "MCP server implementations".
    *   **`memory_bank/progress.md`**: Atualizar o status de "Internet Search" e "Web Content Extraction" para remover a menção de exposição via MCP, e remover a menção de baixa cobertura de testes para os módulos MCP.

4.  **Verificação e Testes:**
    *   Garantir que o projeto compile e execute sem erros após a remoção.
    *   Executar todos os testes existentes para garantir que nenhuma funcionalidade não-MCP foi quebrada.

**Diagrama do Fluxo de Trabalho:**

```mermaid
graph TD
    A[Início da Release v0.1.2] --> B{Identificar Arquivos MCP};
    B --> C[Remover Diretório fbpyutils_ai/servers];
    C --> D[Atualizar Arquivos Python Relacionados];
    D --> E[Atualizar Documentação .md];
    E --> F[Executar Testes Existentes];
    F --> G{Testes Passaram?};
    G -- Sim --> H[Concluir Plano de Release];
    G -- Não --> I[Corrigir Erros e Repetir];
    I --> F;
