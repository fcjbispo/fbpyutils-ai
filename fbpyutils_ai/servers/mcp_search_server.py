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


async def _format_table(
    results: List[Dict[str, Union[str, int, float, bool, None]]],
    max_results: int,
    sort_by: str,
    category: str,
) -> str:
    if len(results) == 0:
        return f"No results found."
    # Simplify the results and convert to a DataFrame
    results_data = await _apply_category(results, category)

    # Create a DuckDB database and insert the results to perform sorting and limiting
    return (
        ddb.sql(
            f"SELECT * FROM results_data ORDER BY {sort_by} DESC LIMIT {max_results}"
        )
        .to_df()
        .to_markdown(index=False)
    )


async def search(
    query: str, language, max_results, sort_by, categories, safesearch
) -> Any:
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

    yield "Searching... wait..."
    # Perform the search on internet web using SearXNG
    results = await _searxng.async_search(
        query,
        method="GET",
        categories=categories,
        language=language,
        safesearch=int(safesearch),
    )

    yield await _format_table(results, max_results, sort_by, category=categories[0])
