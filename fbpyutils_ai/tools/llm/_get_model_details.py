import json
from typing import Any, Dict

from jsonschema import ValidationError, validate
from fbpyutils_ai import logging
import litellm
from litellm import get_supported_openai_params

from fbpyutils_ai.tools.llm._utils import get_llm_resources
from ._list_models import _get_api_model_response


litellm.logging = logging
litellm.drop_params = True

(
    LLM_PROVIDERS,       
    LLM_ENDPOINTS, 
    LLM_COMMON_PARAMS, 
    LLM_INTROSPECTION_PROMPT, 
    LLM_INTROSPECTION_VALIDATION_SCHEMA
) = get_llm_resources()


def get_model_details(
    provider: str, 
    api_base_url: str, 
    api_key: str, 
    model_id: str, 
    introspection: bool = False,
    retries: int = 3,
    **kwargs: Any,
) -> Dict[str, Any]:
    if not all([provider, api_base_url, api_key]):
        raise ValueError("provider, api_base_ur, and api_key must be provided.")
        
    retries = retries or 3
    kwargs['timeout'] = kwargs.get("timeout", 300)
    api_provider = provider.lower()
    response_data = {}
    try:
        url = f"{api_base_url}/models/{model_id}"

        if provider.lower() == "openrouter":
            url += "/endpoints"
        
        logging.info(f"Fetching model details from: {url}")
        response_data = _get_api_model_response(url, api_key, **kwargs)

        if introspection:
            messages = [
                {"role": "system", "content": LLM_INTROSPECTION_PROMPT},
                {"role": "user", "content": "Please list me ALL the details about this model."},
            ]

            # if api_provider == "lm_studio":
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
            try_no = 1
            while try_no <= retries:
                logging.info(f"Attempt {try_no}/{retries} to get model details.")
                response = {}
                try: 
                    response = litellm.completion(
                        model=f"{api_provider}/{model_id}",
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
                            retry_message = {
                                "role": "user",
                                "content": f"Please correct the JSON and return it again. Use this json schema to format the document: {str(LLM_INTROSPECTION_VALIDATION_SCHEMA)}. Error: {e}",
                            }
                        except json.JSONDecodeError as e:
                            logging.info(f"Error decoding JSON on attempt {try_no}: {e}. JSON: {llm_model_details}")
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
                model=model_id, custom_llm_provider=api_provider
            ) or LLM_COMMON_PARAMS
            response_data['introspection'] = llm_model_details
        return response_data
    except Exception as e:
        logging.error(
            f"Failed to retrieve model details: {e}. Response data: {response_data}"
        )
        raise
