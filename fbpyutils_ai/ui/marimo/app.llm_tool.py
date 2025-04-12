import marimo

__generated_with = "0.11.8"
app = marimo.App(
    width="medium",
    app_title="LiteLLM Inspector",
    auto_download=["ipynb"],
)


@app.cell
def _(llm_model_details, mo, selected_model_ui, selected_provider_ui):
    mo.md(f'''
        - {selected_provider_ui}
        - {selected_model_ui}
        ```
        {mo.json(llm_model_details)}
        ```
    ''')
    return


@app.cell
def _(llm_endpoints, mo):
    selected_provider_ui = mo.ui.dropdown(
        options=[e['provider'] for e in llm_endpoints], 
        label='Select a provider',
    )
    return (selected_provider_ui,)


@app.cell
def _(llm_models, mo):
    selected_model_ui = mo.ui.dropdown(
        options=llm_models, 
        label='Select a model',
    )
    return (selected_model_ui,)


@app.cell
def _(llm_endpoints, selected_provider_ui):
    if selected_provider_ui.value is not None:
        selected_provider = { p['provider']: p for p in llm_endpoints}[selected_provider_ui.value]
    else:
        selected_provider = None
    return (selected_provider,)


@app.cell
def _(selected_model_ui):
    if selected_model_ui.value is not None:
        selected_model = selected_model_ui.value
    else:
        selected_model = None
    return (selected_model,)


@app.cell
def _(json, os, pd):
    prompt_path = os.path.sep.join(
        ["fbpyutils_ai", "tools", "llm", "resources", "llm_introspection_prompt.md"]
    )
    schema_path = os.path.sep.join(
        [
            "fbpyutils_ai",
            "tools",
            "llm",
            "resources",
            "llm_introspection_validation_schema.json",
        ]
    )
    endpoints_path = os.path.sep.join(
        [
            "fbpyutils_ai",
            "tools",
            "llm",
            "resources",
            "llm_endpoints.md",
        ]
    )

    with open(prompt_path, "r", encoding="utf-8") as f:
        llm_introspection_prompt = f.read()
    with open(schema_path, "r", encoding="utf-8") as f:
        llm_introspection_validation_schema = json.load(f)
    with open(endpoints_path, "r", encoding="utf-8") as f:
        llm_endpoints_raw = f.read()
        indexes = [0, *range(2, len(llm_endpoints_raw.split("\n")))]

        def _strip(x: str) -> str:
            while '  ' in x:
                x = x.replace('  ', '')
            return x.strip()

        parts = llm_endpoints_raw.replace(
            "-|-", ";"
        ).replace(
            " | ", ";"
        ).replace(
            "| ", ""
        ).replace(
            "| ", ""
        ).replace(
            " |", ""
        ).replace(
            "|", ""
        ).split("\n")

        endpoints = [_strip(e).split(";") for e in 
            [parts[i] for i in indexes if parts[i]]
        ]

        llm_endpoints = [
            e for e in pd.DataFrame(
                [
                    [d.strip() for d in p] for p in endpoints[1:]
                ], columns=[h.lower().replace(' ', '_').strip() 
                for h in endpoints[0]]
            ).to_dict(orient="records") if e['selected'] == 'True'
        ]

    llm_common_params = [
        "temperature",
        "max_tokens",  
        "top_p",
        "stream",  
        "stream_options",  
        "tool_choice",
    ]
    return (
        endpoints,
        endpoints_path,
        f,
        indexes,
        llm_common_params,
        llm_endpoints,
        llm_endpoints_raw,
        llm_introspection_prompt,
        llm_introspection_validation_schema,
        parts,
        prompt_path,
        schema_path,
    )


@app.cell
def _(LLMServiceTool, os, selected_provider):
    provider, base_url, env_api_key = None, None, None

    if selected_provider:
        provider, base_url, env_api_key, selected = selected_provider.values()

        llm = LLMServiceTool(
            model_id="None",
            api_key=os.environ[env_api_key],
            api_base=base_url,
            timeout=3000,
            session_retries=1,
        )

        llm_models = [m["id"] for m in llm.list_models()]
        llm_models.sort()
    else:
        llm_models = []
    return base_url, env_api_key, llm, llm_models, provider, selected


@app.cell
def _(
    Exeption,
    ValidationError,
    base_url,
    env_api_key,
    get_supported_openai_params,
    json,
    litellm,
    llm_common_params,
    llm_introspection_prompt,
    llm_introspection_validation_schema,
    os,
    print,
    provider,
    selected_model_ui,
    validate,
):
    if not all([provider, base_url, env_api_key]) or not selected_model_ui.value:
        llm_model_details = {}
    else:
        messages = [
            {"role": "system", "content": llm_introspection_prompt},
            {"role": "user", "content": "Please list me ALL the details about this model."},
        ]

        api_provider = provider.lower()
        api_base = base_url
        api_key = os.environ[env_api_key]
        model_id = selected_model_ui.value

        # response_format = None
        if api_provider == "lm_studio":
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": "llm_introspection_validation_schema",
                    "strict": "true",
                    "schema": llm_introspection_validation_schema,
                    "required": ["llm_introspection_validation_schema"]
                }
            }
        else:
            response_format = {
                "type": "json_schema",
                "schema": llm_introspection_validation_schema,
                "strict": True,
            }

        try: 
            litellm.debug = False
            response = litellm.completion(
                model=f"{api_provider}/{model_id}",
                messages=messages,
                api_base=api_base,
                api_key=api_key,
                timeout=3000,
                max_retries=3,
                top_p=1,
                temperature=0.0,
                stream=False,
                response_format=None,
            )

            contents = response.get('choices',[{}])[0].get('message', {}).get('content')

            if contents:
                llm_model_details = json.loads(contents.replace("```json", "").replace("```", ""))
            else:
                print("No content found in the response.")
                llm_model_details = {}

            try:
                llm_model_details = json.loads(contents.replace("```json", "").replace("```", ""))
                try:
                    validate(instance=llm_model_details, schema=llm_introspection_validation_schema)

                    supported_params = get_supported_openai_params(
                        model=model_id, custom_llm_provider=api_provider
                    ) or llm_common_params
                    llm_model_details['supported_ai_parameters'] = supported_params 

                    llm_model_details['model_id'] = model_id
                except ValidationError as e:
                    raise Exception(f"JSON Validation error: {e}")
            except json.JSONDecodeError as e:
                raise Exeption(f"Error decoding JSON: {e}")
        except Exception as e:
            llm_model_details = {
                "error": str(e),
                "message": "An error occurred while fetching model details.",
            }
    return (
        api_base,
        api_key,
        api_provider,
        contents,
        llm_model_details,
        messages,
        model_id,
        response,
        response_format,
        supported_params,
    )


@app.cell
def _():
    import os
    from dotenv import load_dotenv

    _ = load_dotenv()

    import json
    import pandas as pd

    from time import sleep
    from rich import print
    from jsonschema import validate, ValidationError

    from fbpyutils_ai import logging, log_dir
    from fbpyutils_ai.tools.llm import LLMServiceTool
    return (
        LLMServiceTool,
        ValidationError,
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
