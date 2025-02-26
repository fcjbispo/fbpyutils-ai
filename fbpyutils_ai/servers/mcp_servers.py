from typing import List
import argparse
from mcp.server.fastmcp import FastMCP
from fbpyutils_ai.servers.mcp_search_server import search
from fbpyutils_ai.servers.mcp_scrape_server import scrape, scrape_n

# Initialize FastMCP server
mcp = FastMCP("fbpyutils_ai_tools")


@mcp.tool()
async def web_search(query: str, language: str = 'auto', max_results: int = 10, sort_by: str = 'score', safesearch: bool = False) -> str:
    """
    Performs a general internet search on internet web using various search mechanisms.
    Args:
        query: The search query.
        language: The language of the search query. Ex: 'en'. Default: 'auto'.
        max_results: The maximum number of results to return. Default: 10.
        sort_by: The sorting criterion for the results. Valid values: Any output field except 'other_info'. Default is 'score'.
        safesearch: Indicates whether the search should be safe (without explicit content). Default: False.
    """
    return await search(query, language=language, max_results=max_results, sort_by=sort_by, safesearch=safesearch, categories=['general'])


@mcp.tool()
async def web_search_images(query: str, language: str = 'auto', max_results: int = 10, sort_by: str = 'score', safesearch: bool = False) -> str:
    """
    Performs an image search on internet web using various search mechanisms.
    Args:
        query: The search query.
        language: The language of the search query. Ex: 'en'. Default: 'auto'.
        max_results: The maximum number of results to return. Default: 10.
        sort_by: The sorting criterion for the results. Valid values: Any output field except 'other_info'. Default is 'score'.
        safesearch: Indicates whether the search should be safe (without explicit content). Default: False.
    """
    return await search(query, language=language, max_results=max_results, sort_by=sort_by, safesearch=safesearch, categories=['images'])


@mcp.tool()
async def web_search_videos(query: str, language: str = 'auto', max_results: int = 10, sort_by: str = 'score', safesearch: bool = False) -> str:
    """
    Performs a video search on internet web using various search mechanisms.
    Args:
        query: The search query.
        language: The language of the search query. Ex: 'en'. Default: 'auto'.
        max_results: The maximum number of results to return. Default: 10.
        sort_by: The sorting criterion for the results. Valid values: Any output field except 'other_info'. Default is 'score'.
        safesearch: Indicates whether the search should be safe (without explicit content). Default: False.
    """
    return await search(query, language=language, max_results=max_results, sort_by=sort_by, safesearch=safesearch, categories=['videos'])


@mcp.tool()
async def web_search_music(query: str, language: str = 'auto', max_results: int = 10, sort_by: str = 'score', safesearch: bool = False) -> str:
    """
    Performs a music search on internet web using various search mechanisms.
    Args:
        query: The search query.
        language: The language of the search query. Ex: 'en'. Default: 'auto'.
        max_results: The maximum number of results to return. Default: 10.
        sort_by: The sorting criterion for the results. Valid values: Any output field except 'other_info'. Default is 'score'.
        safesearch: Indicates whether the search should be safe (without explicit content). Default: False.
    """
    return await search(query, language=language, max_results=max_results, sort_by=sort_by, safesearch=safesearch, categories=['music'])


@mcp.tool()
async def web_search_map(query: str, language: str = 'auto', max_results: int = 10, sort_by: str = 'score', safesearch: bool = False) -> str:
    """
    Performs a map search on internet web using various search mechanisms.
    Args:
        query: The search query.
        language: The language of the search query. Ex: 'en'. Default: 'auto'.
        max_results: The maximum number of results to return. Default: 10.
        sort_by: The sorting criterion for the results. Valid values: Any output field except 'other_info'. Default is 'score'.
        safesearch: Indicates whether the search should be safe (without explicit content). Default: False.
    """
    return await search(query, language=language, max_results=max_results, sort_by=sort_by, safesearch=safesearch, categories=['map'])

@mcp.tool()
async def web_scrape(url: str, tags_to_remove: List[str] = [], timeout: int = 30000) -> str:
    """
    Scrapes a webpage and extracts full content in Markdown format.
    
    Args:
        url: The URL of the webpage to scrape.
        tags_to_remove: A list of HTML tags to remove. Ex: ['/script', '/ad']. Defaults to an empty list.
        timeout: Maximum time to wait for scraping. Defaults to 30000.
    """
    tags_to_remove = tags_to_remove or []
    for t in ["script", ".ad", "#footer"]:
        if t not in tags_to_remove:
            tags_to_remove.append(t)

    return await scrape(url, tags_to_remove=tags_to_remove, timeout=timeout)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
