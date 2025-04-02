# AI AGENT TOOL SPECIFICATIONS

## Tools and their Applications

### 1. Internet Search Agent
#### Tool: `SearXNGTool`

- **Description:** Performs internet searches using the SearXNG REST API. The `SearXNGTool` class implements the abstract `SearchTool` class to provide a flexible and configurable search tool.

- **Usage:** To use this tool, initialize `SearXNGTool` with the base URL of the SearXNG service. The `search` method allows performing searches with specific API parameters.

- **Python Initialization Example:**
  ```python
  from fbpyutils_ai.tools.search import SearXNGTool

  searxng_tool = SearXNGTool(base_url="https://searxng.instance")
  ```

- **Python Search Example:**
  ```python
  results = searxng_tool.search("OpenAI", params={"category_general": "1"})
  print(results)
  ```

- **`search` Method Parameters:**
  - `query` (str): Search term.
  - `params` (Optional[Dict]): Dictionary of additional parameters for the SearXNG API. Consult the SearXNG API documentation for details on supported parameters.

- **`search` Method Return:**
  - `List[Dict]`: List of search results, where each result is a dictionary containing the information returned by the SearXNG API.

---

### 2. Web Content Extraction Agent
#### Tool: **lxml**
- **Description:** Parses HTML and extracts specific elements using lxml.
- **JSON Specification:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "parse_html_with_lxml",
      "description": "Parses HTML using lxml and extracts specific elements.",
      "parameters": {
        "type": "object",
        "properties": {
          "html_content": {
            "type": "string",
            "description": "HTML content to be parsed."
          },
          "xpath": {
            "type": "string",
            "description": "XPath expression to select elements."
          }
        },
        "required": ["html_content", "xpath"]
      },
      "response_model": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "List of strings representing the extracted elements."
      }
    }
  }
  ```
- **Python Usage Example:**
  ```python
  from lxml import etree

  def parse_html_with_lxml(html_content, xpath):
      tree = etree.HTML(html_content)
      elements = tree.xpath(xpath)
      return [etree.tostring(el).decode('utf-8') for el in elements]

  # Example usage
  html = "<html><body><p>Text</p></body></html>"
  elements = parse_html_with_lxml(html, "//p")
  print(elements)
  ```

### 3. Excel Spreadsheet Manipulation Agent
#### Tool: **openpyxl**
- **Description:** Reads data from an Excel spreadsheet using openpyxl.
- **JSON Specification:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "read_excel_with_openpyxl",
      "description": "Reads data from an Excel spreadsheet using openpyxl.",
      "parameters": {
        "type": "object",
        "properties": {
          "file_path": {
            "type": "string",
            "description": "Path to the Excel file."
          },
          "sheet_name": {
            "type": "string",
            "description": "Name of the sheet to be read."
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
        "description": "List of rows, where each row is a list of values."
      }
    }
  }
  ```
- **Python Usage Example:**
  ```python
  from openpyxl import load_workbook

  def read_excel_with_openpyxl(file_path, sheet_name):
      wb = load_workbook(file_path)
      sheet = wb[sheet_name]
      data = []
      for row in sheet.iter_rows(values_only=True):
          data.append(row)
      return data

  # Example usage
  data = read_excel_with_openpyxl("example.xlsx", "Sheet1")
  print(data)
  ```

## Tool: **pandas**
- **Description:** Reads data from an Excel spreadsheet using pandas.
- **JSON Specification:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "read_excel_with_pandas",
      "description": "Reads data from an Excel spreadsheet using pandas.",
      "parameters": {
        "type": "object",
        "properties": {
          "file_path": {
            "type": "string",
            "description": "Path to the Excel file."
          },
          "sheet_name": {
            "type": "string",
            "description": "Name of the sheet to be read."
          }
        },
        "required": ["file_path", "sheet_name"]
      },
      "response_model": {
        "type": "array",
        "items": {
          "type": "object"
        },
        "description": "List of dictionaries representing the spreadsheet records."
      }
    }
  }
  ```
- **Python Usage Example:**
  ```python
  import pandas as pd

  def read_excel_with_pandas(file_path, sheet_name):
      df = pd.read_excel(file_path, sheet_name=sheet_name)
      return df.to_dict(orient='records')

  # Example usage
  data = read_excel_with_pandas("example.xlsx", "Sheet1")
  print(data)
  ```

## Tool: **json**
- **Description:** Reads a JSON file and returns its content.
- **JSON Specification:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "read_json_file",
      "description": "Reads a JSON file and returns its content.",
      "parameters": {
        "type": "object",
        "properties": {
          "file_path": {
            "type": "string",
            "description": "Path to the JSON file."
          }
        },
        "required": ["file_path"]
      },
      "response_model": {
        "type": "object",
        "description": "Parsed content of the JSON file."
      }
    }
  }
  ```
- **Python Usage Example:**
  ```python
  import json

  def read_json_file(file_path):
      with open(file_path, 'r') as file:
          data = json.load(file)
      return data

  # Example usage
  data = read_json_file("example.json")
  print(data)
  ```

## Tool: **csv**
- **Description:** Reads a CSV file and returns its content.
- **JSON Specification:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "read_csv_file",
      "description": "Reads a CSV file and returns its content.",
      "parameters": {
        "type": "object",
        "properties": {
          "file_path": {
            "type": "string",
            "description": "Path to the CSV file."
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
        "description": "List of rows, where each row is a list of values."
      }
    }
  }
  ```
- **Python Usage Example:**
  ```python
  import csv

  def read_csv_file(file_path):
      with open(file_path, 'r') as file:
          reader = csv.reader(file)
          data = list(reader)
      return data

  # Example usage
  data = read_csv_file("example.csv")
  print(data)
  ```

## Tool: **OpenCV**
- **Description:** Analyzes an image using OpenCV and returns a basic description.
- **JSON Specification:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "describe_image_with_opencv",
      "description": "Analyzes an image using OpenCV and returns a description.",
      "parameters": {
        "type": "object",
        "properties": {
          "image_path": {
            "type": "string",
            "description": "Path to the image file."
          }
        },
        "required": ["image_path"]
      },
      "response_model": {
        "type": "string",
        "description": "Basic description of the image (e.g., 'Color image')."
      }
    }
  }
  ```
- **Python Usage Example:**
  ```python
  import cv2

  def describe_image_with_opencv(image_path):
      image = cv2.imread(image_path)
      if len(image.shape) == 3:
          return "Color image"
      else:
          return "Black and white image"

  # Example usage
  description = describe_image_with_opencv("example.jpg")
  print(description)
  ```

## Tool: **CLIP**
- **Description:** Uses the CLIP model to generate an image description based on provided labels.
- **JSON Specification:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "describe_image_with_clip",
      "description": "Uses the CLIP model to generate an image description.",
      "parameters": {
        "type": "object",
        "properties": {
          "image_path": {
            "type": "string",
            "description": "Path to the image file."
          },
          "possible_labels": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "List of possible labels for the image."
          }
        },
        "required": ["image_path", "possible_labels"]
      },
      "response_model": {
        "type": "string",
        "description": "Most likely label for the image."
      }
    }
  }
  ```
- **Python Usage Example:**
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

  # Example usage
  labels = ["a dog", "a cat", "a car"]
  description = describe_image_with_clip("example.jpg", labels)
  print(description)
  ```

## Tool: **DALL-E (via API)**
- **Description:** Generates an image from a prompt using the DALL-E API.
- **JSON Specification:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "generate_image_with_dalle",
      "description": "Generates an image from a prompt using the DALL-E API.",
      "parameters": {
        "type": "object",
        "properties": {
          "prompt": {
            "type": "string",
            "description": "Textual description of the image to be generated."
          },
          "api_key": {
            "type": "string",
            "description": "OpenAI API key."
          }
        },
        "required": ["prompt", "api_key"]
      },
      "response_model": {
        "type": "string",
        "description": "URL of the generated image."
      }
    }
  }
  ```
- **Python Usage Example:**
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

  # Example usage
  image_url = generate_image_with_dalle("A cat playing piano", "your_api_key")
  print(image_url)
  ```

## Tool: **sqlite3**
- **Description:** Executes an SQL query on an SQLite database.
- **JSON Specification:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "query_sqlite_database",
      "description": "Executes an SQL query on an SQLite database.",
      "parameters": {
        "type": "object",
        "properties": {
          "db_path": {
            "type": "string",
            "description": "Path to the SQLite database file."
          },
          "query": {
            "type": "string",
            "description": "SQL query to be executed."
          }
        },
        "required": ["db_path", "query"]
      },
      "response_model": {
        "type": "array",
        "items": {
          "type": "array"
        },
        "description": "List of tuples representing the query results."
      }
    }
  }
  ```
- **Python Usage Example:**
  ```python
  import sqlite3

  def query_sqlite_database(db_path, query):
      conn = sqlite3.connect(db_path)
      cursor = conn.cursor()
      cursor.execute(query)
      results = cursor.fetchall()
      conn.close()
      return results

  # Example usage
  results = query_sqlite_database("example.db", "SELECT * FROM table")
  print(results)
  ```

## Tool: **SQLAlchemy**
- **Description:** Executes an SQL query on a database using SQLAlchemy.
- **JSON Specification:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "query_database_with_sqlalchemy",
      "description": "Executes an SQL query using SQLAlchemy.",
      "parameters": {
        "type": "object",
        "properties": {
          "connection_string": {
            "type": "string",
            "description": "Database connection string."
          },
          "query": {
            "type": "string",
            "description": "SQL query to be executed."
          }
        },
        "required": ["connection_string", "query"]
      },
      "response_model": {
        "type": "array",
        "items": {
          "type": "array"
        },
        "description": "List of tuples representing the query results."
      }
    }
  }
  ```
- **Python Usage Example:**
  ```python
  from sqlalchemy import create_engine, text

  def query_database_with_sqlalchemy(connection_string, query):
      engine = create_engine(connection_string)
      with engine.connect() as connection:
          result = connection.execute(text(query))
          return result.fetchall()

  # Example usage
  results = query_database_with_sqlalchemy("sqlite:///example.db", "SELECT * FROM table")
  print(results)
  ```

## Tool: **requests**
- **Description:** Makes an HTTP request using the requests library.
- **JSON Specification:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "make_http_request",
      "description": "Makes an HTTP request using the requests library.",
      "parameters": {
        "type": "object",
        "properties": {
          "url": {
            "type": "string",
            "description": "Endpoint URL."
          },
          "method": {
            "type": "string",
            "enum": ["GET", "POST", "PUT", "DELETE"],
            "description": "HTTP method."
          },
          "headers": {
            "type": "object",
            "description": "Request headers."
          },
          "data": {
            "type": "object",
            "description": "Data to be sent in the request."
          }
        },
        "required": ["url", "method"]
      },
      "response_model": {
        "type": "object",
        "description": "JSON response from the HTTP request."
      }
    }
  }
  ```
- **Python Usage Example:**
  ```python
  import requests

  def make_http_request(url, method, headers=None, data=None):
      response = requests.request(method, url, headers=headers, json=data)
      return response.json()

  # Example usage
  response = make_http_request("https://api.example.com/data", "GET")
  print(response)
  ```

## Tool: **httpx**
- **Description:** Makes an HTTP request using the httpx library.
- **JSON Specification:**
  ```json
  {
    "type": "function",
    "function": {
      "name": "make_http_request_with_httpx",
      "description": "Makes an HTTP request using the httpx library.",
      "parameters": {
        "type": "object",
        "properties": {
          "url": {
            "type": "string",
            "description": "Endpoint URL."
          },
          "method": {
            "type": "string",
            "enum": ["GET", "POST", "PUT", "DELETE"],
            "description": "HTTP method."
          },
          "headers": {
            "type": "object",
            "description": "Request headers."
          },
          "json": {
            "type": "object",
            "description": "Data to be sent in the request in JSON format."
          }
        },
        "required": ["url", "method"]
      },
      "response_model": {
        "type": "object",
        "description": "JSON response from the HTTP request."
      }
    }
  }
  ```
- **Python Usage Example:**
  ```python
  import httpx

  def make_http_request_with_httpx(url, method, headers=None, json=None):
      with httpx.Client() as client:
          response = client.request(method, url, headers=headers, json=json)
          return response.json()

  # Example usage
  response = make_http_request_with_httpx("https://api.example.com/data", "GET")
  print(response)
