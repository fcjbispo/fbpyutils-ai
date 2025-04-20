# FBPyUtils-AI: AI Tools in Python

## 1. Introduction
This project implements a Python library with AI utilities, focusing on tools for:
- Web search (using SearXNG)
- Web scraping
- HTTP requests

## 2. Main Features

### 2.1 Web Search
Implements a generic search tool and a specific tool for SearXNG.

The `SearchTool` class in `fbpyutils_ai/tools/search.py` provides an abstract interface for search tools. The `SearXNGTool` class implements this interface to perform searches using the SearXNG REST API.

To use the SearXNG search tool, initialize the `SearXNGTool` class with the base URL of your SearXNG service:

```python
from fbpyutils_ai.tools.search import SearXNGTool

searxng_tool = SearXNGTool(base_url="https://searxng.instance")
results = searxng_tool.search("OpenAI", categories=["general"])
print(results)
```

Search parameters can be passed to the `search` method. Refer to the SearXNG API documentation for the complete list of supported parameters.

### 2.2 Web Scraping
Extracts data and information from web pages using scraping techniques.

### 2.3 HTTP Requests
Provides tools to make HTTP requests to web services, supporting methods like POST, GET, PUT, and DELETE.

### 2.4 Firecrawl API Tool (`tools/crawl.py`)
The `FireCrawlTool` class provides a Python interface to interact with the [Firecrawl API](https://docs.firecrawl.dev/). It handles authentication, request retries, and session management. Key functionalities include:
- **Scraping (`scrape`)**: Fetches and extracts content from a single URL, with options for content extraction (Markdown, main content only), tag removal, and timeouts.
- **Crawling (`crawl`)**: Initiates a crawl job starting from a given URL, allowing configuration of depth, included/excluded paths, limits, and page processing options. Returns a `jobId`.
- **Crawl Status (`get_crawl_status`)**: Retrieves the status and data (if available) of an ongoing or completed crawl job using its `jobId`.
- **Cancel Crawl (`cancel_crawl`)**: Cancels a running crawl job using its `jobId`.
- **Search (`search`)**: Performs a search using the Firecrawl API's search endpoint (distinct from the SearXNG search tool).
This tool is used internally by the `mcp_scrape_server.py`.

### 2.4 Logging Configuration
The package utilizes Python's built-in `logging` module, configured in `fbpyutils_ai/__init__.py`. Key features include:
- **Rotating File Handler**: Logs are written to `~/.fbpyutils_ai/fbpyutils_ai.log` with automatic rotation (max size 256KB, 5 backup files).
- **Multiprocessing Support**: Uses `QueueHandler` and `QueueListener` to safely handle logs from multiple processes.
- **Configurable Log Level**: The log level can be set using the `FBPY_LOG_LEVEL` environment variable (defaults to `INFO`). Supported levels are `DEBUG`, `INFO`, `WARNING`, `ERROR`.

## 3. Usage

### 3.1 Environment Setup
To install the dependencies, run:
```bash
uv pip install .
```

This command installs the required libraries listed in `pyproject.toml`.


### 2.5 Web Scraping Server (`mcp_scrape_server.py`)
Provides an MCP (Model Context Protocol) server tool for scraping web pages.
- Uses `FireCrawlTool` internally to fetch and process web content.
- Offers `scrape` (single URL) and `scrape_n` (multiple URLs, parallel) functions.
- Returns page content, metadata, and links formatted in Markdown.
- Supports removing specific HTML tags and setting timeouts.
- Can stream results for multiple URLs (`scrape_n` with `stream=True`).

### 2.6 Web Search Server (`mcp_search_server.py`)
Provides an MCP server tool for performing web searches using SearXNG.
- Uses `SearXNGTool` internally to interact with a SearXNG instance.
- Leverages `duckdb` and `pandas` to process, sort, and filter results based on category templates.
- Supports various search categories (`general`, `images`, `videos`, `music`, `map`).
- Allows specifying language, maximum results, sorting criteria, and safesearch options.
- Can return results formatted as Markdown (default) or as a raw list of dictionaries.

### 2.7 MCP Server Entrypoint (`mcp_servers.py`)
This script initializes the `FastMCP` server named `fbpyutils_ai_tools`. It uses the `@mcp.tool()` decorator to expose the search and scrape functionalities defined in the other server modules (`mcp_search_server.py`, `mcp_scrape_server.py`) as callable tools for MCP clients. This is the main script to run to start the MCP server (e.g., `python -m fbpyutils_ai.servers.mcp_servers`).

### 2.8 Document Conversion Tool (`tools/document.py`)
The `DoclingConverter` class provides a wrapper around the `docling` command-line tool for document conversion.
- **Supported Formats**: Converts between various formats like PDF, DOCX, PPTX, HTML, Markdown, JSON, text, etc. (See `SUPPORTED_INPUT_FORMATS` and `SUPPORTED_OUTPUT_FORMATS`).
- **OCR**: Includes options to enable OCR (`--ocr`) using different engines (`--ocr-engine`).
- **PDF Preprocessing**: Offers a `force_image` option to convert PDF pages to images before processing, potentially improving OCR on complex PDFs. This uses `pdf2image` and `Pillow`.
- **Configuration**: Allows setting various `docling` parameters like PDF backend, table mode, image export mode, etc.
- **Error Handling**: Validates inputs and handles potential errors during the conversion process.
- **Requires `docling`**: The `docling` CLI tool must be installed and accessible in the system's PATH for this converter to work.
### 2.9 Vector Database and Embedding Tools (`tools/embedding.py`)
This module provides tools for managing and searching vector embeddings, crucial for semantic search and retrieval-augmented generation (RAG).
- **Vector Database Abstraction (`VectorDatabase`)**: Defines a common interface for vector database operations (add, search, count, etc.).
- **Implementations**:
    - `ChromaDB`: Interface for ChromaDB (persistent local or client/server).
    - `PgVectorDB`: Interface for PostgreSQL with the `pgvector` extension. Handles connection, table/index creation (HNSW), and operations.
    - `PineconeDB`: Interface for the Pinecone managed vector database. Handles index creation and operations.
- **Embedding Manager (`EmbeddingManager`)**: Orchestrates the process of generating embeddings for text documents (using an `LLMService` instance) and storing/searching them in a configured `VectorDatabase`. It handles document processing, ID generation, and batching.
### 2.10 HTTP Request Tools (`tools/http.py`)
This module offers utilities for making HTTP requests.
- **`HTTPClient`**: An asynchronous and synchronous HTTP client built on `httpx`.
    - Supports GET, POST, PUT, DELETE methods.
    - Handles base URLs, default headers, and SSL verification.
    - Provides `async_request` and `sync_request` methods.
    - Supports response streaming (returns the `httpx.Response` object directly when `stream=True`).
    - Includes context managers (`__enter__`, `__exit__`, `__aenter__`, `__aexit__`) for proper client lifecycle management.
- **`RequestsManager`**: A synchronous HTTP request utility built on `requests` and `tenacity`.
    - Primarily designed for interacting with APIs requiring retries (e.g., LLM APIs).
    - Supports GET, POST, PUT, DELETE methods.
    - Implements automatic retry logic with exponential backoff using `tenacity`.
    - Handles session creation with authentication (basic auth, bearer token) and SSL verification.
    - Supports streaming responses for POST requests (returns a generator).
    - Provides static methods `create_session`, `request` (convenience method), and `make_request`.
### 2.11 OpenAI Compatible LLM Tool (`tools/llm.py`)
The `LiteLLMServiceTool` class implements the `LLMService` interface to interact with OpenAI-compatible APIs (including Anthropic via specific headers).
- **Core Functionalities**:
    - `generate_embedding`: Creates vector embeddings for text using a specified embedding model.
    - `generate_text`: Generates text completions based on a prompt (legacy completions endpoint).
    - `generate_completions`: Generates chat completions based on a list of messages (chat completions endpoint).
    - `generate_tokens`: Tokenizes text using `tiktoken`, compatible with OpenAI models.
    - `describe_image`: Generates a description for an image (provided as path, URL, or base64) using a vision-compatible model.
    - `list_models`: Lists available models from the configured API endpoint.
    - `get_model_details`: Retrieves detailed information about a specific model.
- **Configuration**: Allows specifying different models, API keys, and base URLs for text generation, embeddings, and vision tasks. Reads API keys and base URLs from environment variables (`FBPY_OPENAI_API_KEY`, `FBPY_OPENAI_API_BASE`) if not provided directly.
- **Dependencies**: Uses `RequestsManager` for HTTP requests and `tiktoken` for tokenization.
### 2.12 SearXNG Search Tool (`tools/search.py`)
This module provides tools specifically for interacting with a SearXNG instance.
- **`SearXNGUtils`**: Contains static utility methods for processing SearXNG results:
    - `simplify_results`: Extracts key fields ('url', 'title', 'content', etc.) from raw results.
    - `convert_to_dataframe`: Converts a list of results into a pandas DataFrame.
- **`SearXNGTool`**: A client class for making search requests to a SearXNG API.
    - Supports synchronous (`search`) and asynchronous (`async_search`) requests using `HTTPClient`.
    - Handles configuration of base URL and API key (via arguments or environment variables `FBPY_SEARXNG_BASE_URL`, `FBPY_SEARXNG_API_KEY`).
    - Allows specifying search parameters like categories, language, time range, and safesearch level.
    - Validates input parameters.
    - This tool is used internally by the `mcp_search_server.py`.
### 2.13 Abstract Base Classes (`tools/__init__.py`)
This file defines abstract base classes (ABCs) that serve as interfaces for core functionalities:
- **`VectorDatabase`**: Defines the standard methods (`add_embeddings`, `search_embeddings`, `count`, `get_version`, `list_collections`, `reset_collection`) expected from any vector database implementation within this package (e.g., `ChromaDB`, `PgVectorDB`, `PineconeDB`).
- **`LLMService`**: Defines the standard methods (`generate_embedding`, `generate_text`, `generate_completions`, `generate_tokens`, `describe_image`, `list_models`, `get_model_details`) expected from any LLM service implementation (e.g., `LiteLLMServiceTool`).
These interfaces ensure consistency and allow for easier integration and swapping of different database or LLM providers.

### 3.2 Usage Examples

#### 3.2.1 Web Search
```python
from fbpyutils_ai.tools.search import SearXNGTool

searxng_tool = SearXNGTool() # Uses default base URL or env variable
results = searxng_tool.search("OpenAI", categories=["general"])
print(results)
```

## 4. Full Documentation
For detailed information on each feature and integration, refer to the documentation files:
- [AGENTS.md](AGENTS.md)
- [TOOLS.md](TOOLS.md)

## 5. Contribution
Feel free to contribute to the project! If you have questions or suggestions, please reach out through the repository or our support channels.

## 6. License
This project is licensed under the MIT License. For the full text of the license, see [the official MIT License](https://opensource.org/licenses/MIT).
---

## MIT License Disclaimer

Copyright (c) 2025 Francisco C J Bispo

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.**
