# ESPECIFICAÇÕES DE FERRAMENTAS PARA AGENTES DE IA

## Ferramentas e suas Aplicações

### 1. Agente de Pesquisa na Internet
#### Ferramenta: **BeautifulSoup**
- **Descrição:** Extraí conteúdo de páginas web usando BeautifulSoup.
- **Especificação JSON:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "scrape_webpage",
      "description": "Extrai conteúdo de uma página web usando BeautifulSoup.",
      "parameters": {
        "type": "object",
        "properties": {
          "url": {
            "type": "string",
            "description": "URL da página web a ser scraped."
          }
        },
        "required": ["url"]
      },
      "response_model": {
        "type": "string",
        "description": "Texto extraído da página web."
      }
    }
  }
  ```
- **Exemplo de Uso em Python:**
  ```python
  import requests
  from bs4 import BeautifulSoup

  def scrape_webpage(url):
      response = requests.get(url)
      soup = BeautifulSoup(response.content, 'html.parser')
      return soup.get_text()

  # Exemplo de uso
  content = scrape_webpage("https://example.com")
  print(content)
```

### 2. Agente de Extração de Conteúdo Web
#### Ferramenta: **lxml**
- **Descrição:** Parseia HTML e extrai elementos específicos usando lxml.
- **Especificação JSON:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "parse_html_with_lxml",
      "description": "Parseia HTML usando lxml e extrai elementos específicos.",
      "parameters": {
        "type": "object",
        "properties": {
          "html_content": {
            "type": "string",
            "description": "Conteúdo HTML a ser parseado."
          },
          "xpath": {
            "type": "string",
            "description": "Expressão XPath para selecionar elementos."
          }
        },
        "required": ["html_content", "xpath"]
      },
      "response_model": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "Lista de strings representando os elementos extraídos."
      }
    }
  }
  ```
- **Exemplo de Uso em Python:**
  ```python
  from lxml import etree

  def parse_html_with_lxml(html_content, xpath):
      tree = etree.HTML(html_content)
      elements = tree.xpath(xpath)
      return [etree.tostring(el).decode('utf-8') for el in elements]

  # Exemplo de uso
  html = "<html><body><p>Texto</p></body></html>"
  elements = parse_html_with_lxml(html, "//p")
  print(elements)
```

### 3. Agente de Manipulação de Planilhas Excel
#### Ferramenta: **openpyxl**
- **Descrição:** Lê dados de uma planilha Excel usando openpyxl.
- **Especificação JSON:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "read_excel_with_openpyxl",
      "description": "Lê dados de uma planilha Excel usando openpyxl.",
      "parameters": {
        "type": "object",
        "properties": {
          "file_path": {
            "type": "string",
            "description": "Caminho para o arquivo Excel."
          },
          "sheet_name": {
            "type": "string",
            "description": "Nome da planilha a ser lida."
          }
        },
        "required": ["file_path", "sheet_name"]
      },
      "response_model": {
        "type": "array",
        "items": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "description": "Lista de linhas, onde cada linha é uma lista de valores."
      }
    }
  }
  ```
- **Exemplo de Uso em Python:**
  ```python
  from openpyxl import load_workbook

  def read_excel_with_openpyxl(file_path, sheet_name):
      wb = load_workbook(file_path)
      sheet = wb[sheet_name]
      data = []
      for row in sheet.iter_rows(values_only=True):
          data.append(row)
      return data

  # Exemplo de uso
  data = read_excel_with_openpyxl("exemplo.xlsx", "Sheet1")
  print(data)
```

## Ferramenta: **pandas**
- **Descrição:** Lê dados de uma planilha Excel usando pandas.
- **Especificação JSON:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "read_excel_with_pandas",
      "description": "Lê dados de uma planilha Excel usando pandas.",
      "parameters": {
        "type": "object",
        "properties": {
          "file_path": {
            "type": "string",
            "description": "Caminho para o arquivo Excel."
          },
          "sheet_name": {
            "type": "string",
            "description": "Nome da planilha a ser lida."
          }
        },
        "required": ["file_path", "sheet_name"]
      },
      "response_model": {
        "type": "array",
        "items": {
          "type": "object"
        },
        "description": "Lista de dicionários representando os registros da planilha."
      }
    }
  }
  ```
- **Exemplo de Uso em Python:**
  ```python
  import pandas as pd

  def read_excel_with_pandas(file_path, sheet_name):
      df = pd.read_excel(file_path, sheet_name=sheet_name)
      return df.to_dict(orient='records')

  # Exemplo de uso
  data = read_excel_with_pandas("exemplo.xlsx", "Sheet1")
  print(data)
```

## Ferramenta: **json**
- **Descrição:** Lê um arquivo JSON e retorna seu conteúdo.
- **Especificação JSON:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "read_json_file",
      "description": "Lê um arquivo JSON e retorna seu conteúdo.",
      "parameters": {
        "type": "object",
        "properties": {
          "file_path": {
            "type": "string",
            "description": "Caminho para o arquivo JSON."
          }
        },
        "required": ["file_path"]
      },
      "response_model": {
        "type": "object",
        "description": "Conteúdo do arquivo JSON parseado."
      }
    }
  }
  ```
- **Exemplo de Uso em Python:**
  ```python
  import json

  def read_json_file(file_path):
      with open(file_path, 'r') as file:
          data = json.load(file)
      return data

  # Exemplo de uso
  data = read_json_file("exemplo.json")
  print(data)
```

## Ferramenta: **csv**
- **Descrição:** Lê um arquivo CSV e retorna seu conteúdo.
- **Especificação JSON:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "read_csv_file",
      "description": "Lê um arquivo CSV e retorna seu conteúdo.",
      "parameters": {
        "type": "object",
        "properties": {
          "file_path": {
            "type": "string",
            "description": "Caminho para o arquivo CSV."
          }
        },
        "required": ["file_path"]
      },
      "response_model": {
        "type": "array",
        "items": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "description": "Lista de linhas, onde cada linha é uma lista de valores."
      }
    }
  }
  ```
- **Exemplo de Uso em Python:**
  ```python
  import csv

  def read_csv_file(file_path):
      with open(file_path, 'r') as file:
          reader = csv.reader(file)
          data = list(reader)
      return data

  # Exemplo de uso
  data = read_csv_file("exemplo.csv")
  print(data)
```

## Ferramenta: **OpenCV**
- **Descrição:** Analisa uma imagem usando OpenCV e retorna uma descrição básica.
- **Especificação JSON:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "describe_image_with_opencv",
      "description": "Analisa uma imagem usando OpenCV e retorna uma descrição.",
      "parameters": {
        "type": "object",
        "properties": {
          "image_path": {
            "type": "string",
            "description": "Caminho para o arquivo de imagem."
          }
        },
        "required": ["image_path"]
      },
      "response_model": {
        "type": "string",
        "description": "Descrição básica da imagem (e.g., 'Imagem colorida')."
      }
    }
  }
  ```
- **Exemplo de Uso em Python:**
  ```python
  import cv2

  def describe_image_with_opencv(image_path):
      image = cv2.imread(image_path)
      if len(image.shape) == 3:
          return "Imagem colorida"
      else:
          return "Imagem em preto e branco"

  # Exemplo de uso
  description = describe_image_with_opencv("exemplo.jpg")
  print(description)
```

## Ferramenta: **CLIP**
- **Descrição:** Usa o modelo CLIP para gerar uma descrição da imagem com base em rótulos fornecidos.
- **Especificação JSON:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "describe_image_with_clip",
      "description": "Usa o modelo CLIP para gerar uma descrição da imagem.",
      "parameters": {
        "type": "object",
        "properties": {
          "image_path": {
            "type": "string",
            "description": "Caminho para o arquivo de imagem."
          },
          "possible_labels": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "Lista de possíveis rótulos para a imagem."
          }
        },
        "required": ["image_path", "possible_labels"]
      },
      "response_model": {
        "type": "string",
        "description": "Rótulo mais provável para a imagem."
      }
    }
  }
  ```
- **Exemplo de Uso em Python:**
  ```python
  import clip
  import torch
  from PIL import Image

  def describe_image_with_clip(image_path, possible_labels):
      model, preprocess = clip.load("ViT-B/32")
      image = preprocess(Image.open(image_path)).unsqueeze(0)
      text = clip.tokenize(possible_labels)
      with torch.no_grad():
          logits_per_image, _ = model(image, text)
          probs = logits_per_image.softmax(dim=-1).cpu().numpy()
      return possible_labels[probs.argmax()]

  # Exemplo de uso
  labels = ["um cachorro", "um gato", "um carro"]
  description = describe_image_with_clip("exemplo.jpg", labels)
  print(description)
```

## Ferramenta: **DALL-E (via API)**
- **Descrição:** Gera uma imagem a partir de um prompt usando a API do DALL-E.
- **Especificação JSON:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "generate_image_with_dalle",
      "description": "Gera uma imagem a partir de um prompt usando a API DALL-E.",
      "parameters": {
        "type": "object",
        "properties": {
          "prompt": {
            "type": "string",
            "description": "Descrição textual da imagem a ser gerada."
          },
          "api_key": {
            "type": "string",
            "description": "Chave da API OpenAI."
          }
        },
        "required": ["prompt", "api_key"]
      },
      "response_model": {
        "type": "string",
        "description": "URL da imagem gerada."
      }
    }
  }
  ```
- **Exemplo de Uso em Python:**
  ```python
  import openai

  def generate_image_with_dalle(prompt, api_key):
      openai.api_key = api_key
      response = openai.Image.create(
          prompt=prompt,
          n=1,
          size="1024x1024"
      )
      image_url = response['data'][0]['url']
      return image_url

  # Exemplo de uso
  image_url = generate_image_with_dalle("Um gato tocando piano", "sua_chave_api")
  print(image_url)
```

## Ferramenta: **sqlite3**
- **Descrição:** Executa uma consulta SQL em um banco de dados SQLite.
- **Especificação JSON:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "query_sqlite_database",
      "description": "Executa uma consulta SQL em um banco de dados SQLite.",
      "parameters": {
        "type": "object",
        "properties": {
          "db_path": {
            "type": "string",
            "description": "Caminho para o arquivo do banco de dados SQLite."
          },
          "query": {
            "type": "string",
            "description": "Consulta SQL a ser executada."
          }
        },
        "required": ["db_path", "query"]
      },
      "response_model": {
        "type": "array",
        "items": {
          "type": "array"
        },
        "description": "Lista de tuplas representando os resultados da consulta."
      }
    }
  }
  ```
- **Exemplo de Uso em Python:**
  ```python
  import sqlite3

  def query_sqlite_database(db_path, query):
      conn = sqlite3.connect(db_path)
      cursor = conn.cursor()
      cursor.execute(query)
      results = cursor.fetchall()
      conn.close()
      return results

  # Exemplo de uso
  results = query_sqlite_database("exemplo.db", "SELECT * FROM tabela")
  print(results)
```

## Ferramenta: **SQLAlchemy**
- **Descrição:** Executa uma consulta SQL em um banco de dados usando SQLAlchemy.
- **Especificação JSON:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "query_database_with_sqlalchemy",
      "description": "Executa uma consulta SQL usando SQLAlchemy.",
      "parameters": {
        "type": "object",
        "properties": {
          "connection_string": {
            "type": "string",
            "description": "String de conexão com o banco de dados."
          },
          "query": {
            "type": "string",
            "description": "Consulta SQL a ser executada."
          }
        },
        "required": ["connection_string", "query"]
      },
      "response_model": {
        "type": "array",
        "items": {
          "type": "array"
        },
        "description": "Lista de tuplas representando os resultados da consulta."
      }
    }
  }
  ```
- **Exemplo de Uso em Python:**
  ```python
  from sqlalchemy import create_engine, text

  def query_database_with_sqlalchemy(connection_string, query):
      engine = create_engine(connection_string)
      with engine.connect() as connection:
          result = connection.execute(text(query))
          return result.fetchall()

  # Exemplo de uso
  results = query_database_with_sqlalchemy("sqlite:///exemplo.db", "SELECT * FROM tabela")
  print(results)
```

## Ferramenta: **requests**
- **Descrição:** Faz uma requisição HTTP usando a biblioteca requests.
- **Especificação JSON:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "make_http_request",
      "description": "Faz uma requisição HTTP usando a biblioteca requests.",
      "parameters": {
        "type": "object",
        "properties": {
          "url": {
            "type": "string",
            "description": "URL do endpoint."
          },
          "method": {
            "type": "string",
            "enum": ["GET", "POST", "PUT", "DELETE"],
            "description": "Método HTTP."
          },
          "headers": {
            "type": "object",
            "description": "Cabeçalhos da requisição."
          },
          "data": {
            "type": "object",
            "description": "Dados a serem enviados na requisição."
          }
        },
        "required": ["url", "method"]
      },
      "response_model": {
        "type": "object",
        "description": "Resposta JSON da requisição HTTP."
      }
    }
  }
  ```
- **Exemplo de Uso em Python:**
  ```python
  import requests

  def make_http_request(url, method, headers=None, data=None):
      response = requests.request(method, url, headers=headers, json=data)
      return response.json()

  # Exemplo de uso
  response = make_http_request("https://api.example.com/data", "GET")
  print(response)
```

## Ferramenta: **httpx**
- **Descrição:** Faz uma requisição HTTP usando a biblioteca httpx.
- **Especificação JSON:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "make_http_request_with_httpx",
      "description": "Faz uma requisição HTTP usando a biblioteca httpx.",
      "parameters": {
        "type": "object",
        "properties": {
          "url": {
            "type": "string",
            "description": "URL do endpoint."
          },
          "method": {
            "type": "string",
            "enum": ["GET", "POST", "PUT", "DELETE"],
            "description": "Método HTTP."
          },
          "headers": {
            "type": "object",
            "description": "Cabeçalhos da requisição."
          },
          "json": {
            "type": "object",
            "description": "Dados a serem enviados na requisição em formato JSON."
          }
        },
        "required": ["url", "method"]
      },
      "response_model": {
        "type": "object",
        "description": "Resposta JSON da requisição HTTP."
      }
    }
  }
  ```
- **Exemplo de Uso em Python:**
  ```python
  import httpx

  def make_http_request_with_httpx(url, method, headers=None, json=None):
      with httpx.Client() as client:
          response = client.request(method, url, headers=headers, json=json)
          return response.json()

  # Exemplo de uso
  response = make_http_request_with_httpx("https://api.example.com/data", "GET")
  print(response)