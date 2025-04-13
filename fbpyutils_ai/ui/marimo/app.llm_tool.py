import marimo

__generated_with = "0.11.8"
app = marimo.App(
    width="medium",
    app_title="LiteLLM Inspector",
    css_file="styles.css",
    auto_download=["ipynb"],
)


@app.cell
def _(
    base_model,
    embed_model,
    get_llm_models_cards,
    llm_app_sections,
    llm_model_request_retries,
    llm_model_request_timeout,
    mo,
    selected_base_model_ui,
    selected_embed_model_ui,
    selected_provider_ui,
    selected_vision_model_ui,
    vision_model,
):
    llm_model_cards = get_llm_models_cards(
        base_model.__dict__, 
        embed_model.__dict__, 
        vision_model.__dict__,
    )

    mo.md(f'''
        #### Select..
        - {selected_provider_ui}
        - {selected_base_model_ui}
        - {selected_embed_model_ui}
        - {selected_vision_model_ui}
        ---
        #### Set..
        - {mo.hstack([llm_model_request_timeout, mo.md(f"Current value: {llm_model_request_timeout.value}")])}
        - {mo.hstack([llm_model_request_retries, mo.md(f"Current value: {llm_model_request_retries.value}")])}
        ---
        {llm_model_cards}
        ---
        {llm_app_sections}
    ''')
    return (llm_model_cards,)


@app.cell
def _(llm_common_params):
    llm_common_params
    return


@app.cell
def _(mo):
    llm_app_sections = mo.accordion(
        {
            "Generate Text": mo.md("Nothing!"),
            "Generate Embeddings": mo.md("Nothing!"),
            "Generate Completions": mo.md("Nothing!"),
            "Describe Image": mo.md("Nothing!"),
            "Model Introspection": mo.md("Nothing!"),
        }
    )
    return (llm_app_sections,)


@app.cell
def _():
    llm_generate_text_section = None
    return (llm_generate_text_section,)


@app.cell
def _(
    LLMServiceModel,
    LLMServiceTool,
    provider,
    selected_base_model_ui,
    selected_embed_model_ui,
    selected_vision_model_ui,
):
    dummy_model = LLMServiceModel(
        provider="Undefined", 
        api_base_url="Undefined", 
        api_key="Undefined", 
        model_id="Undefined"
    )

    base_model = dummy_model if not selected_base_model_ui.value \
        else LLMServiceModel.get_llm_service_model(selected_base_model_ui.value, provider)

    embed_model = base_model if not selected_embed_model_ui.value \
        else LLMServiceModel.get_llm_service_model(selected_embed_model_ui.value, provider)

    vision_model = base_model if not selected_vision_model_ui.value \
        else LLMServiceModel.get_llm_service_model(selected_vision_model_ui.value, provider)

    if all([
        base_model != dummy_model, embed_model != dummy_model, vision_model != dummy_model
    ]):
        llm = LLMServiceTool(base_model, embed_model, vision_model)
    else:
        llm = None
    return base_model, dummy_model, embed_model, llm, vision_model


@app.cell
def _(llm_providers, mo):
    selected_provider_ui = mo.ui.dropdown(
        options=llm_providers, 
        label='A provider',
    )
    return (selected_provider_ui,)


@app.cell
def _(llm_models, mo):
    selected_base_model_ui = mo.ui.dropdown(
        options=llm_models, 
        label='The base model',
    )

    selected_embed_model_ui = mo.ui.dropdown(
        options=llm_models, 
        label='The embedding model (optional)',
    )

    selected_vision_model_ui = mo.ui.dropdown(
        options=llm_models, 
        label='The vision model (optional)',
    )

    llm_model_request_timeout = mo.ui.slider(
        start=0, 
        stop=1800, 
        step=1, 
        label="Request Timeout (seconds)", 
        value=300,
        full_width=False
    )

    llm_model_request_retries = mo.ui.slider(
        start=1, 
        stop=5, 
        step=1, 
        label="Retries", 
        value=3,
        full_width=False
    )
    return (
        llm_model_request_retries,
        llm_model_request_timeout,
        selected_base_model_ui,
        selected_embed_model_ui,
        selected_vision_model_ui,
    )


@app.cell
async def _(LLMServiceTool, llm_endpoints, mo, os, selected_provider_ui):
    async def _load_llm_models_async(api_base_url, api_key):
        llm_models = [m['id'] for m in LLMServiceTool.list_models(
            api_base_url,
            api_key
        )]
        llm_models.sort()
        return llm_models

    selected_provider = selected_provider_ui.value
    if selected_provider is None:
        provider = {}
        llm_models = []
    else:
        provider = llm_endpoints[selected_provider]
        llm_models = []
        with mo.status.spinner(title="Loading provider models...") as _spinner:
            llm_models = await _load_llm_models_async(
                api_base_url=provider['base_url'],
                api_key=os.environ.get(provider['env_api_key'])
            )
            _spinner.update("Done!")
    return llm_models, provider, selected_provider


@app.cell
async def _(get_llm_resources, mo):
    async def _get_llm_resources_async():
        return get_llm_resources()

    with mo.status.spinner(title="Loading providers...") as _spinner:
        (
            llm_providers,
            llm_endpoints,
            llm_common_params,
            llm_introspection_prompt,
            llm_introspection_validation_schema,
        ) = await _get_llm_resources_async()
    return (
        llm_common_params,
        llm_endpoints,
        llm_introspection_prompt,
        llm_introspection_validation_schema,
        llm_providers,
    )


@app.cell
def _():
    import os
    from dotenv import load_dotenv

    _ = load_dotenv()

    import json
    import asyncio
    import pandas as pd

    from time import sleep
    from rich import print
    from jsonschema import validate, ValidationError

    from fbpyutils_ai import logging, log_dir
    from fbpyutils_ai.tools.llm import (
        get_llm_resources, 
        LLMServiceTool, 
        LLMServiceModel
    )
    from fbpyutils_ai.ui.marimo.components import(
        get_llm_models_cards
    )
    return (
        LLMServiceModel,
        LLMServiceTool,
        ValidationError,
        asyncio,
        get_llm_models_cards,
        get_llm_resources,
        json,
        load_dotenv,
        log_dir,
        logging,
        os,
        pd,
        print,
        sleep,
        validate,
    )


@app.cell
def _(logging, os):
    import litellm
    from litellm import get_supported_openai_params
    litellm.logging = logging
    litellm.drop_params = True

    os.environ["LITELLM_LOG"] = os.environ.get("FBPY_LOG_LEVEL", "DEBUG").lower()
    return get_supported_openai_params, litellm


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
