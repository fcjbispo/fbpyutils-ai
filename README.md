# FBPyUtils-AI: AI Tools in Python (Version 0.1.2)

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

### 2.4 Firecrawl API Tool (`tools/scrape.py`)
The `FireCrawlTool` class provides a Python interface to interact with the [Firecrawl API v1](https://docs.firecrawl.dev/api-reference/introduction). It is designed to work with both the cloud service and a self-hosted instance. It handles authentication, request retries, and uses the `HTTPClient` for making requests.

**Note on Self-Hosted Limitations:** When using a self-hosted Firecrawl instance without the `fire-engine`, certain advanced features are not supported. The `FireCrawlTool` is implemented to exclude parameters related to these unsupported features (e.g., `mobile`, `actions`, `location`, advanced `proxy` options, `changeTrackingOptions` for scraping, `enableWebSearch` for extract). Refer to `specs/SELF_HOST_UNSUPPORTED_PARAMS.md` for details.

Key functionalities implemented for API v1:

- **Scraping (`scrape`)**: Fetches and extracts content from a single URL. Supports various options like specifying output formats (`formats`), extracting only main content (`onlyMainContent`), including/excluding tags (`includeTags`, `excludeTags`), setting timeouts (`timeout`), handling dynamic content (`waitFor`), JSON extraction (`jsonOptions`), removing base64 images (`removeBase64Images`), and blocking ads (`blockAds`).
- **Search (`search`)**: Performs a web search and optionally scrapes the results. Supports specifying the search query, limit, time-based search (`tbs`), language (`lang`), country (`country`), timeout, and supported scrape options for the results.


### 2.5 Logging Configuration
The package utilizes Python's built-in `logging` module, configured in `fbpyutils_ai/__init__.py`. Key features include:
- **Rotating File Handler**: Logs are written to `~/.fbpyutils_ai/fbpyutils_ai.log` with automatic rotation (max size 256KB, 5 backup files).
- **Multiprocessing Support**: Uses `QueueHandler` and `QueueListener` to safely handle logs from multiple processes.
- **Configurable Log Level**: The log level can be set using the `FBPY_LOG_LEVEL` environment variable (defaults to `INFO`). Supported levels are `DEBUG`, `INFO`, `WARNING`, `ERROR`.

### 2.6 Marimo UI for AI Tools (`ui/marimo`)
This directory contains the Marimo-based user interface for demonstrating the AI tools.
- **`app_main.py`**: The main Marimo application that integrates and displays all individual tool modules using `mo.accordion`.
- **`app_llm_tool.py`**: Marimo module for the LLM (Large Language Model) tool, providing an interface for text generation, embeddings, and image description. It now includes dedicated sub-sections for "Generate Text" and "Generate Embeddings" within the LLM tool.
- **`app_search_tool.py`**: Marimo module for the SearXNG search tool, allowing interactive web searches.
- **`app_firecrawl_tool.py`**: Marimo module for the Firecrawl tool, exposing web scraping and search functionalities.
- **`components.py`**: Contains reusable Marimo UI components and helper functions.
- **`styles.css`**: Custom CSS for styling the Marimo applications.

### 2.7 Marimo UI Home Page
The Marimo UI now includes a dedicated "Home" page that provides an overview of the FBPyUtils-AI project and its integrated tools. This page serves as a central hub, offering a brief description of each available tool (LLM, Search, Scrape) and direct links to their respective sections within the application for easy navigation. The LLM tool now features "Generate Text" and "Generate Embeddings" functionalities.

## 3. Usage

### 3.1 Environment Setup
To install the dependencies, run:
```bash
uv pip install .
```

This command installs the required libraries listed in `pyproject.toml`.

To run the Marimo UI, navigate to the `fbpyutils_ai/ui/marimo` directory and execute:
```bash
marimo edit app_main.py
```


### 3.5 Document Conversion Tool (`tools/document.py`)
The `DoclingConverter` class provides a wrapper around the `docling` command-line tool for document conversion.
- **Supported Formats**: Converts between various formats like PDF, DOCX, PPTX, HTML, Markdown, JSON, text, etc. (See `SUPPORTED_INPUT_FORMATS` and `SUPPORTED_OUTPUT_FORMATS`).
- **OCR**: Includes options to enable OCR (`--ocr`) using different engines (`--ocr-engine`).
- **PDF Preprocessing**: Offers a `force_image` option to convert PDF pages to images before processing, potentially improving OCR on complex PDFs. This uses `pdf2image` and `Pillow`.
- **Configuration**: Allows setting various `docling` parameters like PDF backend, table mode, image export mode, etc.
- **Error Handling**: Validates inputs and handles potential errors during the conversion process.
- **Requires `docling`**: The `docling` CLI tool must be installed and accessible in the system's PATH for this converter to work.

### 3.6 Vector Database and Embedding Tools (`tools/embedding.py`)
This module provides tools for managing and searching vector embeddings, crucial for semantic search and retrieval-augmented generation (RAG).
- **Vector Database Abstraction (`VectorDatabase`)**: Defines a common interface for vector database operations (add, search, count, etc.).
- **Implementations**:
    - `ChromaDB`: Interface for ChromaDB (persistent local or client/server).
    - `PgVectorDB`: Interface for PostgreSQL with the `pgvector` extension. Handles connection, table/index creation (HNSW), and operations.
    - `PineconeDB`: Interface for the Pinecone managed vector database. Handles index creation and operations.
- **Embedding Manager (`EmbeddingManager`)**: Orchestrates the process of generating embeddings for text documents (using an `LLMService` instance) and storing/searching them in a configured `VectorDatabase`. It handles document processing, ID generation, and batching.

### 3.7 HTTP Request Tools (`tools/http.py`)
This module offers utilities for making HTTP requests, focusing on GET and POST methods.
- **`HTTPClient`**: An asynchronous and synchronous HTTP client built on `httpx`.
    - Supports GET and POST methods.
    - Handles base URLs, default headers, and SSL verification.
    - Automatically handles Gzip compressed responses.
    - Parses JSON responses with fallback for invalid JSON, returning a dictionary with error details.
    - Provides `async_request` and `sync_request` methods.
    - Supports response streaming (returns the `httpx.Response` object directly when `stream=True`).
    - Includes context managers (`__enter__`, `__exit__`, `__aenter__`, `__aexit__`) for proper client lifecycle management.
- **`RequestsManager`**: A synchronous HTTP request utility built on `requests` and `tenacity`.
    - Primarily designed for interacting with APIs requiring retries (e.g., LLM APIs).
    - Supports GET and POST methods.
    - Automatically handles Gzip compressed responses (via `requests` built-in handling).
    - Parses JSON responses with fallback for invalid JSON, returning a dictionary with error details.
    - Implements automatic retry logic with exponential backoff using `tenacity`.
    - Handles session creation with authentication (basic auth, bearer token) and SSL verification.
    - Supports streaming responses for POST requests (returns a generator).
    - Provides static methods `create_session`, `request` (convenience method), and `make_request`.

### 3.8 OpenAI Compatible LLM Tool (`tools/llm.py`)
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

### 3.9 SearXNG Search Tool (`tools/search.py`)
This module provides tools specifically for interacting with a SearXNG instance.
- **`SearXNGUtils`**: Contains static utility methods for processing SearXNG results:
    - `simplify_results`: Extracts key fields ('url', 'title', 'content', etc.) from raw results.
    - `convert_to_dataframe`: Converts a list of results into a pandas DataFrame.
- **`SearXNGTool`**: A client class for making search requests to a SearXNG API.
    - Supports synchronous (`search`) and asynchronous (`async_search`) requests using `HTTPClient`.
    - Handles configuration of base URL and API key (via arguments or environment variables `FBPY_SEARXNG_BASE_URL`, `FBPY_SEARXNG_API_KEY`).
    - Allows specifying search parameters like categories, language, time range, and safesearch level.
    - Validates input parameters.

### 3.10 Abstract Base Classes (`tools/__init__.py`)
This file defines abstract base classes (ABCs) that serve as interfaces for core functionalities:
- **`VectorDatabase`**: Defines the standard methods (`add_embeddings`, `search_embeddings`, `count`, `get_version`, `list_collections`, `reset_collection`) expected from any vector database implementation within this package (e.g., `ChromaDB`, `PgVectorDB`, `PineconeDB`).
- **`LLMService`**: Defines the standard methods (`generate_embedding`, `generate_text`, `generate_completions`, `generate_tokens`, `describe_image`, `list_models`, `get_model_details`) expected from any LLM service implementation (e.g., `LiteLLMServiceTool`).
These interfaces ensure consistency and allow for easier integration and swapping of different database or LLM providers.

### 4. Usage Examples

#### 4.1 Web Search
```python
from fbpyutils_ai.tools.search import SearXNGTool

searxng_tool = SearXNGTool() # Uses default base URL or env variable
results = searxng_tool.search("OpenAI", categories=["general"])
print(results)
```

## 5. Full Documentation
For detailed information on each feature and integration, refer to the documentation files:
- [AGENTS.md](AGENTS.md)
- [TOOLS.md](TOOLS.md)
- [DOC.md](DOC.md)

## 6. Contribution
Feel free to contribute to the project! If you have questions or suggestions, please reach out through the repository or our support channels.

## 7. License
This project is licensed under the MIT License. For the full text of the license, see [the official MIT License](https://opensource.org/licenses/MIT).

---
## MIT License Disclaimer

Copyright (c) 2025 Francisco C J Bispo

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.**
