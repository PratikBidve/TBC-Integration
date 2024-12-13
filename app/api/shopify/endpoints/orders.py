from fastapi import APIRouter
import logging
import httpx
from app.dependencies.shopify_auth import get_shopify_client

router = APIRouter()

logger = logging.getLogger(__name__)

shopify_client = get_shopify_client()

def create_shopify_draft_order(deal_data, variant_ids):
    metafields = [
        {
            "namespace": "custom",
            "key": "payment_Condition",
            "value": deal_data['payment_condition'],
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "order_status",
            "value": 'Design',
            "type": "single_line_text_field"
        }
    ]
    base_url = shopify_client['base_url']
    token = shopify_client['token']

    # Prepare the headers
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': token
    }

    # Prepare the GraphQL mutation
    mutation = """
    mutation createDraftOrderMetafields($input: DraftOrderInput!) {
      draftOrderCreate(input: $input) {
        draftOrder {
          id
          metafields(first: 3) {
            edges {
              node {
                id
                namespace
                key
                value
              }
            }
          }
        }
        userErrors {
          message
          field
        }
      }
    }
    """

    # Prepare the line items using the list of variant IDs
    line_items = [{"variantId": item['variantId'], "quantity": int(item['quantity'])} for item in variant_ids]

    # Prepare the applied discount
    applied_discount = {
        "description": "Order Discount",
        "value": deal_data['discount_percentage'],
        "valueType": "PERCENTAGE",
        "title": "Order Discount"
    }

    # logger.info(f"GraphQL mutation for draft order: {mutation}")
    logger.info(f"GraphQL line items for draft order: {line_items}")
    logger.info(f"GraphQL applied discount for draft order: {applied_discount}")
    logger.info(f"GraphQL metafields for draft order: {metafields}")
    # logger.info(f"GraphQL headers for draft order: {headers}")
    # logger.info(f"GraphQL base URL for draft order: {base_url}")
    # logger.info(f"GraphQL deal data for draft order: {deal_data}")
    logger.info(f"GraphQL variant IDs for draft order: {variant_ids}")
    
    
    variables = {
        "input": {
            "customerId": deal_data['customer_id'],
            "note": deal_data['dealname'],
            "email": deal_data['email'],
            "phone": deal_data['phone'],
            "taxExempt": True,
            "tags": f"HubspotCompanyId-{deal_data['company_id']}",
            "shippingLine": {
                "title": deal_data['dealname']
            },
            "shippingAddress": {
                "address1": deal_data['delivery_address'],
                "city": deal_data['delivery_city'],
                "province": "",
                "country": deal_data['delivery_country'],
                "zip": deal_data['delivery_zip']
            },
            "billingAddress": {
                "address1": deal_data['billing_address'],
                "city": deal_data['billing_city'],
                "province": "",
                "country": deal_data['billing_country'],
                "zip": deal_data['billing_postal_code']
            },
            "appliedDiscount": applied_discount,
            "lineItems": line_items,
            "metafields": metafields
        }
    }

    logger.info(f"GraphQL variables for draft order: {variables}")

    try:
        # Make the POST request using httpx.Client instead of httpx.AsyncClient
        with httpx.Client() as client:
            response = client.post(
                f'{base_url}/graphql.json',
                headers=headers,
                json={
                    'query': mutation,
                    'variables': variables
                }
            )
            logger.info(f"GraphQL response for draft order: {response.json()}")

            if response.status_code != 200:
                logger.error(f"Shopify draft order creation failed with status code {response.status_code}: {response.json()}")
                return None, response.json()
            else:
                result = response.json()
                if result['data']['draftOrderCreate']['userErrors']:
                    logger.error(f"Shopify draft order creation failed: {result['data']['draftOrderCreate']['userErrors']}")
                    return None, result['data']['draftOrderCreate']['userErrors']
                else:
                    draft_order_id = result['data']['draftOrderCreate']['draftOrder']['id']
                    logger.info(f"Successfully created Shopify draft order with ID: {draft_order_id}")
                    return draft_order_id, None
    except Exception as e:
        logger.error(f"An exception occurred while creating Shopify draft order: {e}")
        return None, str(e)