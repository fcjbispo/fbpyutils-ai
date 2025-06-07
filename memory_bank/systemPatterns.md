# System Patterns: FBPyUtils-AI

## System Architecture

The FBPyUtils-AI project is structured as a Python library providing a collection of tools primarily intended for use by AI agents. The architecture is designed for modularity, extensibility, and ease of integration.

Key components include:

1.  **Tool Modules (`fbpyutils_ai/tools/`)**: Individual Python modules implementing specific functionalities (e.g., `search.py`, `scrape.py`, `document.py`, `http.py`, `embedding.py`, `llm/`). These modules contain classes and functions that wrap existing libraries or implement custom logic.
2.  **Abstract Base Classes (`fbpyutils_ai/tools/__init__.py`)**: Define standard interfaces (`VectorDatabase`, `LLMServices`) that concrete tool implementations adhere to. This promotes consistency and allows for swapping different backend implementations.
4.  **Basic UI Components (`fbpyutils_ai/ui/`)**: Simple user interface elements (`inspector/`, `marimo/`) to aid developers in using and debugging the tools.
5.  **Configuration and Utilities**: Modules for handling logging (`fbpyutils_ai/__init__.py`) and potentially other shared utilities.

The primary interaction flow for AI agents is expected to be through the MCP server, which provides a standardized way to call the exposed tools. However, developers can also directly import and use classes and functions from the `fbpyutils_ai.tools` modules within their Python applications.

## Key Technical Decisions

-   **Modular Tool Design:** Each tool focuses on a specific task, promoting separation of concerns and maintainability.
-   **Use of Abstract Interfaces:** Enables flexibility and allows for integrating different implementations of core functionalities (e.g., various vector databases or LLM providers).
-   **Leveraging Existing Libraries:** Instead of reinventing the wheel, the project wraps established and robust Python libraries (`requests`, `httpx`, `docling`, `pandas`, database connectors, etc.) to provide functionalities.
-   **Environment-based Configuration:** Sensitive information like API keys and service URLs are often configured via environment variables, following standard practices.
-   **Asynchronous Operations:** Use of libraries like `httpx` suggests support for asynchronous HTTP requests, which can improve performance for I/O-bound tasks.

## Design Patterns in Use

-   **Adapter Pattern:** Tools often act as adapters, providing a consistent interface over different underlying libraries (e.g., `SearXNGTool` over the SearXNG API, `DoclingConverter` over the `docling` CLI).
-   **Abstract Factory Pattern:** The use of abstract base classes (`VectorDatabase`, `LLMServices`) and concrete implementations follows the principles of the Abstract Factory pattern, allowing for families of related objects (database connectors, LLM clients) to be created.
-   **Singleton Pattern (Potential):** While not explicitly stated, certain resources like HTTP clients or database connections might be managed as singletons or within a session context to optimize resource usage.

## Component Relationships

-   `fbpyutils_ai.tools.llm.OpenAITool` depends on `fbpyutils_ai.tools.http.RequestsManager` and `tiktoken`.
-   `fbpyutils_ai.tools.embedding.EmbeddingManager` depends on `fbpyutils_ai.tools.llm.LLMServices` implementations and `fbpyutils_ai.tools.embedding.VectorDatabase` implementations (`ChromaDB`, `PgVectorDB`, `PineconeDB`).
-   `fbpyutils_ai.tools.document.DoclingConverter` depends on the external `docling` CLI tool and potentially `pdf2image` and `Pillow`.
-   The basic UI components in `fbpyutils_ai/ui/marimo` likely depend on the core tools or their underlying logic to provide interactive examples or interfaces.

## Critical Implementation Paths

-   **Tool Initialization and Configuration:** Ensuring tools are correctly initialized with necessary parameters (API keys, base URLs) is critical for their functionality.
-   **Error Handling:** Robust error handling within each tool is essential to provide meaningful feedback to AI agents and prevent failures.
-   **Data Serialization/Deserialization:** Correctly handling data formats (JSON, XML, CSV, etc.) when interacting with external services or files is crucial.
-   **Asynchronous Operations Management:** For tools using asynchronous operations, proper management of event loops and concurrent requests is important for performance and stability.
-   **Dependency Management:** The project relies on numerous external libraries, and managing these dependencies (`pyproject.toml`, `uv.lock`) is vital for reproducibility.
