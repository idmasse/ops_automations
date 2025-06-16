import os
import logging
import requests
from api.auth_api import get_headers, get_flip_access_token
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

FLIP_BASE_URL = os.getenv('FLIP_BASE_URL')
FLIP_DISABLE_SKUS_PATH = os.getenv('FLIP_DISABLE_SKUS_PATH')
X_FLIPINATOR_TOOLS = os.getenv('X_FLIPINATOR_TOOLS')

def disable_sku(sku, token, audit_status="connectivity"):
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "x-flipinator-tools": X_FLIPINATOR_TOOLS
    }
    payload = {
        "skus": [sku],
        "auditStatus": audit_status
    }
    try:
        disable_skus_url = f'{FLIP_BASE_URL}{FLIP_DISABLE_SKUS_PATH}'
        response = requests.put(disable_skus_url, headers=headers, json=payload)
        response.raise_for_status()
        resp_data = response.json()
        logger.info(f"Disabled SKU {sku} with auditStatus '{audit_status}': {resp_data}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to disable SKU {sku}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status code: {e.response.status_code}")
            logger.error(f"Response content: {e.response.text}")
