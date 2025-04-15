import marimo

__generated_with = "0.12.9"
app = marimo.App(
    width="medium",
    app_title="LiteLLM Inspector",
    css_file="styles.css",
)


@app.cell
def _(
    llm_app_sections,
    llm_model_cards,
    llm_model_details_section,
    llm_model_request_retries,
    llm_model_request_timeout,
    mo,
    selected_base_model_ui,
    selected_embed_model_ui,
    selected_provider_ui,
    selected_vision_model_ui,
):
    mo.md(f'''
        #### Select..
        - {selected_provider_ui}
        - {selected_base_model_ui}
        - {selected_embed_model_ui}
        - {selected_vision_model_ui}
        #### Set..
        - {mo.hstack([llm_model_request_timeout, mo.md(f"Current value: {llm_model_request_timeout.value}")])}
        - {mo.hstack([llm_model_request_retries, mo.md(f"Current value: {llm_model_request_retries.value}")])}
        #### Selected Models
        ---
        {llm_model_cards}
        {llm_app_sections}
        {llm_model_details_section}
    ''')
    return


@app.cell
async def _(
    LLMServiceTool,
    check_model_selection,
    llm_map,
    llm_model_details_container_full_introspection_ui,
    llm_model_details_container_model_selector_ui,
    llm_model_details_section,
    llm_model_request_timeout,
    mo,
    selected_model_details,
):
    if check_model_selection():
        llm_app_sections = mo.accordion(
            {
                "Generate Text": mo.md("Nothing!"),
                "Generate Embeddings": mo.md("Nothing!"),
                "Generate Completions": mo.md("Nothing!"),
                "Describe Image": mo.md("Nothing!"),
                "Model Details": llm_model_details_section,
            }
        )
    else:
        llm_app_sections = mo.md('')

    async def get_llm_model_details_async(
        base_type: str = 'base',
        full_introspection: bool = False,
        timeout: int = 300,
    ):
        provider, api_base, api_key, model_id = llm_map[base_type].__dict__.values()
        return LLMServiceTool.get_model_details(
            provider=provider,
            api_base_url=api_base,
            api_key=api_key,
            model_id=model_id,
            introspection=full_introspection,
            timeout=timeout
        )

    if llm_model_details_container_model_selector_ui.value is not None:
        model_id = llm_model_details_container_model_selector_ui.value
        models = [
            (llm_map[m], m) for m in llm_map.keys() 
            if llm_map[m].model_id == model_id
        ]
        if len(models) > 0:
            model, base_type = models[0]
            model_dict = model.__dict__
            selected_model_details['details'] = {
                'model_id': model_dict['model_id'],
                'api_base_url': model_dict['api_base_url'],
                'provider': model_dict['provider'],      
            }
            with mo.status.spinner(title="Loading model details...") as _spinner:
                response = await get_llm_model_details_async(
                    base_type=base_type,
                    full_introspection=llm_model_details_container_full_introspection_ui.value,
                    timeout=llm_model_request_timeout.value
                )
                _spinner.update("Done!")
            selected_model_details['details']['details'] = response
    else:
        selected_model_details['details'] = {}
    return (
        base_type,
        get_llm_model_details_async,
        llm_app_sections,
        model,
        model_dict,
        model_id,
        models,
        response,
    )


@app.cell
def _(
    json,
    llm_model_details_container_full_introspection_ui,
    llm_model_details_container_model_selector_ui,
    mo,
    selected_model_details,
):
    llm_model_details_section = mo.md(f'''
    {
        mo.hstack([
            llm_model_details_container_model_selector_ui, 
            llm_model_details_container_full_introspection_ui,
        ])
    }
    {
        mo.json(
            json.dumps(
                selected_model_details['details'],
                indent=4,
                ensure_ascii=False
            )
        )
    }
    ''')
    return (llm_model_details_section,)


@app.cell
def _(mo, selected_models):
    llm_model_details_container_model_selector_ui = mo.ui.dropdown(
        label="Selected the model:",
        options=selected_models
    )
    llm_model_details_container_full_introspection_ui = mo.ui.switch(
        label="Full Introspection", 
        value=False
    )
    return (
        llm_model_details_container_full_introspection_ui,
        llm_model_details_container_model_selector_ui,
    )


@app.cell
def _(base_model, embed_model, vision_model):
    selected_models = [
        m.model_id for m in (base_model, embed_model, vision_model,)
        if m.provider != 'Undefined'
    ]

    def check_model_selection():
        for m in (base_model, embed_model, vision_model):
            if m.provider != 'Undefined':
                return True
    return check_model_selection, selected_models


@app.cell
def _(
    LLMServiceModel,
    LLMServiceTool,
    get_llm_models_cards,
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

    llm_model_cards = get_llm_models_cards(
        base_model.__dict__, 
        embed_model.__dict__, 
        vision_model.__dict__,
    )

    llm, llm_map = None, {}
    if all([
        base_model != dummy_model, embed_model != dummy_model, vision_model != dummy_model
    ]):
        llm = LLMServiceTool(base_model, embed_model, vision_model)
        llm_map = {
            'base': base_model,
            'embed': embed_model,
            'vision': vision_model
        }
    return (
        base_model,
        dummy_model,
        embed_model,
        llm,
        llm_map,
        llm_model_cards,
        vision_model,
    )


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
def _(mo):
    def get_common_params_ui_set(
        temperature_var, top_p_var, max_tokens_var, stream_var, tool_choice_var
    ):
        return {
            "temperature": mo.ui.slider(
                start=0, 
                stop=2, 
                step=0.01, 
                label="Temperature", 
                value=temperature_var,
                full_width=False
            ),
            "top_p": mo.ui.slider(
                start=0, 
                stop=1, 
                step=0.01, 
                label="Top P", 
                value=top_p_var,
                full_width=False
            ),
            "max_tokens": mo.ui.slider(
                start=1, 
                stop=32768, 
                step=1, 
                label="Max Tokens", 
                value=max_tokens_var,
                full_width=False
            ),
            "stream": mo.ui.switch(
                label="Stream", 
                value=stream_var
            ),
            "tool_choice": mo.ui.switch(
                label="Use tools", 
                value=tool_choice_var
            ),
        }
    return (get_common_params_ui_set,)


@app.cell
async def _(LLMServiceTool, llm_endpoints, mo, os, selected_provider):
    async def load_llm_models_async(api_base_url, api_key):
        llm_models = [m['id'] for m in LLMServiceTool.list_models(
            api_base_url,
            api_key
        )]
        llm_models.sort()
        return llm_models

    if selected_provider is None:
        provider = {}
        llm_models = []
    else:
        provider = llm_endpoints[selected_provider]
        llm_models = []
        with mo.status.spinner(title="Loading provider models...") as _spinner:
            llm_models = await load_llm_models_async(
                api_base_url=provider['base_url'],
                api_key=os.environ.get(provider['env_api_key'])
            )
            _spinner.update("Done!")
    return llm_models, load_llm_models_async, provider


@app.cell
def _(selected_provider_ui):
    selected_provider = selected_provider_ui.value
    selected_model_details = {
        'details': {}
    }
    return selected_model_details, selected_provider


@app.cell
def _(llm_providers, mo):
    selected_provider_ui = mo.ui.dropdown(
        options=llm_providers, 
        label='A provider',
    )
    return (selected_provider_ui,)


@app.cell
async def _(get_llm_resources_async, mo):
    with mo.status.spinner(title="Loading providers...") as _spinner:
        (
            llm_providers,
            llm_endpoints,
            llm_common_params,
            llm_introspection_prompt,
            llm_introspection_validation_schema,
        ) = await get_llm_resources_async()
    return (
        llm_common_params,
        llm_endpoints,
        llm_introspection_prompt,
        llm_introspection_validation_schema,
        llm_providers,
    )


@app.cell
def _(get_llm_resources):
    async def get_llm_resources_async():
        return get_llm_resources()
    return (get_llm_resources_async,)


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

    import litellm
    from litellm import get_supported_openai_params

    import marimo as mo

    litellm.logging = logging
    litellm.drop_params = True

    os.environ["LITELLM_LOG"] = os.environ.get("FBPY_LOG_LEVEL", "DEBUG").lower()
    return (
        LLMServiceModel,
        LLMServiceTool,
        ValidationError,
        asyncio,
        get_llm_models_cards,
        get_llm_resources,
        get_supported_openai_params,
        json,
        litellm,
        load_dotenv,
        log_dir,
        logging,
        mo,
        os,
        pd,
        print,
        sleep,
        validate,
    )


if __name__ == "__main__":
    app.run()
