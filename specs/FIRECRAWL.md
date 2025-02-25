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