## Plano Atualizado para Centralizar a Lógica de Retry HTTP

**Objetivo:** Garantir que todas as operações de nova tentativa (retry) em requisições HTTP sejam tratadas exclusivamente pelas classes [`RequestsManager`](fbpyutils_ai/tools/http.py:258) e [`HTTPClient`](fbpyutils_ai/tools/http.py:35) no arquivo [`fbpyutils_ai/tools/http.py`](fbpyutils_ai/tools/http.py:1), utilizando a biblioteca `tenacity` de forma padronizada.

**Fases do Plano:**

1.  **Fase 1: Análise e Identificação nos Clientes**
    *   Para cada um dos seguintes arquivos:
        *   [`fbpyutils_ai/tools/scrape.py`](fbpyutils_ai/tools/scrape.py:1)
        *   [`fbpyutils_ai/tools/document.py`](fbpyutils_ai/tools/document.py:1)
        *   [`fbpyutils_ai/tools/embedding.py`](fbpyutils_ai/tools/embedding.py:1)
        *   [`fbpyutils_ai/tools/search.py`](fbpyutils_ai/tools/search.py:1)
        *   [`fbpyutils_ai/tools/utils.py`](fbpyutils_ai/tools/utils.py:1)
    *   **Passos da Análise:**
        1.  **Identificar Lógica de Retry Local:**
            *   Buscar por usos diretos da anotação `@retry` de `tenacity` ou outras bibliotecas de retry.
            *   Identificar loops com blocos `try-except` que simulam comportamento de retry para chamadas HTTP.
            *   Verificar configurações de adaptadores HTTP com `max_retries` (ex: `requests.adapters.HTTPAdapter`) fora das classes centrais.
            *   Analisar qualquer outra implementação manual de lógica de nova tentativa.
        2.  **Documentar Descobertas:** Registrar os trechos de código onde a lógica de retry customizada foi encontrada.
:start_line:21
-------
    *   **Status:** Concluída.
    *   **Descobertas:** Lógica de retry customizada identificada em [`fbpyutils_ai/tools/llm/__init__.py`](fbpyutils_ai/tools/llm/__init__.py):
        *   Uso do decorator `@retry` de `tenacity` no método `_make_request`.
        *   Loop manual de retry no método `get_model_details` para introspecção.

2.  **Fase 2: Verificação e Padronização das Classes Centrais ([`HTTPClient`](fbpyutils_ai/tools/http.py:35) e [`RequestsManager`](fbpyutils_ai/tools/http.py:258))**
    *   Analisar as classes [`HTTPClient`](fbpyutils_ai/tools/http.py:35) e [`RequestsManager`](fbpyutils_ai/tools/http.py:258) em [`fbpyutils_ai/tools/http.py`](fbpyutils_ai/tools/http.py:1).
    *   **Passos da Verificação e Padronização:**
        1.  **[`RequestsManager`](fbpyutils_ai/tools/http.py:258):**
            *   Confirmar que o uso existente de `tenacity` (decorator [`@retry`](fbpyutils_ai/tools/http.py:401) em [`_execute_request_with_retry`](fbpyutils_ai/tools/http.py:402)) e `HTTPAdapter` em [`create_session`](fbpyutils_ai/tools/http.py:278) é adequado.
            *   Avaliar se os parâmetros de retry (ex: `wait`, `stop`, `retry_on_exception`) são configuráveis e se atendem às necessidades gerais. Se não, propor a adição de parâmetros ao método [`make_request`](fbpyutils_ai/tools/http.py:350) ou [`create_session`](fbpyutils_ai/tools/http.py:278) para permitir essa configuração pelos clientes.
        2.  **[`HTTPClient`](fbpyutils_ai/tools/http.py:35):**
            *   Verificar como `httpx` (usado por [`HTTPClient`](fbpyutils_ai/tools/http.py:35)) lida com retries nativamente.
            *   Se `httpx` não fornecer uma solução de retry robusta e configurável via `tenacity`, propor a adição da anotação `@retry` de `tenacity` aos métodos [`sync_request`](fbpyutils_ai/tools/http.py:173) e [`async_request`](fbpyutils_ai/tools/http.py:88).
            *   Garantir que os parâmetros de retry (ex: `wait`, `stop`, `retry_on_exception`) sejam configuráveis, possivelmente através de novos parâmetros nos métodos de requisição ou na inicialização da classe.
    *   **Status:** Concluída.
    *   **Resultados da Análise:**
        *   **RequestsManager:** Utiliza `HTTPAdapter` para retries de conexão e `@retry` de `tenacity` para retries baseados em exceções. O `max_retries` do `HTTPAdapter` é configurável, mas os parâmetros do decorator `@retry` (`wait`, `stop`) não são configuráveis pelos métodos de requisição.
        *   **HTTPClient:** Utiliza `httpx`, que não possui retry nativo robusto. Atualmente, não há lógica de retry explícita implementada nos métodos `sync_request` e `async_request`.
    *   **Propostas de Padronização/Melhoria:**
        *   **RequestsManager:** Tornar os parâmetros do decorator `@retry` em `_execute_request_with_retry` configuráveis através dos métodos `make_request` e `request`. Isso pode envolver refatorar a aplicação do retry para ser dinâmica ou passar os parâmetros para a lógica interna.
        *   **HTTPClient:** Adicionar o decorator `@retry` de `tenacity` aos métodos `sync_request` e `async_request`. Tornar os parâmetros de retry configuráveis, preferencialmente adicionando-os como parâmetros aos próprios métodos de requisição para permitir configuração por chamada.

3.  **Fase 3: Proposta de Refatoração dos Clientes**
    *   Com base nas Fases 1 e 2:
        1.  Para cada cliente com lógica de retry local (incluindo o cliente LLM em [`fbpyutils_ai/tools/llm/__init__.py`](fbpyutils_ai/tools/llm/__init__.py)), detalhar como essa lógica será removida.
        2.  As chamadas existentes aos métodos de [`HTTPClient`](fbpyutils_ai/tools/http.py:35) ou [`RequestsManager`](fbpyutils_ai/tools/http.py:258) pelos clientes **não devem ter suas assinaturas alteradas**. A configuração do comportamento de retry (se necessária além do padrão) será feita através dos parâmetros adicionados nas classes centrais (conforme Fase 2).
        3.  Garantir que toda a responsabilidade de retry seja delegada às classes centrais.
    *   **Status:** Concluída.

4.  **Fase 4: Análise de Impacto e Ajuste dos Testes Unitários**
    *   **Passos:**
        1.  Identificar todos os testes unitários existentes para os arquivos clientes modificados e para as classes [`HTTPClient`](fbpyutils_ai/tools/http.py:35) e [`RequestsManager`](fbpyutils_ai/tools/http.py:258).
        2.  Analisar como a remoção da lógica de retry dos clientes e a centralização/padronização nas classes HTTP podem afetar esses testes.
        3.  Propor ajustes nos testes para:
            *   Remover mocks ou asserções relacionadas à lógica de retry antiga nos clientes.
            *   Adicionar/modificar testes para as classes [`HTTPClient`](fbpyutils_ai/tools/http.py:35) e [`RequestsManager`](fbpyutils_ai/tools/http.py:258) para cobrir a funcionalidade de retry configurável (se novos parâmetros foram adicionados).
            *   Garantir que os testes dos clientes ainda cubram os cenários de sucesso e falha das chamadas HTTP, agora confiando no comportamento de retry das classes centrais.
    *   **Status:** Concluída.

5.  **Fase 5: Implementação e Refatoração**
    *   **Status:** Concluída.
    *   **Passos:**
        1.  Implementar as melhorias propostas na Fase 2 para as classes [`HTTPClient`](fbpyutils_ai/tools/http.py:35) e [`RequestsManager`](fbpyutils_ai/tools/http.py:258) em [`fbpyutils_ai/tools/http.py`](fbpyutils_ai/tools/http.py:1), tornando os parâmetros de retry configuráveis.
        2.  Refatorar os arquivos clientes identificados na Fase 1 (especificamente [`fbpyutils_ai/tools/llm/__init__.py`](fbpyutils_ai/tools/llm/__init__.py)) para remover a lógica de retry local, conforme detalhado na Fase 3.
        3.  Garantir que os clientes utilizem as classes centrais (`RequestsManager`/`HTTPClient`) para todas as requisições HTTP e dependam exclusivamente da lógica de retry centralizada.
        4.  Implementar os ajustes nos testes unitários conforme proposto na Fase 4, que incluem:
            *   Adicionar novos testes em [`tests/tools/http/test_http.py`](tests/tools/http/test_http.py) para cobrir a funcionalidade de retry do [`HTTPClient`](fbpyutils_ai/tools/http.py:35) com `tenacity`.
            *   Modificar os testes existentes em [`tests/tools/http/test_http_requests_manager.py`](tests/tools/http/test_http_requests_manager.py) para verificar a configuração dos parâmetros de retry configuráveis na classe [`RequestsManager`](fbpyutils_ai/tools/http.py:258).
            *   Criar um novo arquivo de teste (ex: `tests/tools/llm/test_llm.py`) para o módulo LLM ([`fbpyutils_ai/tools/llm/__init__.py`](fbpyutils_ai/tools/llm/__init__.py)) para garantir que a lógica de retry local foi removida e que ele depende corretamente das classes HTTP centrais.
        5.  Executar os testes unitários para garantir que as alterações não introduziram regressões e que a lógica de retry centralizada está funcionando corretamente.

**Diagrama Conceitual do Fluxo de Decisão (Revisado):**

::: mermaid
graph TD
    A[Analisar Arquivo Cliente] --> B{Possui lógica de retry própria?};
    B -- Sim --> C[Planejar Remoção do Retry Local];
    B -- Não --> D[Nenhuma ação de retry no cliente];
    C --> E{Retry da Classe Central HTTPClient/RequestsManager é adequado e configurável via tenacity?};
    E -- Sim --> F[Cliente Utiliza Classe Central com Retry Configurado];
    E -- Não --> G[Padronizar/Melhorar Retry na Classe Central com tenacity e parâmetros configuráveis];
    G --> F;
    F --> H[Analisar/Ajustar Testes Unitários do Cliente e Classes Centrais];
    D --> H_NoRetry[Analisar Testes Unitários do Cliente - sem foco em retry removido];
    H --> I[Atualizar plano de execução para indicar o progresso da execução];
    subgraph Legenda
        direction LR
        L1[Processo]
        L2{Decisão}
    end
:::

**Próximos Passos (Após Conclusão da Fase 4):**

1.  Solicitar a mudança para o modo "Code" para implementar as alterações da Fase 5.
