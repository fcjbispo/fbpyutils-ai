import duckdb as ddb
import pandas as pd

from typing import Dict, Union, Any, List

from fbpyutils_ai.tools.search import SearXNGTool


# Define the templates for each category
_category_templates = {
    "images": [
        "img_src",
        "title",
        "score",
        "resolution",
        "thumbnail_src",
        "publishedDate",
    ],
    "music": [
        "url",
        "title",
        "author",
        "content",
        "score",
        "length",
        "publishedDate",
        "thumbnail",
        "iframe_src",
    ],
    "videos": [
        "url",
        "title",
        "author",
        "content",
        "score",
        "length",
        "publishedDate",
        "thumbnail",
        "iframe_src",
    ],
    "map": [
        "url",
        "title",
        "score",
        "latitude",
        "longitude",
        "boundingbox",
        "geojson",
        "publishedDate",
    ],
    "general": ["url", "title", "content", "score", "publishedDate"],
}

# Initialize SearXNG tool
_searxng = SearXNGTool()


async def _apply_category(
    results: List[Dict[str, Union[str, int, float, bool, None]]], category: str
) -> pd.DataFrame:
    """
    Applies a category template to filter and structure search results into a DataFrame.

    Args:
        results: A list of dictionaries, where each dictionary is a search result.
        category: The category template to apply (e.g., 'images', 'general').

    Returns:
        A pandas DataFrame with structured results based on the category template.
    """
    if category not in _category_templates.keys():
        category = "general"

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


async def _format(
    results: List[Dict[str, Union[str, int, float, bool, None]]],
    max_results: int,
    sort_by: str,
    category: str,
    format_type: str = "markdown",
) -> Union[str, List[Dict[str, Any]]]:
    """
    Formats the search results into the specified format (Markdown or raw dictionary list).

    Sorts and limits the results using DuckDB before formatting.

    Args:
        results: The list of raw search result dictionaries.
        max_results: The maximum number of results to return.
        sort_by: The field to sort the results by.
        category: The search category used (influences available sort fields).
        format_type: The desired output format ('markdown' or 'raw'). Defaults to 'markdown'.

    Returns:
        The formatted results, either as a Markdown string or a list of dictionaries.
        Returns a simple string message if no results are found.
    """
    if len(results) == 0:
        return f"No results found."

    format_type = format_type or "markdown"
    if format_type not in ("raw", "markdown"):
        format_type = "markdown"

    # Create a DuckDB database and insert the results to perform sorting and limiting
    # Simplify the results and convert to a DataFrame
    results_data = await _apply_category(results, category)

    # Create a DuckDB database and insert the results to perform sorting and limiting
    results = ddb.sql(
        f"SELECT * FROM results_data ORDER BY {sort_by} DESC LIMIT {max_results}"
    ).to_df()

    return (
        results.to_markdown(index=False)
        if format_type == "markdown"
        else results.to_dict(orient="records")
    )


async def search(
    query: str,
    language: str,
    max_results: int,
    sort_by: str,
    categories: List[str],
    safesearch: bool,
    raw: bool = False,
) -> Union[str, List[Dict[str, Any]]]:
    """
    Performs a web search using SearXNG, processes the results, and returns them formatted.

    Args:
        query: The search query string.
        language: The language code for the search (e.g., 'en', 'pt-BR', 'auto').
        max_results: The maximum number of results to return.
        sort_by: The field to sort results by (depends on category, defaults to 'score').
        categories: A list containing the search category (e.g., ['general'], ['images']).
                    Currently, only the first category in the list is used.
        safesearch: Whether to enable safe search (True/False).
        raw: If True, returns results as a list of dictionaries. Otherwise, returns Markdown. Defaults to False.

    Returns:
        Formatted search results (Markdown string or list of dictionaries),
        or an error message string.

    Raises:
        ValueError: If an invalid category is provided.
    """
    if query is None or query == "":
        return "Unable to perform an empty search. Please provide a search query."
    if max_results is None or max_results < 0:
        max_results = 10
    if language is None or language not in _searxng.LANGUAGES:
        language = "auto"
    if safesearch is None or safesearch not in [True, False]:
        safesearch = False
    if (
        categories is None
        or len(categories) == 0
        or not all(category in _searxng.CATEGORIES for category in categories)
    ):
        raise ValueError("Invalid category selected.")

    category = categories[0]
    if sort_by is None or sort_by not in _category_templates[category]:
        sort_by = "score"

    # Perform the search on internet web using SearXNG
    results = await _searxng.async_search(
        query,
        categories=categories,
        language=language,
        safesearch=int(safesearch),
    )

    format_type = "raw" if raw else "markdown"

    return await _format(
        results, max_results, sort_by, category=categories[0], format_type=format_type
    )
