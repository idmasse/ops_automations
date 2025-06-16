import os
import logging
import time
from api.brands_api import update_return_addr
from api.auth_api import get_flip_access_token
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    token = get_flip_access_token()
    if not token:
        print('failed to retrieve access token')
        return

    brand_ids = [
        "68017c906433cdb7fb57e471",
        "68013af046ae3dcf22c6ba81"
    ]

    results = {}
    for brand_id in brand_ids:
        print(f'\nprocessing brand: {brand_id}')
        result = update_return_addr(brand_id, token)
        results[brand_id] = result
        time.sleep(1)
    return results

if __name__ == '__main__':
    print('Starting address updates...')
    main()