from typing import Any, Dict, List
from fbpyutils_ai import logging
import litellm

from fbpyutils_ai.tools.http import RequestsManager, basic_header

litellm.logging = logging
litellm.drop_params = True


def _get_api_model_response(url: str, api_key: str, **kwargs: Any) -> List[Dict[str, Any]]:
    headers = basic_header()
    headers.update({
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    })

    if 'api.anthropic.com' in url.lower():
        headers["x-api-key"] = url
        headers["anthropic-version"] = "2023-06-01"

    timeout = kwargs.get("timeout", 30000)
    response_data = {}
    try:
        response = RequestsManager.make_request(
            session=RequestsManager.create_session(),
            url=url,
            headers=headers,
            json_data={},
            timeout=timeout,
            method="GET", 
            stream=False,
        )
        models_data = response

        # Parse and structure the model metadata
        if not url.endswith("/models"):
            return models_data

        models = []
        if "data" in models_data:
            models_data = models_data.get("data", [])
        for model in models_data:
            models.append(model)

        return models
    except Exception as e:
        logging.error(
            f"Failed to retrieve models: {e}. Response data: {response_data}"
        )
        raise

def list_models(api_base_url: str, api_key: str, **kwargs: Any) -> List[Dict[str, Any]]:
    if not all([api_base_url, api_key]):
        raise ValueError("api_base_ur and api_key must be provided.")

    url = f"{api_base_url}/models"
    return _get_api_model_response(url, api_key, **kwargs)
