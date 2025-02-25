import duckdb as ddb
import pandas as pd

from typing import Dict, Union, Any, List

from fbpyutils_ai.tools.search import SearXNGTool
from fbpyutils_ai.tools.crawl import FireCrawlTool

from mcp.server.fastmcp import FastMCP


# Define the templates for each category
_category_templates = {
    'images': ["img_src", "title", "score", "resolution", "thumbnail_src", "publishedDate"],
    'music': ["url", "title", "author", "content", "score", "length", "publishedDate", "thumbnail", "iframe_src"],
    'videos': ["url", "title", "author", "content", "score", "length", "publishedDate", "thumbnail", "iframe_src"],
    'map': ["url", "title", "score", "latitude", "longitude", "boundingbox", "geojson", "publishedDate"],
    'general': ["url", "title", "content", "score", "publishedDate"]
}

# Initialize SearXNG tool
_searxng = SearXNGTool()

# Initialize FireCrawl tool
_firecrawl = FireCrawlTool()

# Initialize FastMCP server
mcp = FastMCP("fbpyutilsai_web_search")


async def _apply_category(results: List[Dict[str, Union[str, int, float, bool, None]]], category: str) -> pd.DataFrame:
    if category not in _category_templates.keys():
        category = 'general'

    results_list = []
    key_columns = _category_templates[category]
    for result in results:
        result_record = {}
        for key in key_columns:
            result_record[key] = str(result.get(key))
        other_keys = [k for k in result.keys() if k not in key_columns]
        result_record["other_info"] = {k: str(result[k]) for k in other_keys}
        results_list.append(result_record)
    return pd.DataFrame.from_dict(results_list, orient="columns")


async def _format_table(results: List[Dict[str, Union[str, int, float, bool, None]]], max_results: int, sort_by: str, category: str) -> str:
    if len(results) == 0:
        return f"No results found."
    # Simplify the results and convert to a DataFrame
    results_data = await _apply_category(results, category)

    # Create a DuckDB database and insert the results to perform sorting and limiting
    return ddb.sql(f"SELECT * FROM results_data ORDER BY {sort_by} DESC LIMIT {max_results}").to_df().to_markdown(index=False)


async def _perform_search(query: str, language, max_results, sort_by, categories, safesearch) -> Any:
    if query is None or query == "":
        return "Unable to perform an empty search. Please provide a search query."
    if max_results is None or max_results < 0:
        max_results = 10
    if language is None or language not in _searxng.LANGUAGES:
        language = 'auto'
    if safesearch is None or safesearch not in [True, False]:
        safesearch = False
    if categories is None or len(categories) == 0 or not all(category in _searxng.CATEGORIES for category in categories):
        raise ValueError("Invalid category selected.")
    
    category = categories[0]
    if sort_by is None or sort_by not in _category_templates[category]:
        sort_by = 'score'

    # Perform the search on internet web using SearXNG
    results = await _searxng.async_search(
        query,
        method='GET',
        categories=categories,
        language=language,
        safesearch=int(safesearch))

    return await _format_table(results, max_results, sort_by, category=categories[0])


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
    return await _perform_search(query, language=language, max_results=max_results, sort_by=sort_by, safesearch=safesearch, categories=['general'])


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
    return await _perform_search(query, language=language, max_results=max_results, sort_by=sort_by, safesearch=safesearch, categories=['images'])


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
    return await _perform_search(query, language=language, max_results=max_results, sort_by=sort_by, safesearch=safesearch, categories=['videos'])


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
    return await _perform_search(query, language=language, max_results=max_results, sort_by=sort_by, safesearch=safesearch, categories=['music'])


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
    return await _perform_search(query, language=language, max_results=max_results, sort_by=sort_by, safesearch=safesearch, categories=['map'])


async def _metadata_to_markdown(metadata: dict) -> str:
    title = metadata.get("title") or metadata.get("ogTitle") or "Sem Título"
    description = metadata.get("description") or metadata.get("ogDescription") or "Sem descrição"
    url = metadata.get("url") or metadata.get("ogUrl") or metadata.get("sourceURL") or ""
    language = metadata.get("language") or "N/A"
    author = metadata.get("sailthru.author") or metadata.get("article:author") or "Desconhecido"
    tags = metadata.get("sailthru.tags") or metadata.get("parsely-tags") or ""
    favicon = metadata.get("favicon")
    og_image = metadata.get("ogImage") or metadata.get("og:image")

    markdown_lines = [
        "# Page Metadata",
        "",
        f"**Page**:{title}",
        "",
        f"**Descrição**: {description}",
        "",
    ]
    if url:
        markdown_lines.append(f"**URL**: [{url}]({url})")
        markdown_lines.append("")
    markdown_lines.append(f"**Idioma**: {language}")
    markdown_lines.append("")
    markdown_lines.append(f"**Autor**: {author}")
    markdown_lines.append("")
    if tags:
        markdown_lines.append(f"**Tags**: {tags}")
        markdown_lines.append("")
    if favicon:
        markdown_lines.append(f"**Favicon**: ![Favicon]({favicon})")
        markdown_lines.append("")
    if og_image:
        markdown_lines.append(f"**Imagem Principal**: ![Imagem Principal]({og_image})")
        markdown_lines.append("")

    return "\n".join(markdown_lines)


async def _links_to_markdown(links: list) -> str:
    markdown_lines = ["# Page Links", ""]
    for link in links:
        markdown_lines.append(f"- [{link}]({link})")
    return "\n".join(markdown_lines)


async def _scrape_result_to_markdown(scrape_result: dict) -> str:
    if not (scrape_result['success'], scrape_result['returnCode']) == (True, 200):
        return "# No content found"
    else:
        scrape_content = {
            k: scrape_result['data'][k] 
            for  k in scrape_result['data'].keys() 
            if k in ['metadata', 'markdown', 'linksOnPage']
        }

        contents = scrape_content['markdown']
        metadata = await _metadata_to_markdown(scrape_content['metadata'])
        links = await _links_to_markdown(scrape_content['linksOnPage'])

        return f"""
        # Page Contents:
        {contents}
        ---
        {metadata}
        ---
        {links}
        """

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

    scrape_result = await _firecrawl.scrape(
        url=url,
        pageOptions={
            "includeHtml": False,
            "includeRawHtml": False,
            "onlyMainContent": True,
            "removeTags": tags_to_remove,
            "replaceAllPathsWithAbsolutePaths": True,
            "waitFor": 200
        },
        extractorOptions={
            "mode": "markdown"
        },
        timeout=timeout,
    )
    return await _scrape_result_to_markdown(scrape_result)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
