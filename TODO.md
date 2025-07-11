# TODO List: Feature Implementation vs. Plan (TOOLS.md) - Version 0.1.1

This list compares the features planned in `TOOLS.md` with the current implementation status based on `README.md`, `DOC.md`, and test coverage from `coverage.xml`.

| Feature (TOOLS.md)                 | Initialized? | Implemented?                                     | Tested? (Coverage File)             | Coverage % | Notes                                                                 |
| :--------------------------------- | :----------: | :----------------------------------------------- | :---------------------------------- | :--------: | :-------------------------------------------------------------------- |
| 1. Internet Search Tool            |      ✅      | ✅ (`SearXNGTool`)                                 | ✅ (`tools/search.py`)              |   22.68%   | Needs more tests.                                                     |
| 2. Web Content Extraction Tool | ✅ | ✅ (`FireCrawlTool` v1 - flattened methods)        | ✅ (`tests/scrape/`) | 29.11% | `FireCrawlTool` methods flattened. Tests in `tests/scrape/` need expansion for new methods and better coverage. `lxml` example exists but not integrated as a tool. |
| 3. Marimo UI for AI Tools          |      ✅      | ✅ (`ui/marimo/app_main.py`, `app_llm_tool.py`, `app_search_tool.py`, `app_firecrawl_tool.py`) | ✅ | - | New UI for demonstrating AI tools, using `mo.accordion` for layout. "Home" page implemented. "Generate Text" and "Generate Embeddings" sub-sessions implemented and tested in LLM UI. |
| 4. Excel Manipulation Tool         |      ❌      | ❌                                               | ❌                                  |     -      | Feature not implemented. Examples (`openpyxl`, `pandas`) in DOC.md need integration. |
| 5. Text File Manipulation Tool     |      ✅      | Partial (`DoclingConverter` for conversion)      | ✅ (`tools/document.py`)            |     0%     | `DoclingConverter` needs tests. Basic read/write for specific formats (JSON, CSV, etc.) as described in TOOLS.md needs dedicated implementation and tests. |
| 6. Image Reading/Description Tool  |      ✅      | Partial (`LiteLLMServiceTool.describe_image`)            | ✅ (`tools/llm.py`)                 |   16.55%   | `LiteLLMServiceTool.describe_image` needs specific tests. Examples (`OpenCV`, `CLIP`) in DOC.md need integration or dedicated tools. |
| 7. Image Creation from Prompts Tool|      ✅      | Partial (Potentially via `LiteLLMServiceTool`)           | ✅ (`tools/llm.py`)                 |   16.55%   | Need explicit implementation and tests for image *creation*. DALL-E example in DOC.md needs integration or dedicated tool. |
| 8. SQL Database Reading Tool       |      ✅      | Partial (`PgVectorDB` for vector ops)            | ✅ (`tools/embedding.py`)           |   18.47%   | Need a general SQL reading tool as planned. Examples (`sqlite3`, `SQLAlchemy`) in DOC.md need integration or dedicated tool. `PgVectorDB` part has low coverage. |
| 9. Remote API Execution Tool       |      ✅      | ✅ (`HTTPClient`, `RequestsManager`)             | ✅ (`tools/http.py`)                |   18.44%   | Updated: Removed PUT/DELETE, added Gzip/JSON handling. Coverage still low. Needs more tests reflecting changes. |

**Overall Coverage:** (To be recalculated after MCP removal) - Indicates significant testing gaps across the implemented features.

**Key Actions:**
- Melhoria na interface da UI marimo com inclusao de novas funcinalidades e correcoes.
- Desenvolvimento das proximas ferramentas previstas.
- Aumento da cobertura dos testes unitarios e funcionais.
- Implement missing features (Excel, dedicated Text File tools, Image Creation, SQL Reading).
- Integrate example code from DOC.md into proper tools where applicable.
- Increase test coverage significantly for all implemented modules.
