import os
import json
from typing import Any, Dict, List

from jsonschema import ValidationError, validate
from fbpyutils_ai import logging

from fbpyutils_ai.tools.llm import (
    LLMServiceTool, 
    LLM_COMMON_PARAMS,       
    LLM_PROVIDERS,    
    LLM_INTROSPECTION_PROMPT, 
    LLM_INTROSPECTION_VALIDATION_SCHEMA
)
from fbpyutils_ai.tools.llm.litellm.info import ModelPricesAndContextWindow

import litellm
from litellm import get_supported_openai_params


litellm.logging = logging
litellm.drop_params = True


_model_prices_and_context_window = ModelPricesAndContextWindow()


def list_models(api_base_url: str, api_key: str, **kwargs: Any) -> List[Dict[str, Any]]:
    try:
        selected_models = []
        llm_providers = [p for p in LLM_PROVIDERS.values() if p['base_url'] == api_base_url]
        if len(llm_providers) > 0:
            llm_provider = llm_providers[0]
            provider, api_base_url, api_key, _, is_local = llm_provider.values()

            models = LLMServiceTool.list_models(
                api_base_url,
                os.environ[api_key],
                **kwargs
            )
            llm_models = _model_prices_and_context_window \
                    .get_model_prices_and_context_window_by_provider(provider)

            for model in models:
                model_id = model['id']
                if provider == 'ollama':
                    model_id.replace(':latest', '')

                llm_model = llm_models.get(model_id)
                if not llm_model:
                    model_id = f"{provider}/{model['id']}"
                    llm_model = llm_models.get(model_id)
                if llm_model:
                    model['id'] = model_id
                    model.update(llm_model)

                if llm_model or is_local:
                    selected_models.append(model)
        return selected_models
    except Exception as e:
        raise e


def get_model_details(
    provider: str, 
    api_base_url: str, 
    api_key: str, 
    model_id: str, 
    introspection: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    if not all([provider, api_base_url, api_key]):
        raise ValueError("provider, api_base_ur, and api_key must be provided.")
        
    kwargs['timeout'] = kwargs.get("timeout", 300)
    kwargs['retries'] = kwargs.get("retries", 3)
    retries = kwargs["retries"]
    response_data = {}
    try:
        logging.info(f"Fetching default model details for: {provider}/{model_id}")

        llm_models = [m for m in list_models(
            api_base_url,
            os.environ[api_key]
        ) if m['id'] == model_id]

        if len(llm_models) == 0:
            raise ValueError(f"Model {model_id} not found")
        else:
            llm_model = llm_models[0]
            llm_provider = LLM_PROVIDERS[provider]
            llm_model.update(llm_provider)
            del llm_model['env_api_key']
            del llm_model['selected']
            del llm_model['is_local']
        response_data = llm_model

        try:
            model_prices_and_context_window = \
                ModelPricesAndContextWindow().get_model_prices_and_context_window_by_provider(provider)
        except Exception as e:
            logging.warning(f"Error getting model prices and context window: {e}")
            model_prices_and_context_window = {}
        
        response_data.update(
            model_prices_and_context_window.get(model_id, {})
        )

        if introspection:
            logging.info(f"Performing model introspection for: {model_id}")
            messages = [
                {"role": "system", "content": LLM_INTROSPECTION_PROMPT},
                {"role": "user", "content": "Please list me ALL the details about this model."},
            ]

            llm_model_supported_parameters = get_supported_openai_params(
                model=model_id, custom_llm_provider=provider
            ) or LLM_COMMON_PARAMS

            if "response_format" in llm_model_supported_parameters:
                if provider == "lm_studio":
                    response_format = {
                        "type": "json_schema",
                        "json_schema": {
                            "name": "llm_introspection_validation_schema",
                            "strict": "true",
                            "schema": LLM_INTROSPECTION_VALIDATION_SCHEMA,
                            "required": ["llm_introspection_validation_schema"]
                        }
                    }
                else:
                    response_format = {
                        "type": "json_schema",
                        "schema": LLM_INTROSPECTION_VALIDATION_SCHEMA,
                        "strict": True,
                    }
            else:
                response_format = None

            llm_model_details = {}
            introspection_report = {
                'attempts': 0,
                'generation_ok': False,
                'decode_error': False,
                'validation_error': False,
                'sanitized': False,
            }
            try_no = 1
            while try_no <= retries:
                logging.info(f"Attempt {try_no}/{retries} to get model details.")
                response = {}
                try: 
                    response = litellm.completion(
                        model=model_id,
                        messages=messages,
                        api_base_url=api_base_url,
                        api_key=api_key,
                        timeout=kwargs['timeout'],
                        top_p=1,
                        temperature=0.0,
                        stream=False,
                        response_format=response_format,
                    )

                    contents = response.get('choices',[{}])[0].get('message', {}).get('content')

                    if contents:
                        retry_message = None
                        try:
                            llm_model_details = json.loads(contents.replace("```json", "").replace("```", ""))
                            validate(instance=llm_model_details, schema=LLM_INTROSPECTION_VALIDATION_SCHEMA)
                            introspection_report['generation_ok'] = True
                            break
                        except ValidationError as e:
                            logging.info(f"JSON Validation error on attempt {try_no}: {e}. JSON: {llm_model_details}")
                            introspection_report['validation_error'] = True
                            retry_message = {
                                "role": "user",
                                "content": f"Please correct the JSON and return it again. Use this json schema to format the document: {str(LLM_INTROSPECTION_VALIDATION_SCHEMA)}. Error: {e}",
                            }
                        except json.JSONDecodeError as e:
                            logging.info(f"Error decoding JSON on attempt {try_no}: {e}. JSON: {llm_model_details}")
                            introspection_report['decode_error'] = True
                            retry_message = {
                                "role": "user",
                                "content": f"Please return a valid JSON document. Error reported: {e}",
                            }
                        try_no += 1
                        if retry_message:
                            messages.append(                                {
                                "role": "assistant",
                                "content": f"{llm_model_details}",
                            })
                            messages.append(retry_message)
                        continue
                    else:
                        logging.warning("No content found in the response.")
                        break
                except Exception as e:
                    logging.error(
                        f"An error occurred while fetching model details: {e}. JSON: {llm_model_details}"
                    )
                    raise
            llm_model_details['supported_ai_parameters'] = llm_model_supported_parameters
            introspection_report['attempts'] = try_no - 1
            response_data['introspection'] = llm_model_details
            response_data['introspection']['report'] = introspection_report
        return response_data
    except Exception as e:
        logging.error(
            f"Failed to retrieve model details: {e}. Response data: {response_data}"
        )
        raise
