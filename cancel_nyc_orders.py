from utils.flip_auth import get_flip_access_token
from api.flip_api import list_orders, get_order_details, cancel_order
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KEYWORDS = {
    "creatine","green","tea","raspberry","ketone","garcinia",
    "cambogia","coffee","bean","extract","whey","protein","muscular"
}

def cancel_nyc_banned_ingredients():
    token = get_flip_access_token()
    if not token:
        logger.error('could not obtain access token')
        exit(1)

    order_data = list_orders(token, page=1, limit=500, states=['OOSItem','giftPending','stylistApproval','readyToShip'])
    orders = order_data.get('data', [])

    order_ids = [oid['id'] for oid in orders]
    
    order_details_list = []
    for order_id in order_ids:
        order_detail = get_order_details(token, order_id)
        order_details_list.append(order_detail)
        logger.info(f'fetched details for order: {order_id}')

    for order_id, detail in zip(order_ids, order_details_list):
        order = detail.get("order", {})

        # top‐level order fields
        order_flip_id   = order.get("orderID")
        order_state     = order.get("state")
        order_tag       = order.get("tag")
        order_status    = order.get("orderStatus")

        # shipping address state
        shipping_state  = order.get("shippingAddress", {}).get("state")

        # order items
        for line in order.get("items", []):
            item_data           = line.get("item", {})
            item_category       = item_data.get("category")
            item_title          = item_data.get("description")
            title_lower         = item_title.lower()
            item_long_desc      = item_data.get("long_description", "")
            desc_lower          = item_long_desc.lower()
            
            if (
        order_state in {"OOSItem", "giftPending", "stylistApproval", "readyToShip"}
        and order_tag not in {"payment-in-review", "test"}
        and shipping_state == "New York"
        and item_category == "Vitamins & Supplements"
        and order_status != "cancelled"
        and any((keyword in desc_lower) or (keyword in title_lower) for keyword in KEYWORDS)
    ):
                logger.info(f'cancelling order {order_flip_id} / {order_id}')
                cancel_order(token, order_id)
                break

if __name__ == "__main__":
    cancel_nyc_banned_ingredients()