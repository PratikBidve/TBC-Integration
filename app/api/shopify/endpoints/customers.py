import logging
import httpx
import json
from app.dependencies.shopify_auth import get_shopify_client

# Initialize logger
logger = logging.getLogger(__name__)

# Get Shopify client instance
shopify_client = get_shopify_client()

def prepare_metafields_for_graphql_customers(customer_data, company_data, owner_data):
    """Prepare metafields in the format expected by the GraphQL API."""
    metafields = [
        {
            "namespace": "custom",
            "key": "collection",
            "value": json.dumps([customer_data.get('collection', '')]),
            "type": "list.collection_reference"
        },
        {
            "namespace": "custom",
            "key": "company_name",
            "value": company_data.get('company_name', ''),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "ba_email",
            "value": owner_data.get('email', ''),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "companyId",
            "value": company_data.get('company_id', ''),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "ba_id",
            "value": owner_data.get('id', ''),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "BA_name",
            "value": owner_data.get('first_name', ''),
            "type": "single_line_text_field"
        },
        {
            "namespace": "custom",
            "key": "BA_phone",
            "value": owner_data.get('phone', ''),
            "type": "single_line_text_field"
        }
    ]
    return metafields

def create_shopify_customer(customer_data, metafields_string):
    """Create a Shopify customer."""
    # Retrieve Shopify client details
    base_url = shopify_client['base_url']
    token = shopify_client['token']

    # Set request headers
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': token
    }

    # Define GraphQL mutation for customer creation
    mutation = """
    mutation customerCreate($input: CustomerInput!) {
      customerCreate(input: $input) {
        customer {
          id
          email
          firstName
          lastName
        }
        userErrors {
          field
          message
        }
      }
    }
    """

    # Prepare variables for the mutation
    variables = {
        "input": {
            "firstName": customer_data['first_name'],
            "lastName": customer_data['last_name'],
            "email": customer_data['email'],
            "phone": customer_data['phone'],
            "addresses": [
                {
                    "address1": customer_data['address1'],
                    "city": customer_data['city'],
                    "country": customer_data['country']
                }
            ],
            "metafields": metafields_string,
        }
    }

    # Execute the GraphQL mutation
    try:
        response = httpx.post(
            f'{base_url}/graphql.json',
            headers=headers,
            json={'query': mutation, 'variables': variables}
        )

        # Check response status
        if response.status_code!= 200:
            logger.error(f"Shopify customer creation failed with status code {response.status_code}. Full response: {response.text}")
            return None, response.json()
        else:
            result = response.json()
            if 'errors' in result:
                logger.error(f"GraphQL errors encountered: {result['errors']}")
                return None, result['errors']
            elif 'data' in result and 'customerCreate' in result['data']:
                if 'userErrors' in result['data']['customerCreate']:
                    logger.error(f"User errors in customer creation: {result['data']['customerCreate']['userErrors']}")
                    return None, result['data']['customerCreate']['userErrors']
                else:
                    customer_id = result['data']['customerCreate']['customer']['id']
                    logger.info(f"Successfully created Shopify customer with ID: {customer_id}")
                    # Send account invitation
                    success = send_account_invitation(customer_id)
                    if success:
                        logger.info(f"Account invitation sent successfully for customer ID {customer_id}")
                    else:
                        logger.error(f"Failed to send account invitation for customer ID {customer_id}")
                    return customer_id, None
            else:
                logger.error(f"Unexpected response structure: {result}")
                return None, result

    except Exception as e:
        logger.error(f"An exception occurred while creating Shopify customer: {str(e)}")
        return None, str(e)

def send_account_invitation(customer_id):
    """Send an account invitation to the newly created customer."""
    # Construct the URL for the account invitation API
    url = f"{shopify_client['base_url']}/admin/api/2023-07/customers/{customer_id}/send_account_invitation.json"

    # Set request headers
    headers = {
        'Content-Type': 'application/json',
        'X-Shopify-Access-Token': shopify_client['token']
    }

    # Make the API request to send the account invitation
    try:
        response = httpx.post(url, headers=headers)
        if response.status_code!= 200:
            logger.error(f"Failed to send account invitation for customer ID {customer_id} with status code {response.status_code}. Full response: {response.text}")
            return False
        else:
            logger.info(f"Account invitation sent successfully for customer ID {customer_id}")
            return True
    except Exception as e:
        logger.error(f"An exception occurred while sending account invitation for customer ID {customer_id}: {str(e)}")
        return False