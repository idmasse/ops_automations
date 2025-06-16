from api.auth_api import get_flip_access_token
from api.orders_api import list_orders, get_order_details, cancel_order
from utils.gsheet_utils import get_banned_device_ids
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cancel_banned_device_id_orders():
    token = get_flip_access_token()
    if not token:
        logger.error('could not obtain access token')
        exit(1)

    orders_list = list_orders(token, page=1, limit=1000)
    orders_data = orders_list.get('data', [])

    order_ids = [oid['id'] for oid in orders_data]
    logger.info(f'found {len(order_ids)} order ids')

    order_details_list = []
    raw_banned_device_id_list = get_banned_device_ids()
    lower_banned_device_id_list = {device.strip().lower() for device in raw_banned_device_id_list}
    if not lower_banned_device_id_list:
         logger.error(f'failed to fetch banned device id list')
         exit(1)

    for order_id in order_ids:
        try:
            order_details = get_order_details(token, order_id)
            order_details_list.append(order_details)
            logger.info(f'fetched details for order: {order_id}')
        except Exception as e:
            logger.exception(f'failed to fetch details for order: {order_id}')
            continue

    for order_id, detail in zip(order_ids, order_details_list):
            order_obj = detail.get('order', {})
            order_flip_id = order_obj.get('orderID')
            device_id = order_obj.get('deviceId', '').strip().lower()

            if device_id in lower_banned_device_id_list:
                 logger.info(f'found device id: {device_id} from order {order_flip_id} / {order_id}')
                 cancelled_order = cancel_order(token, order_id)
                 if cancelled_order:
                    logger.info(f'successfully cancelled order {order_flip_id} / {order_id}')

if __name__ == '__main__':
     cancel_banned_device_id_orders()