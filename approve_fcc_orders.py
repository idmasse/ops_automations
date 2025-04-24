from utils.flip_auth import get_flip_access_token, get_headers
from api.flip_api import list_orders, get_order_details, approve_order
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def approve_fcc_orders():
    token = get_flip_access_token()
    if not token:
        logger.error('could not obtain access-token')
        exit(1)

    order_data = list_orders(token, page=1, limit=100) # 1. get all order data from page one
    orders = order_data.get('data', []) # 2. get just the data

    order_ids = [oid['id'] for oid in orders] # 3. get just the order IDs
    logger.info(f'found {len(order_ids)} order ids on page 1')

    #4. fetch order dtails for each order
    order_details_list = []
    for order_id in order_ids:
        try:
            order_detail = get_order_details(token, order_id)
            order_details_list.append(order_detail)
            logger.info(f'fetched details for order {order_id}')
        except Exception as e:
            logger.exception(f'failed to fetch details for order {order_id}')

    # 5. check payment method and approve credit orders
    for order_id, detail in zip(order_ids, order_details_list):
        order_obj = detail.get('order', {})
        flip_id = order_obj.get('orderID')
        pmc = order_obj.get('paymentMethodCode')
        order_state = order_obj.get('state')
        
        if pmc == 'credits' and order_state == 'pendingApproval':
            approve_order(token, order_id)
        else:
            logger.info(f"skipping order: {flip_id} / {order_id}. pmc: {pmc}, order state: {order_state}")

if __name__ == "__main__":
    approve_fcc_orders()