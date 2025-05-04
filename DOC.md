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
#### Tool: `FireCrawlTool` (using Firecrawl API v1)
- **Description:** Interacts with the Firecrawl API v1 for web scraping, crawling, extraction, mapping, and searching. It is designed to work with both the cloud service and a self-hosted instance, handling authentication, retries, and using the `HTTPClient` for requests. It also provides methods to format scrape results and scrape multiple URLs in parallel for MCP server compatibility.
- **Reference:** [Firecrawl API v1 Documentation](https://docs.firecrawl.dev/api-reference/introduction)

**Note on Self-Hosted Limitations:** When using a self-hosted Firecrawl instance without the `fire-engine`, certain advanced features are not supported. The `FireCrawlTool` is implemented to exclude parameters related to these unsupported functionalities (e.g., `mobile`, `actions`, `location`, advanced `proxy` options, `changeTrackingOptions` for scraping, `enableWebSearch` for extract). Refer to `specs/SELF_HOST_UNSUPPORTED_PARAMS.md` for details.

- **Python Initialization Example:**
  ```python
  from fbpyutils_ai.tools.crawl import FireCrawlTool

  # Reads FBPY_FIRECRAWL_BASE_URL (defaults to self-hosted v1) and FBPY_FIRECRAWL_API_KEY from env vars
  # verify_ssl can be set to False for self-signed certificates in self-hosted environments
  firecrawl_tool = FireCrawlTool(verify_ssl=False)
  ```

- **`scrape` Method:**
  - **Description:** Fetches and extracts content from a single URL using the Firecrawl v1 API (Self-Hosted compatible).
  - **Reference:** [Firecrawl API v1 Scrape Documentation](https://docs.firecrawl.dev/api-reference/endpoint/scrape)
  - **Parameters (Self-Hosted Compatible):**
    - `url` (str): The URL to scrape. (Required)
    - `formats` (list[str]): List of formats (e.g., "markdown", "html", "rawHtml", "screenshot", "links"). Default: `["markdown"]`.
    - `onlyMainContent` (bool): Extract only main content. Default: `False`.
    - `includeTags` (list[str] | None): CSS selectors to include.
    - `excludeTags` (list[str] | None): CSS selectors to exclude.
    - `headers` (dict | None): Custom request headers.
    - `waitFor` (int): Milliseconds to wait for dynamic content. Default: `0`.
    - `timeout` (int): Request timeout in milliseconds. Default: `30000`.
    - `jsonOptions` (dict | None): Options for LLM-based JSON extraction (schema, prompts).
    - `removeBase64Images` (bool): Remove base64 images. Default: `False`.
    - `blockAds` (bool): Block ads. Default: `False`.
    - `includeHtml` (bool): Include the full HTML content. Default: `False`.
    - `includeRawHtml` (bool): Include the raw HTML content. Default: `False`.
    - `replaceAllPathsWithAbsolutePaths` (bool): Replace relative paths with absolute paths. Default: `True`.
    - `mode` (str): Extraction mode. Default: `"markdown"`.
  - **Return (v1 Structure):**
    - `Dict[str, Any]`: A dictionary containing `success`, `data` (with requested formats and metadata), and `warning`.

- **`crawl` Method:**
  - **Description:** Initiates a crawl job starting from a given URL using the Firecrawl v1 API (Self-Hosted compatible).
  - **Reference:** [Firecrawl API v1 Crawl Documentation](https://docs.firecrawl.dev/api-reference/endpoint/crawl-post)
  - **Parameters (Self-Hosted Compatible):**
    - `url` (str): The starting URL for the crawl. (Required)
    - `includes` (list[str] | None): URL patterns to include.
    - `excludes` (list[str] | None): URL patterns to exclude.
    - `generateImgAltText` (bool): Generate alt text for images (requires paid plan). Default: `False`.
    - `returnOnlyUrls` (bool): Return only URLs. Default: `False`.
    - `maxDepth` (int): Maximum crawl depth. Default: `123`.
    - `mode` (str): Crawling mode (`default`, `fast`). Default: `"default"`.
    - `ignoreSitemap` (bool): Ignore sitemap. Default: `False`.
    - `limit` (int): Maximum pages to crawl. Default: `10000`.
    - `allowBackwardCrawling` (bool): Allow backward crawling. Default: `False`.
    - `allowExternalContentLinks` (bool): Allow external links. Default: `False`.
    - `formats` (list[str]): Formats for each scraped page. Default: `["markdown"]`.
    - `onlyMainContent` (bool): Extract main content for each page. Default: `False`.
    - `includeTags` (list[str] | None): CSS selectors to include for each page.
    - `excludeTags` (list[str] | None): CSS selectors to exclude for each page.
    - `headers` (dict | None): Custom headers for each page.
    - `waitFor` (int): Milliseconds to wait for dynamic content on each page. Default: `0`.
    - `timeout` (int): Request timeout for each page. Default: `30000`.
    - `jsonOptions` (dict | None): JSON extraction options for each page.
    - `removeBase64Images` (bool): Remove base64 images for each page. Default: `False`.
    - `blockAds` (bool): Block ads for each page. Default: `False`.
    - `includeHtml` (bool): Include HTML for each page. Default: `False`.
    - `includeRawHtml` (bool): Include raw HTML for each page. Default: `False`.
    - `replaceAllPathsWithAbsolutePaths` (bool): Replace relative paths for each page. Default: `True`.
  - **Return:**
    - `Dict[str, Any]`: A dictionary containing the `jobId` for the initiated crawl.

- **`get_crawl_status` Method:**
  - **Description:** Retrieves the status and data of an ongoing or completed crawl job.
  - **Reference:** [Firecrawl API v1 Get Crawl Status Documentation](https://docs.firecrawl.dev/api-reference/endpoint/crawl-get)
  - **Parameters:**
    - `job_id` (str): The ID of the crawl job. (Required)
  - **Return:**
    - `Dict[str, Any]`: A dictionary with the crawl status (`status`, `total`, `completed`, `data`, etc.).

- **`cancel_crawl` Method:**
  - **Description:** Cancels a running crawl job.
  - **Reference:** [Firecrawl API v1 Cancel Crawl Documentation](https://docs.firecrawl.dev/api-reference/endpoint/crawl-delete)
  - **Parameters:**
    - `job_id` (str): The ID of the crawl job. (Required)
  - **Return:**
    - `Dict[str, Any]`: A dictionary with the cancellation result (`status`).

- **`get_crawl_errors` Method:**
  - **Description:** Retrieves a list of errors and URLs blocked by robots.txt for a crawl job.
  - **Reference:** [Firecrawl API v1 Get Crawl Errors Documentation](https://docs.firecrawl.dev/api-reference/endpoint/crawl-get-errors)
  - **Parameters:**
    - `job_id` (str): The ID of the crawl job. (Required)
  - **Return:**
    - `Dict[str, Any]`: A dictionary with `errors` (list of error details) and `robotsBlocked` (list of URLs).

- **`batch_scrape` Method:**
  - **Description:** Initiates scraping for a list of URLs in a single job using the Firecrawl v1 API (Self-Hosted compatible).
  - **Reference:** [Firecrawl API v1 Batch Scrape Documentation](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape)
  - **Parameters (Self-Hosted Compatible):**
    - `urls` (list[str]): The list of URLs to scrape. (Required)
    - `webhook` (dict | None): Webhook configuration.
    - `ignoreInvalidURLs` (bool): If invalid URLs are specified, they will be ignored. Default: `False`.
    - `formats` (list[str]): List of formats (same as `scrape`). Default: `["markdown"]`.
    - `onlyMainContent` (bool): Extract only main content (same as `scrape`). Default: `False`.
    - `includeTags` (list[str] | None): CSS selectors to include (same as `scrape`).
    - `excludeTags` (list[str] | None): CSS selectors to exclude (same as `scrape`).
    - `headers` (dict | None): Custom request headers (same as `scrape`).
    - `waitFor` (int): Milliseconds to wait (same as `scrape`). Default: `0`.
    - `timeout` (int): Request timeout (same as `scrape`). Default: `30000`.
    - `jsonOptions` (dict | None): JSON extraction options (same as `scrape`).
    - `removeBase64Images` (bool): Remove base64 images (same as `scrape`). Default: `False`.
    - `blockAds` (bool): Block ads (same as `scrape`). Default: `False`.
    - `includeHtml` (bool): Include HTML (same as `scrape`). Default: `False`.
    - `includeRawHtml` (bool): Include raw HTML (same as `scrape`). Default: `False`.
    - `replaceAllPathsWithAbsolutePaths` (bool): Replace relative paths (same as `scrape`). Default: `True`.
    - `mode` (str): Extraction mode (same as `scrape`). Default: `"markdown"`.
  - **Return:**
    - `Dict[str, Any]`: A dictionary containing `success`, `id` (batch job ID), `url` (status URL), and `invalidURLs`.

- **`get_batch_scrape_status` Method:**
  - **Description:** Retrieves the status and data of an ongoing or completed batch scrape job.
  - **Reference:** [Firecrawl API v1 Get Batch Scrape Status Documentation](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get)
  - **Parameters:**
    - `job_id` (str): The ID of the batch scrape job. (Required)
  - **Return:**
    - `Dict[str, Any]`: A dictionary with the batch scrape status (`status`, `total`, `completed`, `data`, etc.).

- **`get_batch_scrape_errors` Method:**
  - **Description:** Retrieves a list of errors and URLs blocked by robots.txt for a batch scrape job.
  - **Reference:** [Firecrawl API v1 Get Batch Scrape Errors Documentation](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get-errors)
  - **Parameters:**
    - `job_id` (str): The ID of the batch scrape job. (Required)
  - **Return:**
    - `Dict[str, Any]`: A dictionary with `errors` (list of error details) and `robotsBlocked` (list of URLs).

- **`extract` Method:**
  - **Description:** Extracts structured data from URLs based on a prompt and/or schema using the Firecrawl v1 API (Self-Hosted compatible).
  - **Reference:** [Firecrawl API v1 Extract Documentation](https://docs.firecrawl.dev/api-reference/endpoint/extract)
  - **Parameters (Self-Hosted Compatible):**
    - `urls` (list[str]): The list of URLs to extract data from (glob format). (Required)
    - `prompt` (str | None): Prompt to guide extraction.
    - `schema` (dict | None): Schema for extracted data structure.
    - `ignoreSitemap` (bool): Ignore sitemap during scanning. Default: `False`.
    - `includeSubdomains` (bool): Include subdomains during scanning. Default: `True`.
    - `showSources` (bool): Include sources in response. Default: `False`.
    - `formats` (list[str]): Formats for scraping before extraction. Default: `["markdown"]`.
    - `onlyMainContent` (bool): Extract main content before extraction. Default: `False`.
    - `includeTags` (list[str] | None): CSS selectors to include before extraction.
    - `excludeTags` (list[str] | None): CSS selectors to exclude before extraction.
    - `headers` (dict | None): Custom headers before extraction.
    - `waitFor` (int): Milliseconds to wait before extraction. Default: `0`.
    - `timeout` (int): Request timeout before extraction. Default: `30000`.
    - `jsonOptions` (dict | None): JSON extraction options.
    - `removeBase64Images` (bool): Remove base64 images before extraction. Default: `False`.
    - `blockAds` (bool): Block ads before extraction. Default: `False`.
    - `includeHtml` (bool): Include HTML before extraction. Default: `False`.
    - `includeRawHtml` (bool): Include raw HTML before extraction. Default: `False`.
    - `replaceAllPathsWithAbsolutePaths` (bool): Replace relative paths before extraction. Default: `True`.
    - `mode` (str): Extraction mode before extraction. Default: `"markdown"`.
  - **Return:**
    - `Dict[str, Any]`: A dictionary containing `success` and `id` (extract job ID).

- **`get_extract_status` Method:**
  - **Description:** Retrieves the status and extracted data of an extract job.
  - **Reference:** [Firecrawl API v1 Get Extract Status Documentation](https://docs.firecrawl.dev/api-reference/endpoint/extract-get)
  - **Parameters:**
    - `job_id` (str): The ID of the extract job. (Required)
  - **Return:**
    - `Dict[str, Any]`: A dictionary with `success`, `data` (extracted data if completed), `status`, and `expiresAt`.

- **`map` Method:**
  - **Description:** Maps a website's links starting from a base URL using the Firecrawl v1 API (Self-Hosted compatible).
  - **Reference:** [Firecrawl API v1 Map Documentation](https://docs.firecrawl.dev/api-reference/endpoint/map)
  - **Parameters (Self-Hosted Compatible):**
    - `url` (str): The base URL to start mapping from. (Required)
    - `search` (str | None): Search query to filter links.
    - `ignoreSitemap` (bool): Ignore sitemap. Default: `True`.
    - `sitemapOnly` (bool): Only return sitemap links. Default: `False`.
    - `includeSubdomains` (bool): Include subdomains. Default: `False`.
    - `limit` (int): Maximum number of links. Default: `5000`.
    - `timeout` (int | None): Timeout in milliseconds.
  - **Return:**
    - `Dict[str, Any]`: A dictionary containing `success` and `links` (list of URLs).

- **`search` Method:**
  - **Description:** Performs a web search and optionally scrapes the results using the Firecrawl v1 API (Self-Hosted compatible).
  - **Reference:** [Firecrawl API v1 Search Documentation](https://docs.firecrawl.dev/api-reference/endpoint/search)
  - **Parameters (Self-Hosted Compatible):**
    - `query` (str): The search query. (Required)
    - `limit` (int): Maximum number of results. Default: `5`.
    - `tbs` (str | None): Time-based search parameter.
    - `lang` (str): Language code. Default: `"en"`.
    - `country` (str): Country code. Default: `"us"`.
    - `timeout` (int): Timeout in milliseconds. Default: `60000`.
    - `formats` (list[str]): Formats for scraping search results. Default: `["markdown"]`.
    - `onlyMainContent` (bool): Extract main content for search results. Default: `False`.
    - `includeTags` (list[str] | None): CSS selectors to include for search results.
    - `excludeTags` (list[str] | None): CSS selectors to exclude for search results.
    - `headers` (dict | None): Custom headers for search results.
    - `waitFor` (int): Milliseconds to wait for dynamic content for search results. Default: `0`.
    - `jsonOptions` (dict | None): JSON extraction options for search results.
    - `removeBase64Images` (bool): Remove base64 images for search results. Default: `False`.
    - `blockAds` (bool): Block ads for search results. Default: `False`.
    - `includeHtml` (bool): Include HTML for search results. Default: `False`.
    - `includeRawHtml` (bool): Include raw HTML for search results. Default: `False`.
    - `replaceAllPathsWithAbsolutePaths` (bool): Replace relative paths for search results. Default: `True`.
    - `mode` (str): Extraction mode for search results. Default: `"markdown"`.
  - **Return:**
    - `Dict[str, Any]`: A dictionary containing `success`, `data` (list of search results with optional scraped content), and `warning`.

- **`scrape_formatted` Method:**
  - **Description:** Scrapes a single webpage, extracts key information, and returns it as a formatted Markdown string. Mimics the behavior of the scrape tool in the MCP server.
  - **Parameters:**
    - `url` (str): The URL of the webpage to scrape. (Required)
    - `tags_to_remove` (list[str]): A list of HTML tags/selectors to remove (e.g., ['script', '.ad']). Defaults to `[]`.
    - `timeout` (int): Maximum time in milliseconds to wait for scraping. Defaults to `30000`.
    - `onlyMainContent` (bool): Extract only the main content. Defaults to `True`.
    - `mode` (str): Extraction mode. Defaults to `"markdown"`.
  - **Return:**
    - `str`: A Markdown string containing the formatted page content, metadata, and links, or an error message.

- **`scrape_multiple` Method:**
  - **Description:** Scrapes multiple webpages in parallel using threads, extracts key information, and returns a list of formatted Markdown strings. Uses `ThreadPoolExecutor` for synchronous parallel execution.
  - **Parameters:**
    - `urls` (list[str]): List of URLs to scrape. (Required)
    - `tags_to_remove` (list[str]): A list of HTML tags/selectors to remove for all URLs. Defaults to `[]`.
    - `timeout` (int): Maximum time in milliseconds to wait for each scrape. Defaults to `30000`.
    - `onlyMainContent` (bool): Extract only the main content for all URLs. Defaults to `True`.
    - `mode` (str): Extraction mode for all URLs. Defaults to `"markdown"`.
    - `max_workers` (int | None): Maximum number of threads to use. Defaults to `None` (Python's default).
  - **Return:**
    - `list[str]`: A list of Markdown strings (one per URL, in the original order) containing formatted content or error messages.

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
          result = connection.execute(text(query)).fetchall()
      return result

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
      "name": "make_http_request_with_requests",
      "description": "Makes an HTTP request using the requests library.",
      "parameters": {
        "type": "object",
        "properties": {
          "method": {
            "type": "string",
            "description": "HTTP method (GET, POST, PUT, DELETE)."
          },
          "url": {
            "type": "string",
            "description": "URL for the request."
          },
          "headers": {
            "type": "object",
            "description": "Request headers."
          },
          "params": {
            "type": "object",
            "description": "Query parameters."
          },
          "data": {
            "type": "object",
            "description": "Request body data."
          },
          "json": {
            "type": "object",
            "description": "Request body JSON."
          },
          "timeout": {
            "type": "number",
            "description": "Request timeout in seconds."
          }
        },
        "required": ["method", "url"]
      },
      "response_model": {
        "type": "object",
        "description": "Response object from the requests library."
      }
    }
  }
  ```
- **Python Usage Example:**
  ```python
  import requests

  def make_http_request_with_requests(method, url, headers=None, params=None, data=None, json=None, timeout=None):
      response = requests.request(method, url, headers=headers, params=params, data=data, json=json, timeout=timeout)
      return response

  # Example usage
  response = make_http_request_with_requests("GET", "https://api.example.com/data")
  print(response.json())
  ```

## Tool: **httpx**
- **Description:** Makes an HTTP request using the httpx library.
- **JSON Specification:**
  ```json
  {
    "type": "function",
    "function": "make_http_request_with_httpx",
    "description": "Makes an HTTP request using the httpx library.",
    "parameters": {
      "type": "object",
      "properties": {
        "method": {
          "type": "string",
          "description": "HTTP method (GET, POST, PUT, DELETE)."
        },
        "url": {
          "type": "string",
          "description": "URL for the request."
        },
        "headers": {
          "type": "object",
          "description": "Request headers."
        },
        "params": {
          "type": "object",
          "description": "Query parameters."
        },
        "data": {
          "type": "object",
          "description": "Request body data."
        },
        "json": {
          "type": "object",
          "description": "Request body JSON."
        },
        "timeout": {
          "type": "number",
          "description": "Request timeout in seconds."
        }
      },
      "required": ["method", "url"]
    },
    "response_model": {
      "type": "object",
      "description": "Response object from the httpx library."
    }
  }
  ```
- **Python Usage Example:**
  ```python
  import httpx

  def make_http_request_with_httpx(method, url, headers=None, params=None, data=None, json=None, timeout=None):
      response = httpx.request(method, url, headers=headers, params=params, data=data, json=json, timeout=timeout)
      return response

  # Example usage
  response = make_http_request_with_httpx("GET", "https://api.example.com/data")
  print(response.json())
