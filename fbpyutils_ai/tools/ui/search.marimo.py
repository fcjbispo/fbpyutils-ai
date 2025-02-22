import marimo

__generated_with = "0.11.7"
app = marimo.App(
    width="full",
    app_title="FBPyUtils for AI",
    auto_download=["ipynb"],
)


@app.cell
def _():
    return


@app.cell
def _(mo, searxng_tool_output):
    mo.accordion({
        "SearXNG Tool": searxng_tool_output
    })
    return


@app.cell
def _(
    quote_plus,
    searxng_categories,
    searxng_resuls_data,
    searxng_safe_search,
    searxng_safe_search_level,
    searxng_search_text,
    searxng_selected_categories,
    searxng_selected_language,
    searxng_show_parameters,
):
    parameters_output = f"""
    ### Parameters:
    ---
    #### search={quote_plus(searxng_search_text.value)}
    #### categories={searxng_categories}
    #### safe_search={searxng_safe_search_level}
    #### language={searxng_selected_language.value}
    """ if searxng_show_parameters.value else ""

    searxng_tool_output=f"""
    {searxng_search_text}
    ---
    {searxng_selected_categories}\n
    {searxng_selected_language}\n
    {searxng_safe_search}
    ---
    {searxng_show_parameters}
    ---
    {parameters_output}
    ### Search result:
    ---
    {searxng_resuls_data}
    """
    return parameters_output, searxng_tool_output


@app.cell
def _(
    SearXNGTool,
    SearXNGUtils,
    searxng_safe_search,
    searxng_search_text,
    searxng_selected_categories,
    searxng_selected_language,
    searxng_tool,
):
    searxng_categories = [
        SearXNGTool.CATEGORIES[indice] for indice, valor in enumerate(
            searxng_selected_categories.value
        ) if valor
    ]

    searxng_safe_search_level = [
        e[0] for e in enumerate(searxng_safe_search.options.items())
        if e[1][0] == searxng_safe_search.value
    ][0]

    if searxng_search_text.value:
        searxng_results = searxng_tool.search(
            searxng_search_text.value, categories=searxng_categories, language=searxng_selected_language.value,safesearch=searxng_safe_search_level
        )
    else:
        searxng_results = []

    import pandas as pd
    # searxng_results_data = pd.DataFrame([])
    searxng_resuls_data = SearXNGUtils.convert_to_dataframe(searxng_results)
    return (
        pd,
        searxng_categories,
        searxng_resuls_data,
        searxng_results,
        searxng_safe_search_level,
    )


@app.cell
def _(SearXNGTool, mo):
    searxng_tool = SearXNGTool()

    searxng_selected_categories = mo.ui.array([
        mo.ui.switch(
            value=(c == 'general'),
            label=c
        ) for c in SearXNGTool.CATEGORIES
    ], label='Select categories to search on:')

    searxng_safe_search = mo.ui.radio(
        options=['None', 'Moderate', 'Strict'], 
        value='None', label='Safe search level:')

    searxng_selected_language = mo.ui.dropdown(
        options=SearXNGTool.LANGUAGES,
        label='Select languages to search in:',
        value='auto'
    )

    searxng_show_parameters = mo.ui.switch(
        value=True,
        label='Show search parameters'
    )

    searxng_search_text = mo.ui.text_area(
        placeholder="Enter an expression to search for...",
        max_length=None,
        rows=3,
        label="Search expression:",
        full_width=True
    )
    return (
        searxng_safe_search,
        searxng_search_text,
        searxng_selected_categories,
        searxng_selected_language,
        searxng_show_parameters,
        searxng_tool,
    )


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import json
    from rich import print
    from dotenv import load_dotenv
    from urllib.parse import quote_plus
    from fbpyutils_ai.tools.search import SearXNGTool, SearXNGUtils
    load_dotenv()
    return SearXNGTool, SearXNGUtils, json, load_dotenv, print, quote_plus


if __name__ == "__main__":
    app.run()
