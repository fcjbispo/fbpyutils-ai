# Parâmetros Não Suportados na Versão Self-Hosted (Sem Fire-engine)

Este documento lista os parâmetros da API do Firecrawl que ativam funcionalidades que dependem do motor `fire-engine` e, portanto, não são totalmente suportados na versão self-hosted básica. Ao utilizar uma instância self-hosted sem o `fire-engine`, evite incluir estes parâmetros nas suas requisições para garantir a compatibilidade com os motores de raspagem disponíveis (`fetch`, `playwright`, `pdf`, `docx`).

## Endpoint: `/v1/scrape` (POST)

Parâmetros dentro do objeto `scrapeOptions` que não são totalmente suportados:

*   `actions`: Ativa a execução de ações no navegador (cliques, digitação, etc.).
*   `mobile`: Solicita a emulação de um dispositivo móvel.
*   `skipTlsVerification`: Desativa a verificação de certificados TLS/SSL.
*   `location`: Permite especificar a localização geográfica para a raspagem.
*   `proxy`: O uso deste parâmetro na requisição pode tentar ativar funcionalidades de proxy avançadas (`stealthProxy`). É mais seguro configurar proxy apenas via variáveis de ambiente (`PROXY_SERVER`, `PROXY_USERNAME`, `PROXY_PASSWORD`).
*   `screenshot` e `fullScreen`: Solicitam a captura de tela da página.

## Endpoint: `/v0/scrape` (POST)

Parâmetros dentro do objeto `pageOptions` que não são totalmente suportados:

*   `mobile`: Solicita a emulação de um dispositivo móvel.
*   `skipTlsVerification`: Desativa a verificação de certificados TLS/SSL.
*   `proxy`: O uso deste parâmetro na requisição pode tentar ativar funcionalidades de proxy avançadas (`stealthProxy`). É mais seguro configurar proxy apenas via variáveis de ambiente.
*   `actions`: Ativa a execução de ações no navegador.
*   `location`: Permite especificar a localização geográfica para a raspagem.
*   `screenshot` e `fullScreen`: Solicitam a captura de tela da página.

## Endpoint: `/v0/crawl` (POST)

Parâmetros dentro do objeto `pageOptions` que não são totalmente suportados (aplicam-se a cada página raspada durante o crawling):

*   `mobile`: Solicita a emulação de um dispositivo móvel.
*   `skipTlsVerification`: Desativa a verificação de certificados TLS/SSL.
*   `proxy`: O uso deste parâmetro na requisição pode tentar ativar funcionalidades de proxy avançadas (`stealthProxy`). É mais seguro configurar proxy apenas via variáveis de ambiente.
*   `actions`: Ativa a execução de ações no navegador.
*   `location`: Permite especificar a localização geográfica para a raspagem.
*   `screenshot` e `fullScreen`: Solicitam a captura de tela da página.

Parâmetros dentro do objeto `crawlerOptions` geralmente controlam a lógica de navegação e não dependem diretamente do `fire-engine`.

## Endpoint: `/v0/crawlWebsitePreview` (POST)

Parâmetros dentro do objeto `pageOptions` que não são totalmente suportados (aplicam-se a cada página raspada durante o preview):

*   `mobile`: Solicita a emulação de um dispositivo móvel.
*   `skipTlsVerification`: Desativa a verificação de certificados TLS/SSL.
*   `proxy`: O uso deste parâmetro na requisição pode tentar ativar funcionalidades de proxy avançadas (`stealthProxy`). É mais seguro configurar proxy apenas via variáveis de ambiente.
*   `actions`: Ativa a execução de ações no navegador.
*   `location`: Permite especificar a localização geográfica para a raspagem.
*   `screenshot` e `fullScreen`: Solicitam a captura de tela da página.

Parâmetros dentro do objeto `crawlerOptions` geralmente controlam a lógica de navegação e não dependem diretamente do `fire-engine`.

## Endpoint: `/v0/search` (POST)

Este endpoint realiza uma busca e, opcionalmente, raspa o conteúdo dos resultados. Os parâmetros não suportados são aqueles que afetam a etapa de raspagem, contidos no objeto `pageOptions`:

Parâmetros dentro do objeto `pageOptions` que não são totalmente suportados:

*   `mobile`: Solicita a emulação de um dispositivo móvel.
*   `skipTlsVerification`: Desativa a verificação de certificados TLS/SSL.
*   `proxy`: O uso deste parâmetro na requisição pode tentar ativar funcionalidades de proxy avançadas (`stealthProxy`). É mais seguro configurar proxy apenas via variáveis de ambiente.
*   `actions`: Ativa a execução de ações no navegador.
*   `location`: Permite especificar a localização geográfica para a raspagem.
*   `screenshot` e `fullScreen`: Solicitam a captura de tela da página.
