import json
import os

import pandas as pd

from fbpyutils_ai.tools import LLMServiceModel


def get_llm_model(provider_id: str, model_id: str, llm_endpoints: list[dict]) -> LLMServiceModel:
    llm_provider = [p for p in llm_endpoints if p['provider'] == provider_id]
    if llm_provider:
        llm_model = LLMServiceModel(
            provider=provider_id,
            api_base_url=os.environ.get(
                f'{provider_id.upper()}_API_BASE_URL',
                llm_provider[0]['api_base_url']
            ),
            api_key=os.environ.get(llm_provider[0]['env_api_key']),
            model_id=model_id,
        )
        return llm_model


def get_llm_resources():
    def _strip(x: str) -> str:
        while '  ' in x:
            x = x.replace('  ', '')
        return x.strip()

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
            ], columns=[h.lower().strip().replace(' ', '_').strip() 
            for h in endpoints[0]]
        ).to_dict(orient="records") if e['selected'] == 'True'
    ]

    llm_providers = list(set([
        l['provider'] for l in llm_endpoints
    ]))

    llm_common_params = [
        "temperature",
        "max_tokens",  
        "top_p",
        "stream",  
        "stream_options",  
        "tool_choice",
    ]

    return (
        llm_providers,
        {l['provider']: l for l in llm_endpoints},
        llm_common_params,
        llm_introspection_prompt,
        llm_introspection_validation_schema,
    )
