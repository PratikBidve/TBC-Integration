import json
import httpx
from app.dependencies.shopify_auth import get_shopify_client
import logging

logger = logging.getLogger(__name__)

shopify_client = get_shopify_client()

async def get_customer_metafields(customer_id):
    base_url = shopify_client['base_url']
    token = shopify_client['token']
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': token
    }
    query = """
    query GetCustomerMetafields($id: ID!) {
      customer(id: $id) {
        id
        metafields(first: 100) {
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
    }
    """
    variables = {"id": customer_id}
    request_body = {"query": query, "variables": variables}
    async with httpx.AsyncClient() as client:
        response = await client.post(f'{base_url}/graphql.json', headers=headers, json=request_body)
        response_json = response.json()
        if response.status_code == 200 and 'errors' not in response_json:
            return response_json['data']['customer']['metafields']['edges']
        else:
            logger.error(f"Failed to fetch customer metafields: {response_json}")
            return []

async def update_customer_metafields(customer_id, draft_orders_json):
    existing_metafields = await get_customer_metafields(customer_id)
    draft_orders_metafield = next((mf['node'] for mf in existing_metafields if mf['node']['key'] == 'draft_orders'), None)

    base_url = shopify_client['base_url']
    token = shopify_client['token']
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': token
    }

    # Ensure draft_orders_json is a JSON object, not a string
    draft_order_data = json.loads(draft_orders_json)

    if draft_orders_metafield:
        try:
            existing_data = json.loads(draft_orders_metafield['value'])
            if 'DraftOrders' in existing_data:
                # Directly append the new draft order to the existing list
                existing_data['DraftOrders'].append(draft_order_data)
            else:
                existing_data['DraftOrders'] = [draft_order_data]
            new_value = json.dumps(existing_data)
        except json.JSONDecodeError:
            logger.error("Failed to parse existing metafield value or new draft order data.")
            return None
    else:
        # If the metafield does not exist, create a new one with the provided draft order data
        new_value = json.dumps({"DraftOrders": [draft_order_data]})

    mutation = """
    mutation customerUpdate($input: CustomerInput!) {
      customerUpdate(input: $input) {
        customer {
          id
          metafields(first: 100) {
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
          field
          message
        }
      }
    }
    """
    variables = {
        "input": {
            "id": customer_id,
            "metafields": [{
                "id": draft_orders_metafield['id'] if draft_orders_metafield else None,
                "namespace": "custom",
                "key": "draft_orders",
                "value": new_value,
                "type": "json"
            }]
        }
    }
    request_body = {"query": mutation, "variables": variables}

    async with httpx.AsyncClient() as client:
        response = await client.post(f'{base_url}/graphql.json', headers=headers, json=request_body)
        if response.status_code != 200:
            logger.error(f"Shopify customer update failed with status code {response.status_code}: {response.json()}")
            return None, response.json()
        else:
            response_json = response.json()
            # Check for actual errors in the response
            if 'errors' in response_json and response_json['errors']:
                # Extract and log only the error messages, excluding extensions
                error_messages = ', '.join([error['message'] for error in response_json['errors'] if 'message' in error])
                if error_messages:
                    logger.error(f"GraphQL errors: {error_messages}")
                    return None, error_messages
            elif 'userErrors' in response_json['data']['customerUpdate'] and response_json['data']['customerUpdate']['userErrors']:
                # Log the specific error message(s) from userErrors, excluding extensions
                error_messages = ', '.join([error['message'] for error in response_json['data']['customerUpdate']['userErrors']])
                if error_messages:
                    error_message = f"Failed to update customer metafields: {error_messages}"
                    logger.error(error_message)
                    return None, error_message
            else:
                logger.info(f"Successfully updated customer metafields: {response_json}")
                return response_json, None    
