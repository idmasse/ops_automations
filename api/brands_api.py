import os
import logging
import requests
import time
import json
from utils.flip_auth import get_headers, get_flip_access_token
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FLIP_BASE_URL = os.getenv('FLIP_BASE_URL')
CREATE_BRAND_PATH = '/shop/admin/brands/onboarding/outbound/v1'
GET_ALL_BRANDS_PATH = '/shop/admin/brands/onboarding/list/v2'
UPDATE_PROFILE_PATH = '/shop/admin/brands/onboarding/update/v1'
PREAPPROVE_BRAND_PATH = '/shop/admin/brands/onboarding/{brand_id}/start-onboarding/v1'
ASSIGN_BRAND_PATH = '/shop/admin/brands/onboarding/{brand_id}/call/onboarding-assign/v1'
UPDATE_CS_EMAIL_PATH = '/shop/brands/management/request-customer-support-email-change/v1'

# /shop/admin/brands/onboarding/update/v1
def update_return_addr(brand_id, token, retry=True):
    url = f'{FLIP_BASE_URL}{UPDATE_PROFILE_PATH}'
    headers = get_headers(token)
    payload = {
        'id': brand_id,
        'operationData': {
            'orderReturnDCAddress': {
                'receiverName': 'DS Flip Returns',
                'city': 'Corona',
                'street': '1235 Quarry St',
                'postalCode': '92879'
            },
        'isShippingOriginAddressSameAsOrderReturnDCAddress': True
        }
    }
    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()
        if response.status_code in (200, 201):
            print(f'successfully processed brand: {brand_id}')
            return response.json()
        elif response.status_code == 401 and retry:
            print("Received 401. Attempting to refresh access token and retry.")
            new_token = get_flip_access_token()
            if new_token and new_token != token:
                return update_return_addr(brand_id, new_token, retry=False)
        return None
    except requests.exceptions.RequestException as e:
        print(f'error processing brand: {brand_id}: {e}')
        return None

def format_email(brand_name):
    return f"flip+{brand_name.lower().replace(' ', '')}@flipshop.com" #UPDATE THIS

# /shop/admin/brands/onboarding/outbound/v1
def create_brand(brand_name, token):
    url = f'{FLIP_BASE_URL}{CREATE_BRAND_PATH}'
    token = get_flip_access_token()  
    headers = get_headers(token)
    
    payload = {
        "name": brand_name,
        "companyName": "Company name", # UPDATE THIS
        "description": "description",
        "categoryList": ["other"],
        "foundedInYear": 2024,
        "countryOfOrigin": "United States",
        "instagramUrl": "instagram.com",
        "websiteUrl": "website.com",
        "vendorMainContactEmail": format_email(brand_name),
        "mainContactName": "First Name", # UPDATE THIS
        "sales": "from1To5mln",
        "mainContactPhone": "+18888888888",
        "genders": ["unisex"],
        "brandGoalsOnFlip": ["increaseSales"]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"Successfully processed brand: {brand_name}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error processing brand {brand_name}: {e}")
        return None

# /shop/admin/brands/onboarding/list/v2
def lookup_brand_by_name(brand_name):
    logger.info(f"Looking up brand: {brand_name}")
    
    url = f"{FLIP_BASE_URL}{GET_ALL_BRANDS_PATH}"
    payload = {
        "page": 1,
        "limit": 10,
        "name": brand_name,
        "sort": "createdAt",
        "order": "desc"
    }
    
    try:
        response = requests.post(url=url, headers=get_headers(), json=payload)
        response.raise_for_status()
        response_data = response.json()
        
        if not response_data.get('data') or len(response_data['data']) == 0:
            logger.error(f"Brand '{brand_name}' not found")
            return None
            
        brand_data = response_data['data'][0]
        logger.info(f"Found brand: {brand_data['name']} with ID: {brand_data['id']}")
        return brand_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error looking up brand '{brand_name}': {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status code: {e.response.status_code}")
            logger.error(f"Response content: {e.response.text}")
        return None

# /shop/admin/brands/onboarding/{brand_id}/start-onboarding/v1
def pre_approve_brand(brand_id):
    logger.info(f"Pre-approving brand with ID: {brand_id}")
    
    url = f"{FLIP_BASE_URL}{PREAPPROVE_BRAND_PATH}"
    payload = {
        "flipMargin": 15,
        "businessType": "dropShip",
        "relationship": "distributor"
    }
    
    try:
        response = requests.post(url=url, headers=get_headers(), json=payload)
        response.raise_for_status()
        logger.info(f"Successfully pre-approved brand with ID: {brand_id}")
        return True
    except requests.exceptions.RequestException as e:
        # Check if the error is because the brand is already approved
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 400:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('message', '').lower()
                    if 'already' in error_message or 'approved' in error_message:
                        logger.warning(f"Brand with ID '{brand_id}' is already pre-approved. Continuing with next steps.")
                        return True
                except:
                    pass
                    
        logger.error(f"Error pre-approving brand with ID '{brand_id}': {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status code: {e.response.status_code}")
            logger.error(f"Response content: {e.response.text}")
        
        # Continue with the rest of the steps even if pre-approval fails
        logger.warning(f"Continuing with next steps despite pre-approval failure for brand ID: {brand_id}")
        return True

# /shop/admin/brands/onboarding/{brand_id}/call/onboarding-assign/v1
def assign_brand_to_rep(brand_id):
    logger.info(f"Assigning brand with ID: {brand_id} to rep")
    
    url = f"{FLIP_BASE_URL}{ASSIGN_BRAND_PATH}".format()
    payload = {
        "flipOnboardingRepresentativeId": FLIP_ONBOARDING_REP_ID
    }
    
    try:
        response = requests.post(url=url, headers=get_flip_headers(), json=payload)
        response.raise_for_status()
        logger.info(f"Successfully assigned brand with ID: {brand_id} to rep")
        return True
    except requests.exceptions.RequestException as e:
        # Check if the error is because the brand already has a rep assigned
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 400:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('message', '').lower()
                    if 'already' in error_message or 'assigned' in error_message:
                        logger.warning(f"Brand with ID '{brand_id}' already has a rep assigned. Continuing with next steps.")
                        return True
                except:
                    pass
                    
        logger.error(f"Error assigning brand with ID '{brand_id}' to rep: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status code: {e.response.status_code}")
            logger.error(f"Response content: {e.response.text}")
        
        # Continue with the rest of the steps even if rep assignment fails
        logger.warning(f"Continuing with next steps despite rep assignment failure for brand ID: {brand_id}")
        return True

# /shop/brands/management/request-customer-support-email-change/v1
def update_customer_support_email(brand_id):
    logger.info(f"Updating customer support email for brand with ID: {brand_id}")
    
    url = f"{FLIP_BASE_URL}{UPDATE_CS_EMAIL_PATH}"
    payload = {
        "brandId": brand_id,
        "email": cs_email,
        "requireConfirmation": False
    }
    
    try:
        response = requests.post(url=url, headers=get_headers(), json=payload)
        response.raise_for_status()
        logger.info(f"Successfully updated customer support email for brand with ID: {brand_id}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating customer support email for brand with ID '{brand_id}': {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status code: {e.response.status_code}")
            logger.error(f"Response content: {e.response.text}")
        # Continue with the rest of the steps
        logger.warning(f"Continuing with next steps despite customer support email update failure for brand ID: {brand_id}")
        return True


def update_brand_profile(brand_id, brand_name, user_supplied_data, perplexity_data):
    """Update the brand profile with user-supplied and Perplexity data"""
    logger.info(f"Updating profile for brand with ID: {brand_id}")
    
    # Debug logging to see what we're working with
    logger.info(f"Perplexity data for {brand_name}: {json.dumps(perplexity_data)}")
    
    # Validate and fix URLs
    instagram_url = perplexity_data.get("instagramUrl", "")
    website_url = perplexity_data.get("websiteUrl", "")
    
    # Validate Instagram URL
    import re
    if not instagram_url or not re.match(r'^https?://', instagram_url):
        # Default to a standard Instagram URL if missing or invalid
        instagram_url = f"https://instagram.com/{brand_name.lower().replace(' ', '')}"
        logger.info(f"Using default Instagram URL for {brand_name}: {instagram_url}")
    
    # Validate Website URL
    if not website_url or not re.match(r'^https?://', website_url):
        # Default to a standard website URL if missing or invalid
        website_url = f"https://{brand_name.lower().replace(' ', '')}.com"
        logger.info(f"Using default website URL for {brand_name}: {website_url}")
    
    # Merge user-supplied data with Perplexity data
    payload = {
        "id": brand_id,
        "name": brand_name,
        "description": perplexity_data.get("description", ""),
        "companyName": user_supplied_data.get("companyName", ""),
        "mainContactName": user_supplied_data.get("mainContactName", ""),
        "heroTitle": perplexity_data.get("heroTitle", f"Discover {brand_name}"),
        "heroDescription": perplexity_data.get("heroDescription", f"Shop {brand_name} products"),
        "websiteUrl": website_url,
        "instagramUrl": instagram_url,
        "operationData": user_supplied_data.get("operationData", {
            "orderReturnDCAddress": {
                "city": "Commerce",
                "state": "California",
                "street": "6098 Rickenbacker Road",
                "postalCode": "90040"
            },
            "isShippingOriginAddressSameAsOrderReturnDCAddress": True,
            "vendorName": user_supplied_data.get("vendorName", ""),
            "vendorShippingEmail": user_supplied_data.get("vendorShippingEmail", ""),
            "orderShippingPromise": "within72Hrs"
        })
    }
    
    # Debug log the payload we're sending
    logger.info(f"Payload for brand profile update: {json.dumps(payload)}")
    
    url = f"{FLIP_BASE_URL}/shop/admin/brands/onboarding/update/v1"
    
    try:
        # Use PATCH method instead of POST
        response = requests.patch(url=url, headers=get_headers(), json=payload)
        response.raise_for_status()
        logger.info(f"Successfully updated profile for brand with ID: {brand_id}")
        return True
    except requests.exceptions.RequestException as e:
        # Check for specific URL validation errors
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 400:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('message', '').lower()
                    
                    # Retry with modified payload if there's a URL error
                    retry_payload = dict(payload)
                    needs_retry = False
                    
                    if 'instagramurl must be a url' in error_message:
                        logger.warning(f"Invalid Instagram URL. Setting default for {brand_name}")
                        retry_payload["instagramUrl"] = f"https://instagram.com/{brand_name.lower().replace(' ', '')}"
                        needs_retry = True
                    
                    if 'websiteurl must be a url' in error_message:
                        logger.warning(f"Invalid Website URL. Setting default for {brand_name}")
                        retry_payload["websiteUrl"] = f"https://{brand_name.lower().replace(' ', '')}.com"
                        needs_retry = True
                    
                    if needs_retry:
                        logger.info(f"Retrying profile update with fixed URLs for {brand_name}")
                        retry_response = requests.patch(url=url, headers=get_flip_headers(), json=retry_payload)
                        retry_response.raise_for_status()
                        logger.info(f"Successfully updated profile for brand with ID: {brand_id} after URL fix")
                        return True
                except Exception as retry_error:
                    logger.error(f"Error during URL fix retry: {str(retry_error)}")
            
            # Check for specific conflict error about brand already existing
            if e.response.status_code == 409:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('message', '').lower()
                    if 'conflict' in error_message and 'already exists' in error_message:
                        logger.warning(f"Brand '{brand_name}' already exists with the same business type. Continuing with next steps.")
                        return True
                except:
                    pass
        
        logger.error(f"Error updating profile for brand with ID '{brand_id}': {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status code: {e.response.status_code}")
            logger.error(f"Response content: {e.response.text}")
        return False