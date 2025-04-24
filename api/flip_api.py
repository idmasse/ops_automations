import os
import logging
import requests
import urllib.parse
from utils.flip_auth import get_headers
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FLIP_BASE_URL = os.getenv('FLIP_BASE_URL')
ORDER_LIST_PATH = '/api/v2/order/list'
ORDER_DETAIL_PATH = '/api/order/{order_id}'
APPROVE_ORDER_PATH = '/shop/admin/orders/{order_id}/accept-order-in-pending-approval-state/v1'
FLIP_CANCEL_ORDERS_PATH = '/shop/admin/orders/{order_id}/cancel/v1'
ORDER_STATES = [
            "new","inStyling","activeStyling","OOSItem","OOSItemActive",
            "stylistApproval","needAttention","OPS","OPSFailed","OPSProcessing",
            "readyToShip","pendingPick","shipped","withCustomer","pendingPickup",
            "pendingDropOff","pickupMissed","inTransit","inboundTransit",
            "outboundTransit","backInOPS","returnConfirmed","returnConfirmedFailed",
            "completed","cancelled","paymentInReview","revisionFailed","pendingApproval"
            ]

def list_orders(token, page=1, limit=100, states=None):

    if states is None:
        states = ORDER_STATES

    url = f'{FLIP_BASE_URL}{ORDER_LIST_PATH}'
    params = {
        "page": page,
        "limit": limit,
        "state": ",".join(states)
    }

    full_url = f'{url}?{urllib.parse.urlencode(params)}' #confim params are working
    logger.info(f'calling list_orders url: {full_url}')

    headers = get_headers(token)
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_order_details(token, order_id):  
    url = f'{FLIP_BASE_URL}{ORDER_DETAIL_PATH}'.format(order_id=order_id)
    headers = get_headers(token)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def approve_order(token, order_id):
    url = f'{FLIP_BASE_URL}{APPROVE_ORDER_PATH}'.format(order_id=order_id)
    headers = get_headers(token)
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        result = response.json()
        success = result.get('success', False)
        if not success:
            logger.warning(f'order: {order_id} failed to approve: {result}')
        
        return success, result
    
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error approving {order_id}: {http_err} — {response.text}")
        return False, response.text
    except Exception as e:
        logger.exception(f"unexpected error for {order_id}: {e}")
        return False, str(e)

def cancel_order(token, order_id):
    url = f'{FLIP_BASE_URL}{FLIP_CANCEL_ORDERS_PATH}'.format(order_id=order_id)
    headers = get_headers(token)
    payload = {
        "itemsBackToCart": False,
        "reasonForCancellation": "integrationFailure",
        "shouldCancelAdditionalOrders": False
    }
    try:
        logger.info(f"attempting to cancel order id {order_id}")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        result = data.get("data", {}).get("result")
        if result == "success":
            logger.info(f"successfully cancelled order {order_id}")
        else:
            logger.error(f"cancellation failed for order {order_id}. Response: {data}")
    except requests.exceptions.RequestException as e:
        logger.error(f"error cancelling order {order_id}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"status Code: {e.response.status_code} | response: {e.response.text}")