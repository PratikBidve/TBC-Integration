import logging
import httpx
from app.dependencies.shopify_auth import get_shopify_client

logger = logging.getLogger(__name__)

shopify_client = get_shopify_client()

async def publish_collection_to_online_store(collection_id):
    base_url = shopify_client['base_url']
    token = shopify_client['token']

    # Prepare the headers
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': token
    }

    # Prepare the GraphQL mutation to publish the collection
    # This is a conceptual example and might need adjustments based on the Shopify API's requirements
    mutation = """
    mutation collectionPublish($input: CollectionPublishInput!) {
      collectionPublish(input: $input) {
        collection {
          id
          title
        }
        userErrors {
          field
          message
        }
      }
    }
    """

    # Prepare the variables for the mutation
    # Adjust the 'collectionPublications' field with the actual data
    variables = {
        "input": {
            "id": collection_id,
            "collectionPublications": [
                {
                    "publicationId": "gid://shopify/Publication/76389646421"
                },
                {
                    "publicationId": "gid://shopify/Publication/154790887755"
                },
                {
                    "publicationId": "gid://shopify/Publication/168735539531"
                },

            ]
        }
    }

    logger.info(f"Publishing collection with ID {collection_id} to the online store.")

    try:
        # Make the POST request using httpx.AsyncClient
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{base_url}/graphql.json',
                headers=headers,
                json={
                    'query': mutation,
                    'variables': variables
                }
            )
            response_data = response.json()

            if response.status_code != 200:
                logger.error(f"Failed to publish collection with ID {collection_id} to the online store: {response_data}")
                return None, response_data
            else:
                result = response_data.get('data', {}).get('collectionPublish', {})
                if result.get('collection'):
                    logger.info(f"Successfully published collection with ID {collection_id} to the online store.")
                    return result['collection'], None
                else:
                    # Log the entire response body for debugging
                    logger.error(f"Failed to publish collection with ID {collection_id} to the online store. Response: {response_data}")
                    return None, result.get('userErrors', [])
    except Exception as e:
        logger.error(f"An exception occurred while publishing collection with ID {collection_id} to the online store: {e}")
        return None, str(e)