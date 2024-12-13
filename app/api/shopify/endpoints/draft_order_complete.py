from fastapi import APIRouter
import logging
import httpx
from app.dependencies.shopify_auth import get_shopify_client

router = APIRouter()

logger = logging.getLogger(__name__)

def complete_draft_order(draft_order_id, payment_pending, deal_data):
    # Get the Shopify client
    shopify_client = get_shopify_client()
    base_url = shopify_client['base_url']
    token = shopify_client['token']

    # Prepare the headers
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': token
    }

    # Prepare the GraphQL mutation to complete the draft order
    mutation = """
    mutation draftOrderComplete($id: ID!, $paymentPending: Boolean) {
      draftOrderComplete(id: $id, paymentPending: $paymentPending) {
        draftOrder {
          id
          order {
            id
          }
        }
      }
    }
    """

    # Prepare the variables for the GraphQL mutation
    variables = {
        "id": draft_order_id,
        "paymentPending": payment_pending
    }

    # Make the POST request using httpx to complete the draft order
    with httpx.Client() as client:
        response = client.post(
            f'{base_url}/graphql.json',
            headers=headers,
            json={
                'query': mutation,
                'variables': variables
            }
        )

    if response.status_code != 200:
        logger.error(f"Failed to complete draft order: {response.json()}")
        return None, response.json()
    else:
        result = response.json()
        if result['data']['draftOrderComplete']['draftOrder'] is None:
            logger.error(f"Draft order not found or failed to complete: {result['data']['draftOrderComplete']}")
            return None, result['data']['draftOrderComplete']
        else:
            order_id = result['data']['draftOrderComplete']['draftOrder']['order']['id']
            logger.info(f"Successfully completed draft order with ID {draft_order_id}. Order ID: {order_id}")

            # Prepare the GraphQL mutation to update the order with metafields
            update_order_mutation = """
            mutation orderUpdate($input: OrderInput!) {
             orderUpdate(input: $input) {
                order {
                 id
                 metafields(first: 5) {
                    edges {
                      node {
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

            # Prepare the variables for the GraphQL mutation to update the order with metafields
            update_order_variables = {
                "input": {
                    "id": order_id,
                    "metafields": [
                        {
                            "namespace": "custom",
                            "key": "order_status",
                            "value": 'Design'
                        },
                        {
                            "namespace": "custom",
                            "key": "payment_Condition",
                            "value": str(deal_data['payment_condition']),
                            "type": "single_line_text_field"
                        },
                        {
                            "namespace": "custom",
                            "key": "HS_Deal_ID",
                            "value": str(deal_data['HS_Deal_ID']),
                            "type": "single_line_text_field"
                        },
                    ]
                }
            }

            # Make the POST request using httpx to update the order with metafields
            with httpx.Client() as client:
                response = client.post(
                    f'{base_url}/graphql.json',
                    headers=headers,
                    json={
                        'query': update_order_mutation,
                        'variables': update_order_variables
                    }
                )

            # Handle the response for the metafield update
            if response.status_code != 200:
                logger.error(f"Failed to update order with metafields: {response.json()}")
            else:
                result = response.json()
                logger.info(f"Metafield update response: {result}")  # Log the entire response
                logger.info(f"Successfully updated order {order_id} with metafields.")
                return order_id, None