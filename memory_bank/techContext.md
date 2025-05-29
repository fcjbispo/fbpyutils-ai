# Technical Context: FBPyUtils-AI

## Technologies Used

-   **Python:** The primary programming language for the project.
-   **Model Context Protocol (MCP):** Used for exposing tools to AI agents.
-   **Hatch:** Used for project management, dependency management, and packaging (`pyproject.toml`).
-   **uv:** A fast Python package installer and resolver, used for dependency management (`uv.lock`).
-   **pytest:** Testing framework.
-   **pytest-cov:** For measuring code coverage.
-   **Libraries for Web Interaction:**
    -   `requests`: Synchronous HTTP library.
    -   `httpx`: Asynchronous HTTP library.
    -   `Firecrawl API`: External service for web scraping and crawling, accessed via `FireCrawlTool`.
    -   `SearXNG`: Decentralized metasearch engine, accessed via `SearXNGTool`.
-   **Libraries for Data Handling:**
    -   `pandas`: For data manipulation and analysis, particularly with tabular data (used in `mcp_search_server.py`).
    -   `duckdb`: An in-process SQL OLAP database system (used in `mcp_search_server.py`).
    -   `json`, `csv`, `xml.etree.ElementTree`: Standard Python libraries for handling various text formats.
    -   `openpyxl`, `xlrd/xlwt`: Libraries for reading and writing Excel files (mentioned in `TOOLS.md` and `DOC.md` examples, but not yet fully integrated as tools).
-   **Libraries for Document Processing:**
    -   `docling`: Command-line tool for document conversion, wrapped by `DoclingConverter`.
    -   `pdf2image`, `Pillow`: Used for PDF preprocessing in `DoclingConverter`.
-   **Libraries for Vector Databases and Embeddings:**
    -   `chromadb`: ChromaDB client library.
    -   `psycopg`, `psycopg-binary`, `pgvector`: For interacting with PostgreSQL with the `pgvector` extension.
    -   `pinecone`: Pinecone client library.
    -   `tiktoken`: For tokenizing text, compatible with OpenAI models.
-   **Libraries for LLM Interaction:**
    -   `langchain`, `langchain-core`, `langchain-anthropic`, `langchain-mistralai`, `langchain-google-genai`, `langchain-ollama`, `langchain-openai`: Libraries for interacting with various LLM providers.
    -   `openai`: Python client for the OpenAI API (mentioned in `DOC.md` example).
-   **Libraries for Image Processing (Examples):**
    -   `OpenCV`: Computer vision library (mentioned in `DOC.md` example).
    -   `CLIP`: Model for connecting text and images (mentioned in `DOC.md` example).
-   **UI Libraries:**
    -   `marimo`: For building reactive notebooks/applications (used in `fbpyutils_ai/ui/marimo`).
-   **Other Utilities:**
    -   `python-dotenv`: For loading environment variables.
    -   `tenacity`: For retrying failed operations.
    -   `nest-asyncio`: To allow nesting of asyncio event loops.
    -   `browser-use`: Potentially for browser automation tasks.
    -   `MainContentExtractor`: For extracting main content from HTML.
    -   `uuid`: For generating unique identifiers.
    -   `playwright`: For browser automation (dependency).
    -   `fbpyutils`: A dependency library.
    -   `concurrent-log-handler`: For handling logs in a multiprocessing environment.
    -   `rich`: For rich text in the terminal (dev dependency).
    -   `tqdm`: For progress bars (dev dependency).
    -   `ipykernel`, `ipywidgets`, `widgetsnbextension`: For Jupyter/IPython integration (dev dependencies).
    -   `jsonschema`: For validating JSON schemas (dev dependency).

## Development Setup

1.  Clone the repository.
2.  Install dependencies using `uv pip install .` (for core dependencies) and potentially `uv pip install .[dev]` for development dependencies.
3.  Set necessary environment variables (e.g., `FBPY_LOG_LEVEL`, API keys for external services like SearXNG, Firecrawl, LLM providers).
4.  Run tests using `pytest`.
5.  Start the MCP server using `python -m fbpyutils_ai.servers.mcp_servers`.

## Technical Constraints

-   Requires Python 3.11 or later.
-   External dependencies must be installed.
-   Some tools require access to external services (SearXNG, Firecrawl, LLM APIs) and valid API keys or endpoints.
-   The `DoclingConverter` requires the `docling` CLI tool to be installed and in the system's PATH.
-   Database tools require access to the respective database instances.

## Dependencies

See the `[project.dependencies]` and `[project.optional-dependencies]` sections in `pyproject.toml` for a comprehensive list of runtime and optional dependencies. Development dependencies are listed in `[dependency-groups.dev]`.

## Tool Usage Patterns

-   Tools are generally implemented as Python classes, initialized with necessary configuration (e.g., base URLs, API keys).
-   Methods on these classes perform the core functionality (e.g., `search`, `scrape`, `convert`).
-   Asynchronous versions of methods may be provided for performance.
-   Error handling is typically done using exceptions.
-   Configuration often relies on environment variables or parameters passed during initialization.
