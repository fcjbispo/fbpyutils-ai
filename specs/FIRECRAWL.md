## Endpoint: `/scrape`

## Descrição

O endpoint `/scrape` permite scrapear uma URL específica e retorna informações extraídas da página, como conteúdo em markdown, conteúdo HTML, e dados metadata.

## Autorização

Para utilizar este endpoint, é necessário incluir um token de autenticação Bearer no header da requisição.

- **Header:** `Authorization: Bearer <token>`
- **Tipo:** string
- **Obrigatório:** Sim
- **Descrição:** Token de autenticação Bearer. Substitua `<token>` pelo seu token de autenticação Firecrawl.

## Parâmetros

| Parâmetro | Descrição | Valor padrão | Exemplo | Tipo | Obrigatório |
|---|---|---|---|---|---|
| `url` | URL a ser scrapada | - | `"https://example.com"` | string | Sim |
| `pageOptions` | Opções de página | - | `{}` | objeto | Não |
| `pageOptions.headers` | Cabeçalhos HTTP para a requisição da página | `{}` |  `{"User-Agent": "Roo-Agent"}` | objeto | Não |
| `pageOptions.includeHtml` | Incluir conteúdo HTML da página | `false` | `true` | boolean | Não |
| `pageOptions.includeRawHtml` | Incluir conteúdo HTML bruto da página | `false` | `true` | boolean | Não |
| `pageOptions.onlyIncludeTags` | Incluir apenas determinados tags, classes e ids | `[]` | `["script", ".ad", "#footer"]` | string[] | Não |
| `pageOptions.onlyMainContent` | Retornar apenas o conteúdo principal da página | `false` | `true` | boolean | Não |
| `pageOptions.removeTags` | Remover determinados tags, classes e ids | `[]` | `["script", ".ad", "#footer"]` | string[] | Não |
| `pageOptions.replaceAllPathsWithAbsolutePaths` | Substituir todos os caminhos relativos por caminhos absolutos | `false` | `true` | boolean | Não |
| `pageOptions.screenshot` | Incluir uma captura de tela da parte superior da página | `false` | `true` | boolean | Não |
| `pageOptions.fullPageScreenshot` | Incluir uma captura de tela de toda a página | `false` | `true` | boolean | Não |
| `pageOptions.waitFor` | Esperar um tempo específico para a página carregar | `0` | `5000` (5 segundos) | integer | Não |
| `extractorOptions` | Opções para extração de informações | - | `{}` | objeto | Não |
| `extractorOptions.mode` | Modo de extração | `"markdown"` | `"llm-extraction"` | enum<string> | Não |
| `extractorOptions.extractionPrompt` | Prompt para extração de informações com LLM | - | `"Extraia todos os produtos da página"` | string | Não (Obrigatório para `llm-extraction` mode) |
| `extractorOptions.extractionSchema` | Schema para dados a serem extraídos com LLM | - |  `{"type": "array", "items": {"type": "string"}}` | objeto | Não (Obrigatório para `llm-extraction` mode) |
| `timeout` | Tempo de espera para a requisição em milissecos | `30000` | `60000` (60 segundos) | integer | Não |

## Exemplos de Chamada

### Exemplo 1: Scrape uma página e extrair o conteúdo em markdown.

**Requisição:**

```bash
curl --request POST \
  --url https://api.firecrawl.dev/v0/scrape \
  --header 'Authorization: Bearer SEU_TOKEN_AQUI' \
  --header 'Content-Type: application/json' \
  --data '{
    "url": "https://example.com"
  }'
```

**Resposta (200 OK):**

```json
{
  "success": true,
  "data": {
    "markdown": "Conteúdo em Markdown da página example.com...",
    "content": "Conteúdo em texto simples da página example.com...",
    "html": null,
    "rawHtml": null,
    "metadata": {
      "title": "Example Domain",
      "description": "This domain is for use in illustrative examples in documents.",
      "language": null,
      "sourceURL": "https://example.com",
      "pageStatusCode": 200,
      "pageError": null
    },
    "llm_extraction": null,
    "warning": null
  }
}
```

### Exemplo 2: Scrape uma página, incluir HTML e remover tags `script` e `.ad`.

**Requisição:**

```bash
curl --request POST \
  --url https://api.firecrawl.dev/v0/scrape \
  --header 'Authorization: Bearer SEU_TOKEN_AQUI' \
  --header 'Content-Type: application/json' \
  --data '{
    "url": "https://example.com",
    "pageOptions": {
      "includeHtml": true,
      "removeTags": ["script", ".ad"]
    }
  }'
```

**Resposta (200 OK):**

```json
{
  "success": true,
  "data": {
    "markdown": "Conteúdo em Markdown da página example.com...",
    "content": "Conteúdo em texto simples da página example.com...",
    "html": "<!DOCTYPE html><html>...</html>",
    "rawHtml": null,
    "metadata": {
      "title": "Example Domain",
      "description": "This domain is for use in illustrative examples in documents.",
      "language": null,
      "sourceURL": "https://example.com",
      "pageStatusCode": 200,
      "pageError": null
    },
    "llm_extraction": null,
    "warning": null
  }
}
```

### Exemplo 3: Scrape uma página e extrair título e descrição usando LLM.

**Requisição:**

```bash
curl --request POST \
  --url https://api.firecrawl.dev/v0/scrape \
  --header 'Authorization: Bearer SEU_TOKEN_AQUI' \
  --header 'Content-Type: application/json' \
  --data '{
    "url": "https://example.com",
    "extractorOptions": {
      "mode": "llm-extraction",
      "extractionPrompt": "Extraia o título e a descrição da página.",
      "extractionSchema": {
        "type": "object",
        "properties": {
          "title": { "type": "string" },
          "description": { "type": "string" }
        },
        "required": ["title", "description"]
      }
    }
  }'
```

**Resposta (200 OK):**

```json
{
  "success": true,
  "data": {
    "markdown": "Conteúdo em Markdown da página example.com...",
    "content": "Conteúdo em texto simples da página example.com...",
    "html": null,
    "rawHtml": null,
    "metadata": {
      "title": "Example Domain",
      "description": "This domain is for use in illustrative examples in documents.",
      "language": null,
      "sourceURL": "https://example.com",
      "pageStatusCode": 200,
      "pageError": null
    },
    "llm_extraction": {
      "title": "Example Domain",
      "description": "This domain is for use in illustrative examples in documents."
    },
    "warning": null
  }
}
```
## Endpoint: `/crawl`

## Descrição

O endpoint `/crawl` permite iniciar um processo de crawling (rastreamento) em uma URL base, explorando links e extraindo informações de múltiplas páginas. Retorna um `jobId` que pode ser usado para acompanhar o status do crawling.

## Autorização

Assim como o endpoint `/scrape`, o endpoint `/crawl` também requer um token de autenticação Bearer no header da requisição.

- **Header:** `Authorization: Bearer <token>`
- **Tipo:** string
- **Obrigatório:** Sim
- **Descrição:** Token de autenticação Bearer. Substitua `<token>` pelo seu token de autenticação Firecrawl.

## Parâmetros

| Parâmetro | Descrição | Valor padrão | Exemplo | Tipo | Obrigatório |
|---|---|---|---|---|---|
| `url` | URL base para iniciar o crawling | - | `"https://example.com"` | string | Sim |
| `crawlerOptions` | Opções de configuração do crawler | - | `{}` | objeto | Não |
| `crawlerOptions.includes` | Padrões de URL a serem incluídos no crawling | `[]` | `["/blog", "/artigos"]` | string[] | Não |
| `crawlerOptions.excludes` | Padrões de URL a serem excluídos do crawling | `[]` | `["/admin", "/privado"]` | string[] | Não |
| `crawlerOptions.generateImgAltText` | Gerar texto alternativo para imagens usando LLMs (requer plano pago) | `false` | `true` | boolean | Não |
| `crawlerOptions.returnOnlyUrls` | Retornar apenas URLs encontradas, sem conteúdo | `false` | `true` | boolean | Não |
| `crawlerOptions.maxDepth` | Profundidade máxima de crawling a partir da URL base | `123` | `3` | integer | Não |
| `crawlerOptions.mode` | Modo de crawling: `default` ou `fast` (mais rápido, menos preciso) | `"default"` | `"fast"` | enum<string> | Não |
| `crawlerOptions.ignoreSitemap` | Ignorar o sitemap do website | `false` | `true` | boolean | Não |
| `crawlerOptions.limit` | Número máximo de páginas a serem crawled | `10000` | `5000` | integer | Não |
| `crawlerOptions.allowBackwardCrawling` | Permitir crawling para páginas previamente linkadas | `false` | `true` | boolean | Não |
| `crawlerOptions.allowExternalContentLinks` | Permitir seguir links para websites externos | `false` | `true` | boolean | Não |
| `pageOptions` | Opções de página para cada página crawled | - | `{}` | objeto | Não |
| `pageOptions.headers` | Cabeçalhos HTTP para as requisições de página | `{}` |  `{"User-Agent": "Crawler-Agent"}` | objeto | Não |
| `pageOptions.includeHtml` | Incluir conteúdo HTML das páginas crawled | `false` | `true` | boolean | Não |
| `pageOptions.includeRawHtml` | Incluir HTML bruto das páginas crawled | `false` | `true` | boolean | Não |
| `pageOptions.onlyIncludeTags` | Incluir apenas tags, classes e ids específicos | `[]` | `["article", ".post-content"]` | string[] | Não |
| `pageOptions.onlyMainContent` | Retornar apenas o conteúdo principal das páginas | `false` | `true` | boolean | Não |
| `pageOptions.removeTags` | Remover tags, classes e ids específicos das páginas | `[]` | `["aside", "#sidebar"]` | string[] | Não |
| `pageOptions.replaceAllPathsWithAbsolutePaths` | Substituir paths relativos por absolutos nas páginas | `false` | `true` | boolean | Não |
| `pageOptions.screenshot` | Incluir screenshot do topo de cada página crawled | `false` | `true` | boolean | Não |
| `pageOptions.fullPageScreenshot` | Incluir screenshot da página inteira de cada página crawled | `false` | `true` | boolean | Não |
| `pageOptions.waitFor` | Tempo para aguardar carregamento de cada página crawled | `0` | `2000` (2 segundos) | integer | Não |

## Exemplos de Chamada

### Exemplo 1: Iniciar um crawling básico na URL base.

**Requisição:**

```bash
curl --request POST \
  --url https://api.firecrawl.dev/v0/crawl \
  --header 'Authorization: Bearer SEU_TOKEN_AQUI' \
  --header 'Content-Type: application/json' \
  --data '{
    "url": "https://example.com"
  }'
```

**Resposta (200 OK):**

```json
{
  "jobId": "id-do-job-de-crawling"
}
```

### Exemplo 2: Crawling com `crawlerOptions` para incluir apenas URLs com `/blog` e limitar a profundidade.

**Requisição:**

```bash
curl --request POST \
  --url https://api.firecrawl.dev/v0/crawl \
  --header 'Authorization: Bearer SEU_TOKEN_AQUI' \
  --header 'Content-Type: application/json' \
  --data '{
    "url": "https://example.com",
    "crawlerOptions": {
      "includes": ["/blog"],
      "maxDepth": 2
    }
  }'
```

**Resposta (200 OK):**

```json
{
  "jobId": "id-de-outro-job-de-crawling"
}
```

### Exemplo 3: Crawling com `pageOptions` para incluir HTML e remover tags `nav`.

**Requisição:**

```bash
curl --request POST \
  --url https://api.firecrawl.dev/v0/crawl \
  --header 'Authorization: Bearer SEU_TOKEN_AQUI' \
  --header 'Content-Type: application/json' \
  --data '{
    "url": "https://example.com",
    "pageOptions": {
      "includeHtml": true,
      "removeTags": ["nav"]
    }
  }'
```

**Resposta (200 OK):**

```json
{
  "jobId": "id-de-mais-um-job-de-crawling"
}
```

### Exemplo 4: Crawling rápido, ignorando sitemap e permitindo links externos.

**Requisição:**

```bash
curl --request POST \
  --url https://api.firecrawl.dev/v0/crawl \
  --header 'Authorization: Bearer SEU_TOKEN_AQUI' \
  --header 'Content-Type: application/json' \
  --data '{
    "url": "https://example.com",
    "crawlerOptions": {
      "mode": "fast",
      "ignoreSitemap": true,
      "allowExternalContentLinks": true
    }
  }'
```

**Resposta (200 OK):**

```json
{
  "jobId": "id-de-job-rapido-de-crawling"
}
```

### Códigos de Resposta HTTP

- `200`: Sucesso. A requisição foi processada e o jobId do crawling foi retornado.
- `402`: Pagamento Necessário. Indica que a cota de uso do serviço foi excedida ou que é necessário realizar um pagamento para continuar utilizando o serviço.
- `429`: Muitas Requisições. Indica que o limite de requisições foi atingido. É necessário aguardar um tempo antes de realizar novas requisições.
- `500`: Erro Interno do Servidor. Indica um erro interno no servidor do Firecrawl ao processar a requisição.