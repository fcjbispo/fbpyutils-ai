

import marimo

__generated_with = "0.13.3"
app = marimo.App(
    width="medium",
    app_title="FBPyUtils for AI - LLM Tool",
    css_file="styles.css",
)


@app.cell
def _(
    llm_app_sections,
    llm_model_cards,
    llm_model_request_retries,
    llm_model_request_timeout,
    mo,
    selected_base_model_ui,
    selected_embed_model_ui,
    selected_provider_ui,
    selected_vision_model_ui,
):
    mo.md(
        f"""
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
    """
    )
    return


@app.cell
def _(check_model_selection, llm_model_details_section, mo):
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
        llm_app_sections = mo.md("")
    return (llm_app_sections,)


@app.cell
async def _(
    get_llm_model_details_section,
    llm,
    llm_map,
    llm_model_details_container_full_introspection_ui,
    llm_model_details_container_model_selector_ui,
    llm_model_details_container_use_cache_ui,
    llm_model_request_retries,
    llm_model_request_timeout,
    mo,
    print,
    time,
):
    async def get_llm_model_details_async(
        base_type: str = "base",
        full_introspection: bool = False,
        retries: int = 3,
        timeout: int = 300,
    ):
        provider, api_base, api_key, is_local, model_id = llm_map[base_type].__dict__.values()
        model_details = {}
        try:
            model_details = llm.get_model_details(
                model_type=base_type,
                introspection=full_introspection,
                timeout=timeout,
            )
        except Exception as e:
            print(f"Error: {e}")
            model_details = {"error": str(e)}
        return model_details

    if llm_model_details_container_model_selector_ui.value:
        llm_model_details_response = {}
        models = [
            (llm_map[m], m)
            for m in llm_map.keys()
            if llm_map[m].model_id
            == llm_model_details_container_model_selector_ui.value
        ]
        if len(models) > 0:
            _, base_type = models[0]
            try:
                with mo.status.spinner(title="Generating model details...") as _spinner:
                    llm_model_details_response = await get_llm_model_details_async(
                        base_type=base_type,
                        full_introspection=llm_model_details_container_full_introspection_ui.value,
                        retries=llm_model_request_retries.value,
                        timeout=llm_model_request_timeout.value,
                    )
                    _spinner.update("Done!")
            except Exception as e:
                _spinner.update(f"Error: {e}")
                time.sleep(2)
                llm_model_details_response = {"Error generating model details": str(e)}
        llm_model_details_section = get_llm_model_details_section(
            llm_model_details_response,
            llm_model_details_container_model_selector_ui,
            llm_model_details_container_full_introspection_ui,
            llm_model_details_container_use_cache_ui,
        )
    else:
        llm_model_details_section = get_llm_model_details_section(
            {},
            llm_model_details_container_model_selector_ui,
            llm_model_details_container_full_introspection_ui,
            llm_model_details_container_use_cache_ui,
        )
    return (llm_model_details_section,)


@app.cell
def _(mo):
    def get_llm_model_details_section(
        llm_model_details_response: dict,
        llm_model_details_container_model_selector_ui: mo.ui.dropdown,
        llm_model_details_container_full_introspection_ui: mo.ui.switch,
        llm_model_details_container_use_cache_ui: mo.ui.switch,
    ):
        if llm_model_details_container_full_introspection_ui.value:
            return mo.md(
                    f"""
                    {
                        mo.hstack([
                            llm_model_details_container_model_selector_ui,
                            mo.vstack([
                                llm_model_details_container_full_introspection_ui, 
                                llm_model_details_container_use_cache_ui,
                            ]),
                        ])
                    }
                    {
                        mo.json(
                            llm_model_details_response
                        )
                    }
                    """
            )
        else:
            return mo.md(
                    f"""
                    {
                        mo.hstack([
                            llm_model_details_container_model_selector_ui,
                            llm_model_details_container_full_introspection_ui, 
                        ])
                    }
                    {
                        mo.json(
                            llm_model_details_response
                        )
                    }
                    """
            )
    return (get_llm_model_details_section,)


@app.cell
def _(mo, selected_models):
    llm_model_details_container_model_selector_ui = mo.ui.dropdown(
        label="Selected the model:", options=selected_models
    )

    llm_model_details_container_full_introspection_ui = mo.ui.switch(
        label="Full Introspection", value=False
    )

    llm_model_details_container_use_cache_ui = mo.ui.switch(
        label="Use Cache", value=True
    )
    return (
        llm_model_details_container_full_introspection_ui,
        llm_model_details_container_model_selector_ui,
        llm_model_details_container_use_cache_ui,
    )


@app.cell
def _(base_model, embed_model, vision_model):
    selected_models = [
        m.model_id
        for m in (
            base_model,
            embed_model,
            vision_model,
        )
        if m.provider != "Undefined"
    ]

    def check_model_selection():
        for m in (base_model, embed_model, vision_model):
            if m.provider != "Undefined":
                return True

    return check_model_selection, selected_models


@app.cell
def _(
    LLMServiceModel,
    OpenAITool,
    get_llm_models_cards,
    selected_base_model_ui,
    selected_embed_model_ui,
    selected_provider_ui,
    selected_vision_model_ui,
):
    dummy_model = LLMServiceModel(
        provider="Undefined",
        api_base_url="Undefined",
        api_key="Undefined",
        model_id="Undefined",
    )

    base_model = (
        dummy_model
        if not selected_base_model_ui.value
        else LLMServiceModel.get_llm_service_model(
            selected_base_model_ui.value, selected_provider_ui.value
        )
    )

    embed_model = (
        base_model
        if not selected_embed_model_ui.value
        else LLMServiceModel.get_llm_service_model(
            selected_embed_model_ui.value, selected_provider_ui.value
        )
    )

    vision_model = (
        base_model
        if not selected_vision_model_ui.value
        else LLMServiceModel.get_llm_service_model(
            selected_vision_model_ui.value, selected_provider_ui.value
        )
    )

    llm_model_cards = get_llm_models_cards(
        base_model.__dict__,
        embed_model.__dict__,
        vision_model.__dict__,
    )

    llm, llm_map = None, {}
    if all(
        [
            base_model != dummy_model,
            embed_model != dummy_model,
            vision_model != dummy_model,
        ]
    ):
        llm = OpenAITool(base_model, embed_model, vision_model)
        llm_map = {"base": base_model, "embed": embed_model, "vision": vision_model}
    return base_model, embed_model, llm, llm_map, llm_model_cards, vision_model


@app.cell
def _(llm_models, mo):
    selected_base_model_ui = mo.ui.dropdown(
        options=llm_models,
        label="The base model",
    )

    selected_embed_model_ui = mo.ui.dropdown(
        options=llm_models,
        label="The embedding model (optional)",
    )

    selected_vision_model_ui = mo.ui.dropdown(
        options=llm_models,
        label="The vision model (optional)",
    )

    llm_model_request_timeout = mo.ui.slider(
        start=0,
        stop=1800,
        step=1,
        label="Request Timeout (seconds)",
        value=300,
        full_width=False,
    )

    llm_model_request_retries = mo.ui.slider(
        start=1, stop=5, step=1, label="Retries", value=3, full_width=False
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
                full_width=False,
            ),
            "top_p": mo.ui.slider(
                start=0,
                stop=1,
                step=0.01,
                label="Top P",
                value=top_p_var,
                full_width=False,
            ),
            "max_tokens": mo.ui.slider(
                start=1,
                stop=32768,
                step=1,
                label="Max Tokens",
                value=max_tokens_var,
                full_width=False,
            ),
            "stream": mo.ui.switch(label="Stream", value=stream_var),
            "tool_choice": mo.ui.switch(label="Use tools", value=tool_choice_var),
        }

    return


@app.cell
async def _(OpenAITool, mo, os, selected_provider_ui, time):
    async def load_llm_models_async(api_base_url, api_key):
        llm_models = [
            m["id"] for m in OpenAITool.list_models(api_base_url, api_key)
        ]
        llm_models.sort()
        return llm_models

    if selected_provider_ui.value is None:
        llm_models = []
    else:
        llm_models = []
        with mo.status.spinner(title="Loading provider models...") as _spinner:
            try:
                llm_models = await load_llm_models_async(
                    api_base_url=selected_provider_ui.value["base_url"],
                    api_key=os.environ.get(selected_provider_ui.value["env_api_key"]),
                )
                _spinner.update("Done!")
            except Exception as e:
                _spinner.update(f"Error: {e}")
                time.sleep(2)
    return (llm_models,)


@app.cell
def _(llm_providers, mo):
    selected_provider_ui = mo.ui.dropdown(
        options=llm_providers,
        label="A provider",
    )
    return (selected_provider_ui,)


@app.cell
async def _(get_llm_resources_async, mo, time):
    with mo.status.spinner(title="Loading providers...") as _spinner:
        try:
            (
                llm_providers,
                llm_common_params,
                llm_introspection_prompt,
                llm_introspection_validation_schema,
            ) = await get_llm_resources_async()
            _spinner.update("Sorting...")
            provider_names = list(set([p for p in llm_providers]))
            provider_names.sort()
            llm_providers = {k: llm_providers[k] for k in provider_names}
            _spinner.update("Done!")
        except Exception as e:
            _spinner.update(f"Error: {e}")
            time.sleep(2)
    return (llm_providers,)


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
    import time
    import asyncio
    import pandas as pd

    from time import sleep
    from rich import print
    from jsonschema import validate, ValidationError

    from fbpyutils_ai import logging, log_dir
    from fbpyutils_ai.tools.llm import OpenAITool, LLMServiceModel
    from fbpyutils_ai.tools.llm.utils import get_llm_resources
    from fbpyutils_ai.ui.marimo.components import get_llm_models_cards

    import marimo as mo

    os.environ["LITELLM_LOG"] = os.environ.get("FBPY_LOG_LEVEL", "DEBUG").lower()
    return (
        LLMServiceModel,
        OpenAITool,
        get_llm_models_cards,
        get_llm_resources,
        mo,
        os,
        print,
        time,
    )


if __name__ == "__main__":
    app.run()
