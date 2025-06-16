import logging
from dotenv import load_dotenv
from api.auth_api import get_flip_access_token
from api.items_api import disable_sku

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    
    token = get_flip_access_token()
    if not token:
        logger.error('could not obtain access token')

    skus_to_disable = [
        "350380805BRO1V1",
        "400346909BLA1V1",
    ]
    
    disable_sku(token, skus_to_disable)