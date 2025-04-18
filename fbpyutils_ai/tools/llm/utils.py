import json
import os

import pandas as pd

from typing import Any, Dict, List
from fbpyutils_ai.tools import LLMServiceModel
from fbpyutils_ai.tools.http import RequestsManager, basic_header
from fbpyutils_ai import logging


def get_api_model_response(url: str, api_key: str, **kwargs: Any) -> List[Dict[str, Any]]:
    headers = basic_header()
    headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    })

    if 'api.anthropic.com' in url.lower():
        headers["x-api-key"] = url
        headers["anthropic-version"] = "2023-06-01"

    kwargs['timeout'] = kwargs.get("timeout", 300)
    response_data = {}
    try:
        return RequestsManager.make_request(
            session=RequestsManager.create_session(),
            url=url,
            headers=headers,
            json_data={},
            timeout=kwargs['timeout'],
            method="GET", 
            stream=False,
        )
    except Exception as e:
        logging.error(
            f"Failed to retrieve models: {e}. Response data: {response_data}"
        )
        raise


def get_llm_model(provider_id: str, model_id: str, llm_providers: list[dict]) -> LLMServiceModel:
    llm_provider = [p for p in llm_providers if p['provider'] == provider_id]
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
            "llm_providers.md",
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

    llm_providers = {
        l['provider']: l for l in [
            e for e in pd.DataFrame(
                [
                    [d.strip() for d in p] for p in endpoints[1:]
                ], columns=[h.lower().strip().replace(' ', '_').strip() 
                for h in endpoints[0]]
            ).to_dict(orient="records") if e['selected'] == 'True'
        ]
    }

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
        llm_common_params,
        llm_introspection_prompt,
        llm_introspection_validation_schema,
    )
