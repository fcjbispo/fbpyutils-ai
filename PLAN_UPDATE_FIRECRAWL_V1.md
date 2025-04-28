# Plano para Atualizar FireCrawlTool para API v1 (Self-Hosted)

Este documento detalha o plano para atualizar a classe `FireCrawlTool` no arquivo `fbpyutils_ai/tools/crawl.py` para utilizar a v1 da API do Firecrawl em um ambiente self-hosted.

## Requisitos Iniciais

*   Atualizar a classe FireCrawlTool para utilizar a v1 da api do serviço firecrawl.dev disponibilizado localmente via SELF HOSTING em um docker container service (fbnet-tools-firecrawl) acessível através das variáveis de ambiente FBPY_FIRECRAWL_BASE_URL e FBPY_FIRECRAWL_API_KEY.
*   Utilize a documentação fornecida e os scripts de suporte (http.py) para implementar os seguintes serviços na classe FireCrawlTool: scrape, crawl, extract, map, search.
*   Considere que alguns serviços dependem de métodos complementares para suas funcionalidades como por exemplo: get_status, get_errors, cancel. Providencie as respectivas funcionalidades conforme a necessidade para cada método principal.
*   Tenha com ponto principal que o serviço fornecido pela classe FireCrawlTool deverá funcionar sob as restrições do SELF HOSTING, assim nem todas as funcionalidades poderão ser providas. Use o documento SELF_HOST.md para identificar os ajustes nas requisições a serem enviadas para o serviço e as respostas compatíveis e métodos complementares que poderão ser implementados.
*   **Garantir que apenas os argumentos suportados pelo modo SELF_HOST sejam utilizados nos métodos da classe FireCrawlTool e enviados para a API.**
*   **Verificar o documento `specs/SELF_HOST_UNSUPPORTED_PARAMS.md` para identificar os argumentos não suportados.**
*   **Remover argumentos não suportados que não sejam obrigatórios. Para `skipTlsVerification`, prover alternativa via configuração do `HTTPClient` na inicialização da classe.**
*   Utilize as classes auxiliares para enviar as requisições. Escolha a mais apropriada da bibilioteca http.py.
*   Simplifique ao máximo os argumentos a serem passados para cada serviço disponibilizado e funções auxiliares, no entanto, implemente TUDO que for suportado pelo modo SELF_HOST.
*   Certifique-se de retornar sempre um JSON de resposta mesmo que em caso de erros.
*   Utilize as recomendações em VIBE.md para guiá-lo de forma geral. EVITE inserir comentários desnecessários no meio do código a fim de reduzir ao máximo o número de linhas.
*   Para este primeiro momento, desconsidere a cobertura de testes de 90%.
*   Atualize o PLAN_UPDATE_FIRECRAWL_V1.md para a execução dos próximos passo. Inclua estas instruções como requisitos iniciais do plano.
*   Pergunte-me qualquer outra informação que você julgar necessário.

## Passos Detalhados

A implementação será realizada método por método, seguindo uma ordem de dependência (do menos dependente para o mais dependente). Para cada método, será seguido o ciclo completo de TDD: especificação dos casos de teste, criação dos testes unitários e, em seguida, a implementação do código efetivo, aderindo aos princípios SOLID e às diretrizes do VIBE.md. Os testes unitários para a classe `FireCrawlTool` serão armazenados na pasta `tests/tools/crawl/`.

1.  **Atualizar `__init__`:**
    *   Garantir que a URL base seja lida da variável de ambiente `FBPY_FIRECRAWL_BASE_URL` e utilize `http://localhost:3005/v1` como padrão para o modo self-hosted, conforme a documentação `SELF_HOST.md`.
    *   Manter a leitura da chave de API da variável de ambiente `FBPY_FIRECRAWL_API_KEY`, mas considerar que ela é opcional no modo self-hosted.
    *   Adicionar um parâmetro `verify_ssl` ao `__init__` da classe `FireCrawlTool` que será passado para o `HTTPClient` para controlar a verificação TLS/SSL, substituindo o parâmetro `skipTlsVerification` nos métodos individuais.
    *   Utilizar a classe `HTTPClient` do arquivo `http.py` para gerenciar as requisições, configurando-a com a URL base, os headers apropriados e o valor de `verify_ssl`.
2.  **Implementar `get_crawl_status`:** (Menos dependente dos endpoints principais)
    *   Especificar casos de teste para obter o status de um job de crawl.
    *   Criar testes unitários para `get_crawl_status` utilizando mocking para a requisição HTTP em `tests/tools/crawl/test_get_crawl_status.py`.
    *   Implementar o método `get_crawl_status` utilizando o `HTTPClient` para enviar a requisição GET para `/crawl/{job_id}` e tratar a resposta.
3.  **Implementar `cancel_crawl`:** (Menos dependente dos endpoints principais)
    *   Especificar casos de teste para cancelar um job de crawl.
    *   Criar testes unitários para `cancel_crawl` utilizando mocking para a requisição HTTP em `tests/tools/crawl/test_cancel_crawl.py`.
    *   Implementar o método `cancel_crawl` utilizando o `HTTPClient` para enviar a requisição DELETE para `/crawl/cancel/{job_id}` e tratar a resposta.
4.  **Implementar `get_crawl_errors`:** (Menos dependente dos endpoints principais)
    *   Especificar casos de teste para obter os erros de um job de crawl.
    *   Criar testes unitários para `get_crawl_errors` utilizando mocking para a requisição HTTP em `tests/tools/crawl/test_get_crawl_errors.py`.
    *   Implementar o método `get_crawl_errors` utilizando o `HTTPClient` para enviar a requisição GET para `/crawl/{job_id}/errors` e tratar a resposta.
5.  **Implementar `get_batch_scrape_status`:** (Menos dependente dos endpoints principais)
    *   Especificar casos de teste para obter o status de um job de batch scrape.
    *   Criar testes unitários para `get_batch_scrape_status` utilizando mocking para a requisição HTTP em `tests/tools/crawl/test_get_batch_scrape_status.py`.
    *   Implementar o método `get_batch_scrape_status` utilizando o `HTTPClient` para enviar a requisição GET para `/batch/scrape/{id}` e tratar a resposta.
6.  **Implementar `get_batch_scrape_errors`:** (Menos dependente dos endpoints principais)
    *   Especificar casos de teste para obter os erros de um job de batch scrape.
    *   Criar testes unitários para `get_batch_scrape_errors` utilizando mocking para a requisição HTTP em `tests/tools/crawl/test_get_batch_scrape_errors.py`.
    *   Implementar o método `get_batch_scrape_errors` utilizando o `HTTPClient` para enviar a requisição GET para `/batch/scrape/{id}/errors` e tratar a resposta.
7.  **Implementar `get_extract_status`:** (Menos dependente dos endpoints principais)
    *   Especificar casos de teste para obter o status de um job de extract.
    *   Criar testes unitários para `get_extract_status` utilizando mocking para a requisição HTTP em `tests/tools/crawl/test_get_extract_status.py`.
    *   Implementar o método `get_extract_status` utilizando o `HTTPClient` para enviar a requisição GET para `/extract/{id}` e tratar a resposta.
8.  **Implementar `scrape`:** (Depende de `__init__`)
    *   Especificar casos de teste para o método `scrape`, considerando os parâmetros suportados no modo self-hosted.
    *   Criar testes unitários para `scrape` utilizando mocking para a requisição HTTP em `tests/tools/crawl/test_scrape.py`.
    *   Refatorar o método `scrape` existente para aceitar os parâmetros suportados, construir o payload e utilizar o `HTTPClient` para enviar a requisição POST para `/scrape`.
9.  **Implementar `batch_scrape`:** (Depende de `__init__` e parâmetros de scrape)
    *   Especificar casos de teste para o método `batch_scrape`, considerando os parâmetros suportados no modo self-hosted.
    *   Criar testes unitários para `batch_scrape` utilizando mocking para a requisição HTTP em `tests/tools/crawl/test_batch_scrape.py`.
    *   Implementar o método `batch_scrape` para aceitar os parâmetros suportados, construir o payload e utilizar o `HTTPClient` para enviar a requisição POST para `/batch/scrape`.
10. **Implementar `crawl`:** (Depende de `__init__` e parâmetros de scrape)
    *   Especificar casos de teste para o método `crawl`, considerando os parâmetros suportados no modo self-hosted.
    *   Criar testes unitários para `crawl` utilizando mocking para a requisição HTTP em `tests/tools/crawl/test_crawl.py`.
    *   Implementar o método `crawl` para aceitar os parâmetros suportados, construir o payload e utilizar o `HTTPClient` para enviar a requisição POST para `/crawl`.
11. **Implementar `extract`:** (Depende de `__init__` e parâmetros de scrape)
    *   Especificar casos de teste para o método `extract`, considerando os parâmetros suportados no modo self-hosted.
    *   Criar testes unitários para `extract` utilizando mocking para a requisição HTTP em `tests/tools/crawl/test_extract.py`.
    *   Implementar o método `extract` para aceitar os parâmetros suportados, construir o payload e utilizar o `HTTPClient` para enviar a requisição POST para `/extract`.
12. **Implementar `map`:** (Depende de `__init__`)
    *   Especificar casos de teste para o método `map`, considerando os parâmetros suportados no modo self-hosted.
    *   Criar testes unitários para `map` utilizando mocking para a requisição HTTP em `tests/tools/crawl/test_map.py`.
    *   Implementar o método `map` para aceitar os parâmetros suportados, construir o payload e utilizar o `HTTPClient` para enviar a requisição POST para `/map`.
13. **Implementar `search`:** (Depende de `__init__` e parâmetros de scrape)
    *   Especificar casos de teste para o método `search`, considerando os parâmetros suportados no modo self-hosted.
    *   Criar testes unitários para `search` utilizando mocking para a requisição HTTP em `tests/tools/crawl/test_search.py`.
    *   Implementar o método `search` para aceitar os parâmetros suportados, construir o payload e utilizar o `HTTPClient` para enviar a requisição POST para `/search`.
14. **Atualizar Documentação:**
    *   Atualizar `README.md`, `DOC.md`, `TOOLS.md`, e `TODO.md` para refletir as mudanças e novas funcionalidades implementadas, incluindo as limitações do modo self-hosted.

## Diagrama do Fluxo

```mermaid
graph TD
    A[Iniciar Tarefa] --> B{Análise da Documentação e Restrições Self-Hosted};
    B --> C[Atualizar __init__ (HTTPClient, verify_ssl)];
    C --> D[Implementar get_crawl_status (TDD)];
    D --> E[Implementar cancel_crawl (TDD)];
    E --> F[Implementar get_crawl_errors (TDD)];
    F --> G[Implementar get_batch_scrape_status (TDD)];
    G --> H[Implementar get_batch_scrape_errors (TDD)];
    H --> I[Implementar get_extract_status (TDD)];
    I --> J[Implementar scrape (TDD, Parâmetros Suportados)];
    J --> K[Implementar batch_scrape (TDD, Parâmetros Suportados)];
    K --> L[Implementar crawl (TDD, Parâmetros Suportados)];
    L --> M[Implementar extract (TDD, Parâmetros Suportados)];
    M --> N[Implementar map (TDD, Parâmetros Suportados)];
    N --> O[Implementar search (TDD, Parâmetros Suportados)];
    O --> P[Atualizar Documentação (Incluindo Limitações)];
    P --> Q[Atualizar PLAN_UPDATE_FIRECRAWL_V1.md];
    Q --> R{Revisão do Plano com o Usuário};
    R -- Aprovar --> S[Implementação (Modo Código)];
    R -- Modificar --> B;
    S --> T[Fim];
