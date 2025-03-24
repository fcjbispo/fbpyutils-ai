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

## 3. Usage

### 3.1 Environment Setup
To install the dependencies, run:
```bash
uv pip install .
```

This command installs the required libraries listed in `pyproject.toml`.

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
This project is licensed under the [MIT License](LICENSE).
