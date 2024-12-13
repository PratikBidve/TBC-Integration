import logging
import httpx
from app.dependencies.shopify_auth import get_shopify_client

logger = logging.getLogger(__name__)

async def get_shopify_product_variant(product_id):
    shopify_client = get_shopify_client()
    base_url = shopify_client['base_url']
    token = shopify_client['token']

    # Prepare the headers
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': token
    }

    # Prepare the GraphQL query
    query = """
    query getProductVariant($productId: ID!) {
      product(id: $productId) {
        id
        title
        description
        variants(first: 10) {
          edges {
            node {
              id
              title
              price
              inventoryQuantity
            }
          }
        }
      }
    }
    """

    # Prepare the variables for the GraphQL query
    variables = {
        "productId": product_id
    }

    # Make the POST request using httpx
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'{base_url}/graphql.json',
            headers=headers,
            json={
                'query': query,
                'variables': variables
            }
        )

    if response.status_code != 200:
        logger.error(f"Failed to get product variant: {response.json()}")
        return None, response.json()
    else:
        result = response.json()
        if result['data']['product'] is None:
            logger.error(f"Product not found: {result['data']['product']}")
            return None, result['data']['product']
        else:
            variant_edges = result['data']['product']['variants']['edges']
            if not variant_edges:
                logger.error(f"No variants found for product ID: {product_id}")
                return None, "No variants found"
            else:
                # Assuming you want the first variant
                variant = variant_edges[0]['node']
                logger.info(f"Successfully retrieved variant for product ID: {product_id}")
                return variant, None