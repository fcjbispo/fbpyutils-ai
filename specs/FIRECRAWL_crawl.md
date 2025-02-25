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