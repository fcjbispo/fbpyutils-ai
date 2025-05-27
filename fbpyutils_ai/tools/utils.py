"""Utility functions for API parameter discovery."""

from typing import Dict
import httpx # Adicionado import para httpx
from fbpyutils_ai.tools.http import HTTPClient
import time
import logging # Adicionado import para logging

def discover_api_params(
    base_url: str,  # Alterado para receber a URL base
    endpoint: str,  # Alterado para receber o endpoint
    method: str,
    headers: Dict,
    working_payload: Dict,
    full_payload: Dict
) -> Dict:
    """Discover valid API parameters by testing payload combinations.

    Args:
        base_url (str): Base URL for the API
        endpoint (str): Target API endpoint relative to the base_url
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
    client = HTTPClient(base_url, headers=headers) # Inicializa com a base_url

    for key, value in full_payload.items():
        test_payload = {**working_params, key: value}
        try: # Adicionado bloco try-except
            if method == "POST":
                response = client.sync_request(
                    method=method,
                    endpoint=endpoint, # Passa o endpoint
                    json=test_payload
                )
            else:
                response = client.sync_request(
                    method=method,
                    endpoint=endpoint, # Passa o endpoint
                    params=test_payload
                )

            if 200 <= response.status_code < 300:
                working_params[key] = value

            time.sleep(3) # Movido para dentro do try

        except httpx.HTTPStatusError as e: # Captura HTTPStatusError
            if e.response.status_code == 400: # Verifica se é 400 Bad Request
                logging.warning(f"Received 400 Bad Request for key '{key}'. Skipping parameter.") # Log de aviso
                continue # Continua para o próximo parâmetro
            else:
                raise e # Relança outras exceções HTTPStatusError

    return working_params
