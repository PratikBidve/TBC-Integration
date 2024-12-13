import logging
import httpx
from app.dependencies.shopify_auth import get_shopify_client

logger = logging.getLogger(__name__)

def prepare_metafields_for_graphql_products(product_info, hubspot_data, line_item_ids):
    # Prepare metafields in the format expected by the GraphQL API
    
    logger.debug(f"Stock info: {product_info}")
    logger.debug(f"Hubspot data: {hubspot_data}")


    # Convert all line item IDs to strings
    line_item_ids_str = "\n".join(map(str, line_item_ids))
    
    metafields = [
        {
            "namespace": "custom",
            "key": "product_category",
            "value": product_info.get("SKU", ""),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "Materiaal",
            "value": product_info.get("Material", ""),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "Materiaal_kleur",
            "value": product_info.get("Marterial color", ""),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "drukkleuren",
            "value": product_info.get("Print", ""),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "productie",
            "value": product_info.get("Name", ""),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "Aantal_per_doos",
            "value": str(product_info.get("Unit", "")),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "Formaat",
            "value": product_info.get("Size", ""),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "inhoud",
            "value": product_info.get("Beschrijving", ""),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "Vouw",
            "value": product_info.get("Fold", ""),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "Material layer",
            "value": product_info.get("Material_layer", ""),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "customer_name",
            "value": hubspot_data.get("Company Name", ""),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "CompanyID-HS",
            "value": hubspot_data.get("Company ID", ""),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "produt_id",
            "value": product_info.get("uniqueCode", ""),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "Unique_Product_ID",
            "value": product_info.get("uniqueProductIdentifier", ""),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "original_price",
            "value": hubspot_data.get("price", ""),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "original_purchase_price",
            "value": str(product_info.get("Aankoopprijs", "")),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "product_status",
            "value": 'Upload Design/Logo Files',
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "hs_line_item_id_s",
            "value": line_item_ids_str,
            "type": "multi_line_text_field"
        }
    ]

    # Return all metafields without filtering
    return metafields

async def create_shopify_product(hs_sku, product_title, metafields, discounted_price):
    shopify_client = get_shopify_client()
    base_url = shopify_client['base_url']
    token = shopify_client['token']

    # Prepare the headers
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': token
    }

    # Prepare the GraphQL mutation
    mutation = """
    mutation createProductMetafields($input: ProductInput!) {
      productCreate(input: $input) {
        product {
          id
          metafields(first: 20) {
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

    # Prepare the variables for the GraphQL mutation
    variables = {
        "input": {
            "title": product_title,
            "bodyHtml": "<strong>New product created from Hubspot deal!</strong>",
            "vendor": "The Branding Club",
            "productType": "customerSpecific",
            "tags": f"Sku-{hs_sku}",
            "metafields": metafields,
             "variants": [{
                "price": discounted_price,
                "sku": hs_sku,
            }]
        }
    }
    
    # logger.info(f"Metafields for line item ID {hs_sku}: {metafields}")

    # Log the GraphQL mutation and variables before making the request
    # logger.info(f"GraphQL variables for line item ID {hs_sku}: {variables}")

    # Make the POST request using httpx instead of requests
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'{base_url}/graphql.json',
            headers=headers,
            json={
                'query': mutation,
                'variables': variables
            }
        )
        # logger.info(f"GraphQL response for line item ID {hs_sku}: {response.json()}")

    if response.status_code != 200:
        logger.error(f"Shopify product creation failed: {response.json()}")
        return None, response.json()
    else:
        result = response.json()
        if result['data']['productCreate']['userErrors']:
            logger.error(f"Shopify product creation failed: {result['data']['productCreate']['userErrors']}")
            return None, result['data']['productCreate']['userErrors']
        else:
            product_id = result['data']['productCreate']['product']['id']
            logger.info(f"Successfully created Shopify product with ID: {product_id}")
            return product_id, None


