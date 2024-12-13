import logging
import httpx
from app.dependencies.shopify_auth import get_shopify_client

logger = logging.getLogger(__name__)

shopify_client = get_shopify_client()

async def query_shopify_customer_by_email(email):
    base_url = shopify_client['base_url']
    token = shopify_client['token']

    # Prepare the headers
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': token
    }

    # Prepare the GraphQL query with the email directly included
    query = f"""
    query GetThat {{
      customers(first: 10, query: "email:{email}"){{
        edges{{
          node {{
            id # Include the customer ID in the response
            firstName
            lastName
            defaultAddress {{
              id
              address1
            }}
          }}
        }}
      }}
    }}
    """

    logger.info(f"Querying Shopify customer by email: {email}")

    try:
        # Make the POST request using httpx.AsyncClient
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{base_url}/graphql.json',
                headers=headers,
                json={'query': query}
            )
            response_json = response.json()
            logger.info(f"GraphQL response for customer query: {response_json}")

            if response.status_code != 200:
                logger.error(f"Shopify customer query failed with status code {response.status_code}: {response_json}")
                return None, response_json
            else:
                if 'errors' in response_json:
                    logger.error(f"GraphQL errors: {response_json['errors']}")
                    return None, response_json['errors']
                elif 'data' in response_json and 'customers' in response_json['data'] and 'edges' in response_json['data']['customers']:
                    try:
                        customers = [node['node'] for node in response_json['data']['customers']['edges']]
                        logger.info(f"Successfully queried Shopify customers: {customers}")
                        return customers, None
                    except Exception as e:
                        logger.error(f"Error processing customers data: {e}")
                        return None, str(e)
                else:
                    logger.info(f"No customers found with email: {email}")
                    return None, "No customers found"
    except Exception as e:
        logger.error(f"An exception occurred while querying Shopify customers: {e}")
        return None, str(e)