# Progress: FBPyUtils-AI

## What Works

Based on the provided `README.md`, `TODO.md`, and the file structure, the following functionalities are implemented to some extent:

-   **Internet Search:** Implemented via `SearXNGTool` and exposed through `mcp_search_server`.
-   **Web Content Extraction:** Implemented via `FireCrawlTool` (v1 API with supported methods for self-hosted mode) and exposed through `mcp_scrape_server`. Tests moved to `tests/crawl/`.
-   **HTTP Requests:** Core functionality available via `HTTPClient` and `RequestsManager`. Updated to handle Gzip/JSON and removed PUT/DELETE methods.
-   **Document Conversion:** Basic conversion available via `DoclingConverter`.
-   **Vector Database Interaction:** Interfaces and implementations for ChromaDB, PgVector, and Pinecone are present.
-   **LLM Interaction:** OpenAI-compatible LLM interaction, including embeddings and vision, is available via `LiteLLMServiceTool`.
-   **Basic UI:** Inspector and Marimo applications exist in `fbpyutils_ai/ui/`.

## What's Left to Build

According to `TODO.md`, `TOOLS.md`, and recent feedback, the following features need full implementation or significant work:

-   **Excel Manipulation Tool:** Not yet implemented. Examples (`openpyxl`, `pandas`) in DOC.md need integration into a dedicated tool.
-   **Text File Manipulation Tool:** `DoclingConverter` handles conversion, but dedicated tools for basic read/write of specific formats (JSON, CSV, HTML, MD, XML) as described in TOOLS.md needs dedicated implementation and tests.
-   **Image Reading/Description Tool:** `LiteLLMServiceTool.describe_image` exists, but dedicated tools or full integration of examples using libraries like OpenCV and CLIP from `DOC.md` are needed.
-   **Image Creation from Prompts Tool:** Partial implementation potentially via `LiteLLMServiceTool`, but needs explicit implementation and tests for image *creation*. DALL-E example in DOC.md needs integration or dedicated tool.
-   **General SQL Database Reading Tool:** `PgVectorDB` exists for vector operations, but a general tool for reading from SQL databases as planned in `TOOLS.md` is needed. Examples (`sqlite3`, `SQLAlchemy`) in DOC.md need integration or dedicated tools.
-   **Finish Basic UI Tools:** Complete the basic functionality for the `inspector` and `marimo` UI tools. The `marimo` module is predicted for the v0.1.1 release.
-   **Update All Documentation:** Ensure all documentation files (including Memory Bank) are updated to reflect the current project deliveries (v0.1.1).
-   **Increase Test Coverage:** Achieve a minimum code coverage of 90% for the current branch code development, as required by `../VIBE.md`.

## Current Status

-   Successfully rebased the local `v0.1.1` branch with the latest changes from the remote.
-   Core web interaction (search, scraping, HTTP) and LLM interaction tools are partially or fully implemented.
-   Document conversion and vector database integration are initiated.
-   Basic UI components are present but require completion.
-   Several planned tools (Excel, general text file handling, image description/creation, general SQL reading) are either missing or only partially implemented/represented by examples.
-   O plano de centralização da lógica de retry HTTP concluiu a Fase 4 (Análise de Impacto e Ajuste dos Testes Unitários). A Fase 5 (Implementação e Refatoração) foi iniciada, com modificações aplicadas em [`fbpyutils_ai/tools/http.py`](fbpyutils_ai/tools/http.py:1) e [`fbpyutils_ai/tools/llm/__init__.py`](fbpyutils_ai/tools/llm/__init__.py:1), e criação do arquivo de testes [`tests/tools/llm/test_llm.py`](tests/tools/llm/test_llm.py). Estamos atualmente corrigindo falhas nos testes unitários relacionados a essas mudanças, incluindo `AttributeError`s e `NameError`s nos testes do módulo LLM e `RetryError`s nos testes HTTP.
-   Overall test coverage is low (18.91%), indicating a need for substantial testing effort to reach the 90% target. Specific modules like `mcp_search_server.py` (0%), `mcp_scrape_server.py` (9.47%), `DoclingConverter` (0%), `PgVectorDB` (low coverage), e `HTTPClient`/`RequestsManager` (18.44%) têm cobertura particularmente baixa, e os ajustes de teste identificados na Fase 4 do plano de retry HTTP precisam ser implementados.
-   Documentation needs a comprehensive update to reflect the current v0.1.1 deliveries.

## Known Issues

-   Low test coverage across many modules, posing a risk to stability and reliability.
-   Examples provided in `DOC.md` for some planned tools (Excel, image processing, SQL) are not yet integrated into the main tool structure.
-   Specific server modules (`mcp_search_server.py`, `mcp_scrape_server.py`) and tools (`DoclingConverter`, `PgVectorDB`, `HTTPClient`/`RequestsManager`) have particularly low test coverage.
-   Basic UI tools (`inspector`, `marimo`) are not yet fully functional.
-   Documentation is not fully up-to-date with the current v0.1.1 deliveries.
