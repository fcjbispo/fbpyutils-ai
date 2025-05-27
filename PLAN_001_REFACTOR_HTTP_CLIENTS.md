# Plano de Refactoring: HTTPClient e RequestsManager

Este documento descreve o plano para refatorar as classes `HTTPClient` e `RequestsManager` no arquivo `fbpyutils_ai/tools/http.py`, alterando-as para retornar o objeto de resposta bruta em vez de um objeto JSON parseado. O refactoring manterá as implementações síncronas e assíncronas existentes, o suporte a streaming e incluirá a atualização do código cliente, testes unitários e documentação.

## Objetivos

*   Modificar `HTTPClient` e `RequestsManager` para retornar o objeto de resposta HTTP bruto.
*   Preservar a funcionalidade síncrona, assíncrona e de streaming.
*   Atualizar o código cliente que utiliza essas classes para lidar com o novo tipo de retorno.
*   Ajustar os testes unitários existentes para refletir as mudanças.
*   Atualizar a documentação para descrever a nova interface.

## Plano de Ação

1.  **Análise de Dependências:**
    *   Identificar todos os arquivos e funções que importam e utilizam as classes `HTTPClient` e `RequestsManager`.
    *   Analisar como as respostas são atualmente consumidas e parseadas nesses locais.

2.  **Refatorar `HTTPClient` (`fbpyutils_ai/tools/http.py`):**
    *   No método `async_request`, remover a lógica de parseamento de JSON quando `stream=False`. O método deve retornar o objeto `httpx.Response` diretamente.
    *   No método `sync_request`, remover a lógica de parseamento de JSON. O método deve retornar o objeto `httpx.Response` diretamente.
    *   Atualizar as docstrings dos métodos `async_request` e `sync_request` para indicar que o tipo de retorno é `httpx.Response` (ou `Union[httpx.Response, Generator]`).
    *   Atualizar os type hints para refletir o novo tipo de retorno.
    *   Analisar o parâmetro stream: bool em função de como ele é utilizado e se é necessário manter ou ajustar sua lógica.

3.  **Refatorar `RequestsManager` (`fbpyutils_ai/tools/http.py`):**
    *   No método `make_request` e `_execute_request_with_retry`, remover a lógica de parseamento de JSON quando `stream=False`. O método deve retornar o objeto `requests.Response` diretamente.
    *   Manter a lógica do gerador para respostas de streaming (`stream=True`), mas garantir que o gerador produza os dados brutos do stream, se necessário, ou que o parseamento de JSON seja movido para o código cliente que consome o gerador. (Nota: A implementação atual já retorna um gerador que parseia JSON, isso precisará ser ajustado para retornar o objeto de resposta ou um gerador de dados brutos, dependendo da necessidade do cliente).
    *   Atualizar as docstrings dos métodos `request`, `make_request` e `_execute_request_with_retry` para indicar o tipo de retorno correto (`requests.Response` ou `Generator`).
    *   Atualizar os type hints.
    *   Analisar o parâmetro stream: bool em função de como ele é utilizado e se é necessário manter ou ajustar sua lógica.

4.  **Atualizar Código Cliente:**
    *   Para cada uso de `HTTPClient` identificado na etapa 1:
        *   Modificar o código para receber o objeto `httpx.Response`.
        *   Adicionar a lógica para verificar o status da resposta (`response.raise_for_status()`) se ainda não estiver presente.
        *   Adicionar a lógica para parsear o corpo da resposta para JSON (`response.json()`) ou acessar o conteúdo (`response.content`, `response.text`) conforme necessário.
        *   Garantir que o tratamento de respostas de streaming (`response.aiter_bytes()`) funcione corretamente.
    *   Para cada uso de `RequestsManager` identificado na etapa 1:
        *   Modificar o código para receber o objeto `requests.Response` (para não-streaming) ou o gerador (para streaming).
        *   Adicionar a lógica para verificar o status da resposta (`response.raise_for_status()`) se ainda não estiver presente.
        *   Adicionar a lógica para parsear o corpo da resposta para JSON (`response.json()`) ou acessar o conteúdo (`response.content`, `response.text`) conforme necessário.
        *   Ajustar o consumo do gerador para respostas de streaming, movendo a lógica de parseamento de JSON para o código cliente, se aplicável.

5.  **Atualizar Testes Unitários (`tests/tools/http/`):**
    *   Revisar os testes existentes para `HTTPClient` e `RequestsManager`.
    *   Modificar os mocks e stubs para simular o retorno de objetos `httpx.Response` ou `requests.Response` brutos.
    *   Ajustar as asserções para verificar se o código cliente (dentro dos testes) lida corretamente com os objetos de resposta brutos e extrai os dados esperados.
    *   Garantir que os testes de streaming ainda funcionem corretamente.

6.  **Atualizar Documentação:**
    *   Localizar a documentação existente que descreve `HTTPClient` e `RequestsManager` (provavelmente em `DOC.md` ou arquivos relacionados).
    *   Atualizar as descrições das classes e métodos para refletir que eles agora retornam objetos de resposta brutos.
    *   Fornecer exemplos de código mostrando como os clientes devem consumir as respostas (verificar status, parsear JSON, lidar com streaming).

## Escopo

*   Refatorar as classes `HTTPClient` e `RequestsManager` em `fbpyutils_ai/tools/http.py`.
*   Atualizar todo o código cliente dentro do repositório `FBPyUtils-AI` que depende dessas classes.
*   Atualizar os testes unitários existentes em `tests/tools/http/`.
*   Atualizar a documentação relevante dentro do repositório `FBPyUtils-AI`.
*   Manter a cobertura de teste existente, focando em ajustar os testes atuais.
*   Preservar a funcionalidade síncrona, assíncrona e de streaming.

## Fora de Escopo

*   Aumentar a cobertura de teste para 90% neste momento.
*   Implementar novas funcionalidades nas classes `HTTPClient` ou `RequestsManager`.
*   Refatorar outras partes do código que não dependem diretamente de `HTTPClient` ou `RequestsManager`.

Este plano servirá como guia para a implementação do refactoring.

Siga sempre as instruções contidas em:
 - D:\Vibe\CONVENTIONS.md
 - D:\Vibe\MEMORY_BANK.md
 - D:\Vibe\Vibe.md
