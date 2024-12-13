import logging
import httpx
from app.dependencies.shopify_auth import get_shopify_client

logger = logging.getLogger(__name__)

def get_collection(collection_title):
    shopify_client = get_shopify_client()
    base_url = shopify_client['base_url']
    token = shopify_client['token']

    # Prepare the headers
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': token
    }

    # Prepare the GraphQL query to fetch a collection by its title
    query = f"""
    query {{
        collections(first: 1, query: "title:'{collection_title}'") {{
            edges {{
                node {{
                    id
                    title
                }}
            }}
        }}
    }}
    """

    # Make the POST request using httpx
    with httpx.Client() as client:
        response =  client.post(
            f'{base_url}/graphql.json',
            headers=headers,
            json={
                'query': query
            }
        )

    if response.status_code != 200:
        logger.error(f"Failed to get collection: {response.json()}")
        return None, response.json()
    else:
        result = response.json()
        if 'collections' in result['data'] and result['data']['collections']['edges']:
            # If the collection exists, return its ID
            return result['data']['collections']['edges'][0]['node']['id'], None
        else:
            # If the collection does not exist, create a new one
            return  create_collection(collection_title)

def create_collection(collection_title):
    shopify_client = get_shopify_client()
    base_url = shopify_client['base_url']
    token = shopify_client['token']

    # Prepare the headers
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': token
    }

    # Prepare the GraphQL mutation to create a new collection
    mutation = """
    mutation collectionCreate($input: CollectionInput!) {
      collectionCreate(input: $input) {
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

    # Prepare the variables for the GraphQL mutation
    variables = {
        "input": {
            "title": collection_title,
            "descriptionHtml": "This is a new collection",
            "templateSuffix": None,
            "image": None
        }
    }

    # Make the POST request using httpx
    with httpx.Client() as client:
        response =  client.post(
            f'{base_url}/graphql.json',
            headers=headers,
            json={
                'query': mutation,
                'variables': variables
            }
        )

    if response.status_code != 200:
        logger.error(f"Failed to create collection: {response.json()}")
        return None, response.json()
    else:
        result = response.json()
        if 'collectionCreate' in result['data'] and 'collection' in result['data']['collectionCreate']:
            # Return the ID of the newly created collection
            return result['data']['collectionCreate']['collection']['id'], None
        else:
            logger.error(f"Failed to create collection: {result}")
            return None, result

def add_product_to_collection(collection_id, product_ids):
    shopify_client = get_shopify_client()
    base_url = shopify_client['base_url']
    token = shopify_client['token']

    # Prepare the headers
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': token
    }

    # Prepare the GraphQL mutation to add products to a collection
    mutation = """
    mutation collectionAddProducts($id: ID!, $productIds: [ID!]!) {
      collectionAddProducts(id: $id, productIds: $productIds) {
        collection {
          id
          title
          productsCount
          products(first: 20) {
            nodes {
              id
              title
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

    # Prepare the variables for the GraphQL mutation
    variables = {
        "id": collection_id,
        "productIds": product_ids
    }

    # Make the POST request using httpx
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
        logger.error(f"Failed to add products to collection: {response.json()}")
        return None, response.json()
    else:
        result = response.json()
        if 'collectionAddProducts' in result['data'] and 'collection' in result['data']['collectionAddProducts']:
            # Return the updated collection information
            return result['data']['collectionAddProducts']['collection']['id'], None
        else:
            logger.error(f"Failed to add products to collection: {result}")
            return None, result