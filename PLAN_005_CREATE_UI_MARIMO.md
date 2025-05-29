### Plano de Execução

O objetivo é criar um novo módulo Marimo para a `FireCrawlTool`, expondo os métodos `scrape` e `search` em seções distintas usando `mo.accordion`, e integrá-lo à interface geral.

#### Etapas:

1.  **Criação do Módulo `app.firecrawl_tool.py`:**
    *   Criar o arquivo `fbpyutils_ai/ui/marimo/app.firecrawl_tool.py`.
    *   Copiar a estrutura básica de `app.search_tool.py` (importações, inicialização do `marimo.App`).
    *   Importar a classe `FireCrawlTool` de `fbpyutils_ai/tools/scrape.py`.
    *   Considerar o uso de `fbpyutils_ai/ui/marimo/components.py` para funções auxiliares ou componentes de UI reutilizáveis, se necessário.
    *   Definir as células Marimo para:
        *   Inicializar a `FireCrawlTool`.
        *   Criar os elementos de UI (`mo.ui.text`, `mo.ui.dropdown`, `mo.ui.switch`, etc.) para os parâmetros `url`, `formats` e `onlyMainContent` para o método `scrape`.
        *   Criar os elementos de UI para os parâmetros `query`, `limit` e `lang` para o método `search`.
        *   Implementar a lógica para chamar o método `scrape` da `FireCrawlTool` com base nos valores da UI.
        *   Implementar a lógica para chamar o método `search` da `FireCrawlTool` com base nos valores da UI.
        *   Exibir os resultados de `scrape` e `search` de forma clara (por exemplo, usando `mo.json` ou `mo.md`).
        *   Organizar as seções `scrape` e `search` dentro de um `mo.accordion`.

2.  **Integração na Interface Geral (Futuro):**
    *   Esta etapa será realizada após a finalização dos módulos individuais.
    *   Será necessário criar um arquivo `app.main.py` (ou similar) que importe e exiba os módulos `app.llm_tool.py`, `app.search_tool.py` e `app.firecrawl_tool.py` em uma única interface.
    *   A interface geral utilizará o componente `mo.ui.sidebar` para organizar as diferentes ferramentas.

3.  **Finalização dos Módulos Existentes (Mediante Requisições):**
    *   Esta etapa será realizada conforme suas futuras requisições para `app.llm_tool.py` e `app.search_tool.py`.

4.  **Atualização da Documentação do Projeto:**
    *   Atualizar os arquivos `README.md`, `TODO.md`, `TOOLS.md` e `TREE.md` para incluir a nova ferramenta `FireCrawlTool` e sua funcionalidade.
    *   Adicionar informações sobre a estrutura da UI Marimo e como as ferramentas são integradas.

5.  **Registro no Banco de Memória:**
    *   Atualizar os arquivos do banco de memória (`memory_bank/activeContext.md`, `memory_bank/progress.md`, etc.) para refletir as mudanças no projeto, incluindo a adição da `FireCrawlTool` e a evolução da UI.

6.  **Commit do Repositório:**
    *   Realizar commits significativos após a conclusão de cada etapa principal (criação do módulo, integração, documentação).

#### Diagrama do Plano:

```mermaid
graph TD
    A[Início da Tarefa] --> B{Análise de Código Existente};
    B --> C[Definição de Requisitos da UI];
    C --> D[Criar fbpyutils_ai/ui/marimo/app.firecrawl_tool.py];
    D --> D1[Copiar Estrutura de app.search_tool.py];
    D1 --> D2[Importar FireCrawlTool];
    D2 --> D2a[Considerar Uso de components.py];
    D2a --> D3[Criar UI para Scrape (url, formats, onlyMainContent)];
    D3 --> D4[Criar UI para Search (query, limit, lang)];
    D4 --> D5[Implementar Lógica de Chamada dos Métodos];
    D5 --> D6[Exibir Resultados];
    D6 --> D7[Organizar com mo.accordion];
    D7 --> E[Integração na Interface Geral (mo.ui.sidebar)];
    E --> F[Finalização dos Módulos Existentes (Sob Demanda)];
    F --> G[Atualizar Documentação do Projeto (README.md, TODO.md, TOOLS.md, TREE.md)];
    G --> H[Atualizar Banco de Memória];
    H --> I[Realizar Commits];
    I --> J[Fim da Tarefa];
