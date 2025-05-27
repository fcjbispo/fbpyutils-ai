# Planning Document for Python AI Application - Version 0.1.1

## Introduction
This document describes a Python set of applications and that provides tools to artificial intelligence agents to perform various tasks, including internet research, web page content extraction, Excel spreadsheet manipulation, reading and creating text files in different formats (JSON, CSV, HTML, MD, XML), reading and describing image files, creating images from prompts, reading SQL databases, and executing remote APIs. To achieve this, suitable functions, classes and data structures will be presented in the Model Context Protocol (MCP) format.

## AI Agents and Tools

### 1. Internet Search Tool
**Role:** Perform internet searches to gather relevant information.
**Skills:**
- Formulate effective search queries.
- Navigate and extract data from search results.
**Tasks:**
- Receive a topic or question and return relevant information.
- Filter and summarize results for concise answers.
**Tools:**
- Scraping libraries: `BeautifulSoup`, `Scrapy`.
- Search engine APIs: `Google Custom Search API`.

### 2. Web Content Extraction Tool
**Role:** Interact with the Firecrawl API v1 for web scraping, crawling, extraction, mapping, and searching, providing formatted output and parallel processing capabilities.
**Skills:**
- Interact with the Firecrawl API v1 (cloud and self-hosted).
- Configure parameters for various operations (scrape, scrape, extract, map, search, batch scrape) using a "flattened" parameter structure.
- Handle API responses, job IDs, status, and errors.
- Format scrape results into Markdown.
- Process multiple scrape requests in parallel.
**Tasks:**
- Given URLs and options, perform scraping, crawling, extraction, mapping, or searching using the Firecrawl service.
- Retrieve the status and results of asynchronous jobs (scrape, batch scrape, extract).
- Cancel running jobs and retrieve job errors.
- Handle API responses and potential errors, considering self-hosted limitations.
- Scrape single or multiple URLs and return formatted Markdown content.
**Tools:**
- **Primary:** `FireCrawlTool` (from `fbpyutils_ai.tools.scrape`) interacting with the [Firecrawl API v1](https://docs.firecrawl.dev/api-reference/introduction). Includes methods like `scrape`, `scrape`, `batch_scrape`, `extract`, `map`, `search`, `get_crawl_status`, `cancel_crawl`, `get_crawl_errors`, `get_batch_scrape_status`, `get_batch_scrape_errors`, `get_extract_status`, `scrape_formatted`, and `scrape_multiple`.
- (Secondary/Alternative: Libraries like `BeautifulSoup`, `lxml`, `Selenium` could be used for direct, local scraping if needed, but `FireCrawlTool` is the integrated solution).

### 3. Marimo UI for AI Tools
**Role:** Provide an interactive web-based user interface for demonstrating and interacting with the AI tools.
**Skills:**
- Develop Marimo notebooks for interactive data exploration and tool demonstration.
- Integrate various AI tool functionalities into a unified UI.
- Utilize Marimo UI components (e.g., `mo.accordion`, `mo.ui.text_area`, `mo.ui.dropdown`, `mo.ui.switch`).
**Tasks:**
- Create a main Marimo application (`app_main.py`) to serve as the central hub for all AI tools.
- Develop individual Marimo modules for each AI tool (e.g., `app_llm_tool.py`, `app_search_tool.py`, `app_firecrawl_tool.py`).
- Expose key functionalities of each tool through interactive UI elements, including dedicated sub-sections for "Generate Text" and "Generate Embeddings" within the LLM tool.
- Display tool inputs, outputs, and status messages clearly.
**Tools:**
- **Primary:** `marimo` framework.
- Python modules: `fbpyutils_ai.ui.marimo.app_main`, `fbpyutils_ai.ui.marimo.app_llm_tool`, `fbpyutils_ai.ui.marimo.app_search_tool`, `fbpyutils_ai.ui.marimo.app_firecrawl_tool`, `fbpyutils_ai.ui.marimo.components`.

### 4. Excel Spreadsheet Manipulation Tool
**Role:** Read, write, and manipulate Excel spreadsheets.
**Skills:**
- Knowledge of Excel formats (XLSX, XLS).
- Perform operations such as reading, writing, filtering, and calculations.
**Tasks:**
- Read data from spreadsheets and convert it into Python structures.
- Write data to spreadsheets from Python structures.
- Perform filtering, aggregation, and calculations on data.
**Tools:**
- Libraries: `openpyxl`, `pandas`, `xlrd/xlwt`.

### 5. Text File Manipulation Tool
**Role:** Read and create text files in formats such as JSON, CSV, HTML, MD, XML.
**Skills:**
- Knowledge of file formats and their structures.
- Parse and generate files in the specified formats.
**Tasks:**
- Read files and convert their content into Python structures.
- Write Python structures to files in the specified formats.
**Tools:**
- Standard libraries: `json`, `csv`, `xml.etree.ElementTree`.
- Additional libraries: `pandas` (CSV), `BeautifulSoup` (HTML/XML).

### 6. Image Reading and Description Tool
**Role:** Analyze and describe the content of image files.
**Skills:**
- Process images and extract visual features.
- Generate textual descriptions of image content.
**Tasks:**
- Receive an image and return a textual description.
- Identify objects, scenes, text, etc., in the image.
**Tools:**
- Computer vision libraries: `OpenCV`.
- AI models: `CLIP`, pre-trained captioning models.

### 7. Image Creation from Prompts Tool
**Role:** Generate images based on textual descriptions (prompts).
**Skills:**
- Interpret text and convert it into visual representations.
- Generate high-quality images corresponding to the prompts.
**Tasks:**
- Receive a prompt and generate a corresponding image.
- Adjust parameters to control style and quality.
**Tools:**
- Generative models: `DALL-E`, `Stable Diffusion`.
- Libraries for image generation APIs, if applicable.

### 8. SQL Database Reading Tool
**Role:** Connect to SQL databases and execute queries.
**Skills:**
- Knowledge of SQL and database structure.
- Execute queries and manipulate returned data.
**Tasks:**
- Connect to an SQL database with provided credentials.
- Execute queries and return results in usable formats.
**Tools:**
- Connection libraries: `sqlite3`, `mysql-connector`, `psycopg2`.
- ORM: `SQLAlchemy` for abstraction.

### 9. Remote API Execution Tool
**Role:** Interact with remote APIs to send and receive data.
**Skills:**
- Knowledge of HTTP protocols and formats (JSON, XML).
- Authenticate and manage API sessions.
**Tasks:**
- Send HTTP requests (GET, POST, etc.) to remote APIs.
- Parse responses and extract relevant data.
**Tools:**
- HTTP libraries: `requests`, `httpx`.
- Libraries for authentication, if necessary.

## Integration and Orchestration
For the agents to work cohesively, an orchestration system is needed to manage communication and data flow between them. Suggestions include:
- **Frameworks:** `LangChain` or `AutoGen` for conversational agents and tool integration.
- **Messaging System:** Passing data and commands between agents.
- **Central Module:** Task coordination and responsibility distribution.

## Final Considerations
- **Security:** Protect sensitive data, especially in databases and APIs.
- **Scalability:** Design the application to support the expansion of agents or tasks.
- **Maintenance:** Modular and documented code to facilitate updates.
