# Firecrawl API - Endpoint /crawl/status/{jobId}

## Descrição
Endpoint para verificar o status de um job de crawling. Retorna dados parciais durante a execução e dados completos ao finalizar.

## Método
`GET`

## URL
`https://api.firecrawl.dev/v0/crawl/status/{jobId}`

## Parâmetros

### Path Parameters
| Nome   | Tipo   | Obrigatório | Descrição          |
|--------|--------|-------------|--------------------|
| jobId  | string | Sim         | ID do job de crawl |

### Headers
| Chave          | Valor Exemplo        | Obrigatório | Descrição          |
|----------------|----------------------|-------------|--------------------|
| Authorization  | Bearer <token> | Sim         | Token de autenticação |

## Resposta

### Estrutura da Resposta (JSON)
```json
{
  "status": "string",
  "current": 123,
  "total": 123,
  "data": [
    {
      "markdown": "string",
      "content": "string",
      "html": "string",
      "rawHtml": "string",
      "index": 123,
      "metadata": {
        "title": "string",
        "description": "string",
        "language": "string",
        "sourceURL": "string",
        "pageStatusCode": 123,
        "pageError": "string"
      }
    }
  ],
  "partial_data": [...]
}
```

### Campos da Resposta
| Campo         | Tipo     | Descrição                                                                 |
|---------------|----------|---------------------------------------------------------------------------|
| status        | string   | Status do job (completed, active, failed, paused)                        |
| current       | integer  | Página atual sendo processada                                            |
| total         | integer  | Total de páginas a serem processadas                                     |
| data          | array    | Dados completos (disponíveis apenas quando status = completed)           |
| partial_data  | array    | Dados parciais durante processamento (máx. 50 itens)                     |

## Exemplos

### Requisição cURL
```bash
curl --request GET \
  --url https://api.firecrawl.dev/v0/crawl/status/12345 \
  --header 'Authorization: Bearer SEU_TOKEN'
```

### Resposta de Sucesso (200)
```json
{
  "status": "active",
  "current": 15,
  "total": 100,
  "partial_data": [
    {
      "markdown": "...",
      "content": "...",
      "html": "...",
      "index": 1,
      "metadata": {
        "title": "Página 1",
        "sourceURL": "https://exemplo.com/1",
        "pageStatusCode": 200
      }
    }
  ]
}
```

## Observações
- Dados parciais expiram após 24 horas
- Manter controle interno dos jobs é recomendado
- partial_data é uma feature alpha (sujeita a mudanças)