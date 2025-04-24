# Plano para Atualizar FireCrawlTool.scrape para API v1

Este documento detalha o plano para atualizar o método `scrape` da classe `FireCrawlTool` no arquivo `fbpyutils_ai/tools/crawl.py` para utilizar a v1 da API do Firecrawl.

## Passos Detalhados

1.  **Atualizar URL Base:**
    *   Modificar o método `__init__` para usar a URL base da v1: `https://api.firecrawl.dev/v1` como padrão, caso a variável de ambiente `FBPY_FIRECRAWL_BASE_URL` não esteja definida.

2.  **Refatorar Método `scrape`:**
    *   **Assinatura e Docstring:** Atualizar a assinatura do método `scrape` e sua docstring para refletir os novos parâmetros da v1 (ex: `formats`, `onlyMainContent`, `includeTags`, `jsonOptions`, `actions`, etc.) e a nova estrutura de resposta. Remover a estrutura aninhada de `pageOptions` e `extractorOptions`.
    *   **Construção do Payload:** Modificar a construção do payload JSON de acordo com a estrutura plana da v1, utilizando os parâmetros recebidos pelo método.
    *   **Tratamento da Resposta:** Manter o tratamento de erros existente, mas garantir que o tipo de retorno `Dict[str, Any]` ainda seja adequado para a variedade de dados que a v1 pode retornar dentro do campo `data`.

3.  **Atualizar Testes Unitários:**
    *   Localizar os testes existentes para `FireCrawlTool` (provavelmente em `tests/tools/test_tools.py` ou criar `tests/tools/test_crawl.py`).
    *   Atualizar ou criar novos testes para o método `scrape` que:
        *   Verifiquem se a URL correta da v1 (`.../v1/scrape`) está sendo chamada.
        *   Utilizem `mocking` para simular a chamada `requests.Session.post`.
        *   Validem se o payload enviado na chamada mockada corresponde à estrutura e aos parâmetros da v1.
        *   Confirmem que o método retorna corretamente a resposta mockada da v1.
        *   Cubram diferentes combinações dos novos parâmetros da v1.

4.  **Atualizar Documentação:**
    *   **`README.md`:** Revisar e atualizar a seção sobre `FireCrawlTool` para mencionar o uso da v1 e refletir quaisquer mudanças nos exemplos de uso do `scrape`.
    *   **`DOC.md`:** Adicionar ou atualizar a documentação do `FireCrawlTool`, detalhando o método `scrape` com seus parâmetros e resposta da v1.
    *   **`TOOLS.md`:** Atualizar a seção "Web Content Extraction Tool" para indicar que a ferramenta principal agora é `FireCrawlTool` utilizando a API v1.
    *   **`TODO.md`:** Atualizar a linha correspondente à "Web Content Extraction Tool" para refletir a atualização para a v1 e o status dos testes.

## Diagrama do Fluxo

```mermaid
graph LR
    A[Iniciar Tarefa: Atualizar scrape para v1] --> B{Analisar Código Atual e API v1};
    B --> C[Identificar Mudanças Necessárias];
    C --> D[Plano Detalhado];
    D --> E{Revisão do Usuário};
    E -- Aprovar --> F[Implementar Mudanças (Modo Código)];
    F --> G[Atualizar __init__ (URL Base)];
    F --> H[Refatorar scrape (Assinatura, Docstring, Payload)];
    F --> I[Atualizar/Criar Testes Unitários];
    F --> J[Atualizar Documentação (README, DOC, TOOLS, TODO)];
    G & H & I & J --> K[Finalizar Tarefa];
    E -- Rejeitar/Modificar --> D;
