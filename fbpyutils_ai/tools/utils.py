"""Utility functions for API parameter discovery."""

from typing import Dict
from fbpyutils_ai.tools.http import HTTPClient
import time

def discover_api_params(
    url: str,
    method: str,
    headers: Dict,
    working_payload: Dict,
    full_payload: Dict
) -> Dict:
    """Discover valid API parameters by testing payload combinations.

    Args:
        url (str): Target API endpoint URL
        method (str): HTTP method (GET/POST/PUT/etc)
        headers (Dict): Request headers
        working_payload (Dict): Base payload with known valid parameters
        full_payload (Dict): Full set of parameters to test

    Returns:
        Dict: Dictionary of parameters that resulted in successful responses
    """
    if method not in ("GET", "POST"):
        raise ValueError("Only GET and POST methods are supported")

    working_params = working_payload.copy()
    client = HTTPClient(url, headers=headers)

    for key, value in full_payload.items():
        test_payload = {**working_params, key: value}
        if method == "POST":
            response = client.sync_request(
                method=method,
                url=url,
                json=test_payload
            )
        else:
            response = client.sync_request(
                method=method,
                url=url,
                params=test_payload
            )

        if 200 <= response.status_code < 300:
            working_params[key] = value

        time.sleep(3)

    return working_params
