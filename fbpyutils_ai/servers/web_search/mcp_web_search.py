import duckdb as ddb
import pandas as pd

from typing import Dict, Union, Any, List

from fbpyutils_ai.tools.search import SearXNGTool
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
        query (str): The search query.
        language (str): The language of the search query. Default: 'auto'.
        max_results (int): The maximum number of results to return. Default: 10.
        sort_by (str): The sorting criterion for the results. Valid values: Any output field except 'other_info'. Default is 'score'.
        safe (bool): Indicates whether the search should be safe (without explicit content). Default: False.
    Returns:
        str: Search results in Markdown table format:
            - **url**: URL of the result.
            - **title**: Title of the result.
            - **content**: Summary of the result's content.
            - **score**: Score of relevance of the result.
            - **publishedDate**: Publication date of the result.
            - **other_info**: Other relevant information
    """
    return await _perform_search(query, language=language, max_results=max_results, sort_by=sort_by, safesearch=safesearch, categories=['general'])


@mcp.tool()
async def web_search_images(query: str, language: str = 'auto', max_results: int = 10, sort_by: str = 'score', safesearch: bool = False) -> str:
    """
    Performs an image search on internet web using various search mechanisms.

    Args:
        query (str): The search query.
        language (str): The language of the search query. Default is 'auto'.
        max_results (int): The maximum number of results to return. Default is 10.
        sort_by (str): The sorting criterion for the results. Valid values: Any output field except 'other_info'. Default is 'score'.
        safe (bool): Indicates whether the search should be safe, excluding explicit content. Default is False.

    Returns:
        str: Search results in Markdown table format with the following columns:
            - **img_src**: The URL of the result.
            - **title**: The title of the result.
            - **score**: The relevance score of the result.
            - **resolution**: The resolution of the image (if available).
            - **thumbnail_src**: The thumbnail source URL (if available).
            - **publishedDate**: The publication date of the result.
            - **other_info**: Other relevant information
    """
    return await _perform_search(query, language=language, max_results=max_results, sort_by=sort_by, safesearch=safesearch, categories=['images'])


@mcp.tool()
async def web_search_videos(query: str, language: str = 'auto', max_results: int = 10, sort_by: str = 'score', safesearch: bool = False) -> str:
    """
    Performs a video search on internet web using various search mechanisms.

    Args:
        query (str): The search query.
        language (str, optional): The language code for the query. Defaults to 'auto'.
        max_results (int, optional): The maximum number of video results to return. Defaults to 10.
        sort_by (str): The sorting criterion for the results. Valid values: Any output field except 'other_info'. Default is 'score'.
        safesearch (bool, optional): If True, filters out explicit content. Defaults to False.

    Returns:
        str: Search results in Markdown table format with the following columns:
            - **url**: URL of the video.
            - **title**: Title of the video.
            - **author**: The video creator or channel name.
            - **content**: A brief description or summary of the video's content.
            - **score**: Relevance score assigned to the video.
            - **length**: Duration of the video.
            - **publishedDate**: Publication date of the video.
            - **thumbnail**: URL of the video's thumbnail image.
            - **iframe_src**: URL used to embed the video.
            - **other_info**: Additional metadata or relevant information.
    """
    return await _perform_search(query, language=language, max_results=max_results, sort_by=sort_by, safesearch=safesearch, categories=['videos'])


@mcp.tool()
async def web_search_music(query: str, language: str = 'auto', max_results: int = 10, sort_by: str = 'score', safesearch: bool = False) -> str:
    """
    Performs a music search on internet web using various search mechanisms.

    Args:
        query (str): The search query.
        language (str, optional): The language code for the query. Defaults to 'auto'.
        max_results (int, optional): The maximum number of music results to return. Defaults to 10.
        sort_by (str): The sorting criterion for the results. Valid values: Any output field except 'other_info'. Default is 'score'.
        safesearch (bool, optional): If True, filters out explicit content. Defaults to False.

    Returns:
        str: Search results in Markdown table format with the following columns:
            - **url**: URL of the music track.
            - **title**: Title of the track.
            - **author**: Name of the artist or channel.
            - **content**: Additional details or a summary about the track.
            - **score**: Relevance score assigned to the track.
            - **length**: Duration of the track (if available).
            - **publishedDate**: Publication date of the track.
            - **thumbnail**: URL of the track's thumbnail image.
            - **iframe_src**: URL used to embed the track.
            - **other_info**: Additional metadata or relevant information.
    """
    return await _perform_search(query, language=language, max_results=max_results, sort_by=sort_by, safesearch=safesearch, categories=['music'])


@mcp.tool()
async def web_search_map(query: str, language: str = 'auto', max_results: int = 10, sort_by: str = 'score', safesearch: bool = False) -> str:
    """
    Performs a map search on internet web using various search mechanisms.

    Args:
        query (str): The search query.
        language (str, optional): The language code for the query. Defaults to 'auto'.
        max_results (int, optional): The maximum number of map results to return. Defaults to 10.
        sort_by (str): The sorting criterion for the results. Valid values: Any output field except 'other_info'. Default is 'score'.
        safesearch (bool, optional): If True, filters out explicit content. Defaults to False.

    Returns:
        str: Search results in Markdown table format with the following columns:
            - **url**: URL linking to the map resource.
            - **title**: Title or name of the location.
            - **score**: Relevance score assigned to the result.
            - **latitude**: Latitude coordinate of the location.
            - **longitude**: Longitude coordinate of the location.
            - **boundingbox**: The bounding box coordinates defining the area of the location.
            - **geojson**: GeoJSON representation of the location geometry.
            - **publishedDate**: The publication date of the map data (if available).
            - **other_info**: Additional metadata or relevant information about the location.
    """
    return await _perform_search(query, language=language, max_results=max_results, sort_by=sort_by, safesearch=safesearch, categories=['map'])


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
