import json
from typing import Any, Dict, List

from jsonschema import ValidationError, validate
from fbpyutils_ai import logging

from fbpyutils_ai.tools.llm import LLM_COMMON_PARAMS, LLM_INTROSPECTION_PROMPT, LLM_INTROSPECTION_VALIDATION_SCHEMA, LLM_PROVIDERS 
from fbpyutils_ai.tools.llm.utils import get_api_model_response
from .constants import MODEL_PRICES_AND_CONTEXT_WINDOW_BY_PROVIDER

import litellm
from litellm import get_supported_openai_params


litellm.logging = logging
litellm.drop_params = True


def list_models(api_base_url: str, api_key: str, **kwargs: Any) -> List[Dict[str, Any]]:
    return super().list_models(api_base_url, api_key, **kwargs)


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
        
    retries = retries or 3
    kwargs['timeout'] = kwargs.get("timeout", 300)
    kwargs['retries'] = kwargs.get("retries", 3)
    response_data = {}
    try:
        logging.info(f"Fetching default model details for: {provider}/{model_id}")
        response_data = super().get_model_details(provider, api_base_url, api_key, model_id, **kwargs)

        if introspection:
            logging.info(f"Performing model introspection for: {provider}/{model_id}")
            messages = [
                {"role": "system", "content": LLM_INTROSPECTION_PROMPT},
                {"role": "user", "content": "Please list me ALL the details about this model."},
            ]

            # if provider == "lm_studio":
            #     response_format = {
            #         "type": "json_schema",
            #         "json_schema": {
            #             "name": "llm_introspection_validation_schema",
            #             "strict": "true",
            #             "schema": LLM_INTROSPECTION_VALIDATION_SCHEMA,
            #             "required": ["llm_introspection_validation_schema"]
            #         }
            #     }
            # else:
            #     response_format = {
            #         "type": "json_schema",
            #         "schema": LLM_INTROSPECTION_VALIDATION_SCHEMA,
            #         "strict": True,
            #     }

            response_format = None
            llm_model_details = {}
            introspection_report = {
                'attempts': 0,
                'json_generation_success': True,
                'json_validation_success': True,
                'sanitized_json': False,
            }
            try_no = 1
            while try_no <= retries:
                logging.info(f"Attempt {try_no}/{retries} to get model details.")
                response = {}
                try: 
                    response = litellm.completion(
                        model=f"{provider}/{model_id}",
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
                            break
                        except ValidationError as e:
                            logging.info(f"JSON Validation error on attempt {try_no}: {e}. JSON: {llm_model_details}")
                            introspection_report['json_validation_success'] = False
                            retry_message = {
                                "role": "user",
                                "content": f"Please correct the JSON and return it again. Use this json schema to format the document: {str(LLM_INTROSPECTION_VALIDATION_SCHEMA)}. Error: {e}",
                            }
                        except json.JSONDecodeError as e:
                            logging.info(f"Error decoding JSON on attempt {try_no}: {e}. JSON: {llm_model_details}")
                            introspection_report['json_generation_success'] = False
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
            llm_model_details['supported_ai_parameters'] = get_supported_openai_params(
                model=model_id, custom_llm_provider=provider
            ) or LLM_COMMON_PARAMS
            introspection_report['attempts'] = try_no - 1
            response_data['introspection'] = llm_model_details
            response_data['introspection']['report'] = introspection_report
        return response_data
    except Exception as e:
        logging.error(
            f"Failed to retrieve model details: {e}. Response data: {response_data}"
        )
        raise
