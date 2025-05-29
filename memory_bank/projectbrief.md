# Project Brief: FBPyUtils-AI

## Core Requirements and Goals

The primary goal of the FBPyUtils-AI project is to create a comprehensive Python library providing essential utilities for Artificial Intelligence agents. This library will focus on enabling agents to interact with external resources and data sources, specifically:

1.  **Internet Research:** Provide tools for performing web searches and gathering information from the internet.
2.  **Web Content Extraction:** Offer capabilities to scrape and extract specific content from web pages.
3.  **Data Processing and Manipulation:** Include tools for handling various data formats, such as text files (JSON, CSV, HTML, MD, XML), Excel spreadsheets, and potentially image files and SQL databases.
4.  **Remote API Interaction:** Facilitate making HTTP requests to interact with external web services and APIs.
5.  **Document Conversion:** Provide utilities for converting documents between various formats.
6.  **Vector Database Integration:** Offer tools for managing and searching vector embeddings for semantic search and RAG applications.
7.  **Basic UI Features:** Provide simple user interface components, such as an inspector and Marimo applications, to aid in development and debugging.

## Project Scope

The project aims to deliver a modular and extensible set of tools, primarily exposed via the Model Context Protocol (MCP) to be easily consumable by AI agents. It also includes basic UI components to assist developers. The initial focus is on implementing the core functionalities identified above, with potential for expansion based on future needs.

## Key Deliverables

-   A Python package (`fbpyutils_ai`) containing the core utility classes and functions.
-   MCP server implementations (`mcp_scrape_server.py`, `mcp_search_server.py`, `mcp_servers.py`) to expose key tools.
-   Basic UI components (`fbpyutils_ai/ui/inspector`, `fbpyutils_ai/ui/marimo`).
-   Clear documentation (`README.md`, `TOOLS.md`, `DOC.md`, and Memory Bank files) detailing the tools, their usage, and the project's architecture.
-   Automated tests to ensure the reliability and correctness of the implemented tools.

## Non-Goals

-   Developing a full-fledged AI agent framework (leveraging existing ones like LangChain or AutoGen is preferred).
-   Building a complex, production-ready graphical user interface.
-   Implementing complex natural language processing (NLP) tasks within the core library (relying on external LLM services via the provided tools is the approach).

## Target Audience

The primary users of this library are AI agents and developers building AI applications that require interaction with external data sources and services. The basic UI features are intended to support these developers.

## Success Criteria

-   Successful implementation and testing of the core tools (Web Search, Web Scraping, HTTP Requests, Document Conversion, Vector Database).
-   Ability to expose these tools effectively via the MCP server.
-   Functional basic UI components (inspector, Marimo apps).
-   Comprehensive and accurate documentation that allows AI agents and developers to understand and utilize the tools and UI components.
-   Maintainable and extensible codebase.
