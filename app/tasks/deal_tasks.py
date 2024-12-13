import asyncio
from celery import shared_task
from app.dependencies.hubspot_auth import get_hubspot_client
from app.api.hubspot.endpoints.get_line_items_by_deal_id import get_deal_line_items
from app.api.hubspot.endpoints.get_companies_by_deal_id import get_deal_companies
from app.api.hubspot.endpoints.get_contacts_by_deal_id import get_deal_contacts
from app.api.hubspot.endpoints.company_info import get_company
from app.api.hubspot.endpoints.line_item_info import get_line_item
from app.api.hubspot.endpoints.contact_info import get_contact
from app.api.hubspot.endpoints.deal_info import get_deal
from app.api.hubspot.endpoints.owner_info import get_owner_by_id
from app.api.shopify.endpoints.orders import create_shopify_draft_order
from app.api.shopify.endpoints.get_variant import get_shopify_product_variant
from app.api.airtable.endpoints.product_response import get_product_info
from app.api.shopify.endpoints.products import create_shopify_product, prepare_metafields_for_graphql_products
from app.api.shopify.endpoints.customers import create_shopify_customer, prepare_metafields_for_graphql_customers
from app.api.shopify.endpoints.collections import get_collection, create_collection, add_product_to_collection
from app.api.shopify.endpoints.get_customer import query_shopify_customer_by_email
from app.api.shopify.endpoints.draft_order_complete import complete_draft_order
from app.api.shopify.endpoints.publish_collection import publish_collection_to_online_store

import httpx
import logging

# Set up logging
logger = logging.getLogger(__name__)

country_code_to_name = {
    "NL": "Netherlands",
    "FR": "France",
    "ES": "Spain",
    "DE": "Germany",
    "BE": "Belgium",
    # Add more country codes and their corresponding names as needed
}
ERROR_WEBHOOK_URL = "https://hook.eu1.make.com/86s6j3sv99orfg0eobsjt4b6y0xjbjbt"
WEBHOOK_URL = "https://hook.eu1.make.com/rt2bpjtyds60s7p4m9ec845fvysm2pcm"


async def send_error_to_webhook(error_message):
    payload = {
        "error": error_message
    }
    logger.info(f"Sending error webhook with payload: {payload}")
    async with httpx.AsyncClient() as client:
        response = await client.post(ERROR_WEBHOOK_URL, json=payload)
        if response.status_code != 200:
            logger.error(f"Failed to send error webhook: {response.text}")
        else:
            logger.info("Error webhook sent successfully.")


async def send_webhook(webhook_data):
    async with httpx.AsyncClient() as client:
        response = await client.post(WEBHOOK_URL, json=webhook_data)
        if response.status_code != 200:
            logger.error(f"Failed to send webhook: {response.text}")
        else:
            logger.info("Webhook sent successfully.")


@shared_task(name='app.tasks.deal_tasks.get_line_items_and_create_customers')
def get_line_items_and_create_customers(deal_id):
    hubspotLineItems = []
    variant_ids = []
    product_ids = []
    try:
        # Initialize the HubSpot client
        client = get_hubspot_client()
        # Fetch the companies associated with the deal
        companies_response = asyncio.run(get_deal_companies(deal_id, client))
        
        # Filter the companies to only include the primary one
        primary_company = next((company for company in companies_response['results']
                                 if any(assoc['type_id'] == 5 for assoc in company['association_types'])), None)

        if primary_company:
            # Extract the primary company ID
            primary_company_id = primary_company['to_object_id']

            # Fetch the primary company details
            primary_company_details = asyncio.run(get_company(primary_company_id, client))

            # Extract the necessary company data
            company_data = {
                "company_name": primary_company_details.get('properties', {}).get('name', ''),
                "company_id": primary_company_details.get('id', ''),
                "company_address": primary_company_details.get('properties', {}).get('address', ''),
                "company_city": primary_company_details.get('properties', {}).get('city', ''),
                "company_country": primary_company_details.get('properties', {}).get('country', ''),
            }
            # Use the company name as the collection title
            collection_title = company_data['company_name']
            
            # After creating the Shopify product, fetch or create the collection
            collection_id, collection_error = get_collection(collection_title)
            if collection_error:
                error_message = f"Doesn't found existing collection: {collection_error}"
                asyncio.run(send_error_to_webhook(error_message))    
                logger.error(error_message)
                
                # If the collection does not exist, create a new one
                collection_id, collection_error = create_collection(collection_title)
                if collection_error:
                    error_message = f"Failed to create collection: {collection_error}"
                    asyncio.run(send_error_to_webhook(error_message))
                else:
                    logger.info(f"Created new collection with ID: {collection_id}")
            else:
                logger.info(f"Fetched collection with ID: {collection_id}")

            # Log the fetched primary company details
            logger.info(f"Fetched primary company details for ID {primary_company_id}: {company_data}")
            # Fetch the contacts associated with the deal
            contacts_response = asyncio.run(get_deal_contacts(deal_id, client))
            contact_ids = [contact['to_object_id'] for contact in contacts_response['results']]

            # Initialize customer_id to None before the loop
            customer_id = None

            # Iterate over the contact IDs and fetch details for each
            for contact_id in contact_ids:
                try:
                    # Fetch contact details and create Shopify customers
                    contact_details = asyncio.run(get_contact(contact_id, client))
                    email = contact_details.get('properties', {}).get('email', '')
                    owner_id = primary_company_details.get('properties', {}).get('hubspot_owner_id', '')
                    owner_data = asyncio.run(get_owner_by_id(owner_id, client)) if owner_id else {}
                    customer_data = {
                        "first_name": contact_details.get('properties', {}).get('firstname', ''),
                        "last_name": contact_details.get('properties', {}).get('lastname', ''),
                        "email": contact_details.get('properties', {}).get('email', ''),
                        "phone": contact_details.get('properties', {}).get('phone', ''),
                        "contact_id": contact_details.get('id', ''),
                        "owner_email": owner_data.get('email', ''),
                        "owner_first_name": owner_data.get('first_name', ''),
                        "owner_last_name": owner_data.get('last_name', ''),
                        "owner_id": owner_data.get('id', ''),
                        "address1": company_data['company_address'],
                        "city": company_data['company_city'],
                        "country": company_data['company_country'],
                        "collection": collection_id
                    }
                    metafields_string = prepare_metafields_for_graphql_customers(customer_data, company_data, owner_data)

                    # Check if the customer already exists
                    existing_customer, _ = asyncio.run(query_shopify_customer_by_email(email))
                    if existing_customer and len(existing_customer) > 0:
                        customer = existing_customer[0] # Access the first customer in the list
                        logger.info(f"Customer with email {email} already exists. Using existing customer ID {customer['id']}.")
                        customer_id = customer['id']                    
                    else:
                        customer_id, customer_error = create_shopify_customer(customer_data, metafields_string)
                        if customer_error:
                            error_message = f"Failed to create Shopify customer for contact ID {contact_id}: {customer_error}"  
                            logger.error(f"Preparing to send error webhook with message: {error_message}")
                            asyncio.run(send_error_to_webhook(error_message))    
                            logger.info("Attempted to send error webhook.")
                            logger.error(error_message)
                            continue
                        else:
                            logger.info(f"Created Shopify customer with ID {customer_id} for contact ID {contact_id}")
                except Exception as e:
                    error_message = f"An error occurred: {e}"
                    logger.error(error_message)
                    asyncio.run(send_error_to_webhook(error_message))
                    logger.info("Attempted to send error webhook.")
                    continue

            # Fetch the line items for the deal
            line_items_response = asyncio.run(get_deal_line_items(deal_id, client))
            line_item_ids = [item['to_object_id'] for item in line_items_response['results']]

            highest_discount_percentage = 0.0

            line_item_ids_list = []
            
            # Iterate over the line item IDs and fetch details for each
            for to_object_id in line_item_ids:
                try:
                    # Fetch line item details and create Shopify products
                    line_item_details = asyncio.run(get_line_item(to_object_id, client))
                    if 'properties' not in line_item_details:
                        error_message = f"'properties' key not found in line item details for ID {to_object_id}"
                        asyncio.run(send_error_to_webhook(error_message))
                        continue
                    hs_sku = line_item_details['properties']['hs_sku']
                    company_name = company_data['company_name']
                    
                    product_title = f"{hs_sku} - {company_name}"
                    quantity = line_item_details['properties']['quantity']
                    price = float(line_item_details['properties']['price'])
                    discount_percentage = float(line_item_details['properties'].get('hs_discount_percentage')) if line_item_details['properties'].get('hs_discount_percentage') is not None else 0.0
                    
                    # Update the highest discount percentage
                    if discount_percentage > highest_discount_percentage:
                        highest_discount_percentage = discount_percentage
                    
                    product_info_list = asyncio.run(get_product_info(hs_sku))
                    logger.info(f"Product details for SKU {hs_sku}: {product_info_list}")
                    product_info = product_info_list[0][0]['fields'] if product_info_list else {}
                    product_data = {
                        "hs_sku": hs_sku,
                        "customer_specific": company_data,
                        "vendor": "The Branding Club",
                        "status": "ACTIVE",
                        "product_info": product_info,
                        "hubspot_data": line_item_details['properties'],
                        "price": price,
                    }

                    # Collect line item IDs
                    line_item_ids_list.append(to_object_id)

                    metafields = prepare_metafields_for_graphql_products(product_info, product_data['hubspot_data'], line_item_ids_list)
                    product_id, product_error = asyncio.run(create_shopify_product(hs_sku, product_title, metafields, price))
                    if product_error:
                        error_message = f"Failed to create product for line item ID {to_object_id}: {product_error}"
                        asyncio.run(send_error_to_webhook(error_message))
                        continue
                    logger.info(f"Created Shopify product with ID {product_id} for line item ID {to_object_id}")
                    product_ids.append(product_id)
                
                    # After creating the Shopify product, fetch the variant
                    variant, variant_error = asyncio.run(get_shopify_product_variant(product_id))
                    if variant_error:
                        error_message = f"Failed to get variant for product ID {product_id}: {variant_error}"
                        asyncio.run(send_error_to_webhook(error_message))
                    else:
                        variant_id = variant['id']
                        logger.info(f"Fetched variant with ID {variant_id} for product ID {product_id}")
                        variant_ids.append({"variantId": variant_id, "quantity": quantity})
                        # Add the necessary information to the hubspotLineItems list
                        hubspotLineItems.append({
                        "shopifyProductId": product_id.split('/')[-1], # Assuming product_id is the Shopify product ID
                        "hubspotLineItemId": to_object_id # Assuming to_object_id is the HubSpot line item ID
                        })

                except Exception as e:
                    error_message= f"An error occurred while processing line item ID {to_object_id}: {e}"
                    asyncio.run(send_error_to_webhook(error_message))

            if collection_id and product_ids:
                logger.info(f"Adding product IDs {product_ids} to collection with ID {collection_id}")
                collect_id, collect_error = add_product_to_collection(collection_id, product_ids)
                if collect_error:
                    error_message = f"Failed to add product to collection: {collect_error}"
                    asyncio.run(send_error_to_webhook(error_message))
                else:
                    logger.info(f"Successfully added product to collection with ID: {collect_id}")
            else:
                logger.warning(f"No products to add to collection or collection ID is None.")
            
            # Publish the collection to the online store
            published_collection, error = asyncio.run(publish_collection_to_online_store(collection_id))
            if published_collection:
                logger.info(f"Successfully published collection with ID {collection_id} to the online store.")
            else:
                error_message = f"Failed to publish collection with ID {collection_id} to the online store: {error}"
                asyncio.run(send_error_to_webhook(error_message))

            # Fetch deal details and create orders after all customers have been created
            deal_info = asyncio.run(get_deal(deal_id, client))
            logger.info(f"Deal details for ID {deal_id}: {deal_info}")
            # Extract the billing and delivery country codes from the deal response
            billing_country_code = deal_info.get('properties', {}).get('billing_country_region', '')
            delivery_country_code = deal_info.get('properties', {}).get('delivery_country', '')

            # Convert the country codes to the full country names using the mapping dictionary
            billing_country_name = country_code_to_name.get(billing_country_code, "Unknown")
            delivery_country_name = country_code_to_name.get(delivery_country_code, "Unknown")

            # Prepare the order data
            deal_data = {
                "dealname": deal_info.get('properties', {}).get('dealname', ''),
                "email": customer_data.get('email', ''),
                "phone": customer_data.get('phone', ''),
                "company_id": company_data.get('company_id', ''),
                "customer_id": customer_id,
                "variant_ids": variant_ids,
                "amount": deal_info.get('properties', {}).get('amount', ''),
                "billing_address": deal_info.get('properties', {}).get('billing_address', ''),
                "billing_city": deal_info.get('properties', {}).get('billing_city', ''),
                "billing_country": billing_country_name,
                "billing_postal_code": deal_info.get('properties', {}).get('billing_postal_code', ''),
                "delivery_address": deal_info.get('properties', {}).get('delivery_address', ''),
                "delivery_city": deal_info.get('properties', {}).get('delivery_city', ''),
                "delivery_country": delivery_country_name,
                "delivery_zip": deal_info.get('properties', {}).get('delivery_zip', ''),
                "billing_company": deal_info.get('properties', {}).get('billing_company', ''),
                "payment_condition": deal_info.get('properties', {}).get('payment_condition', ''),
                "HS_Deal_ID": deal_id,
                "discount_percentage": highest_discount_percentage
            }
            logger.info(f"Deal data: {deal_data}")
            logger.info(f"Variant IDs for draft order: {variant_ids}")

            if variant_ids:
                draft_order_id, draft_order_error = create_shopify_draft_order(deal_data, variant_ids)
                if draft_order_error:
                    error_message = f"Failed to create draft order: {draft_order_error}"
                    asyncio.run(send_error_to_webhook(error_message))
                else:
                    logger.info(f"Created Shopify draft order with ID {draft_order_id} for deal ID {deal_id}")
                    # After successfully creating the draft order,
                    # Complete the draft order.
                    order_id, order_error = complete_draft_order(draft_order_id, True, deal_data) # Assuming payment is pending
                    if order_error:
                        error_message = f"Failed to complete draft order: {order_error}"
                        asyncio.run(send_error_to_webhook(error_message))
                    else:
                        logger.info(f"Successfully completed draft order with ID {draft_order_id}. Order ID: {order_id} for Hubspot Deal ID {deal_id}")
                        
                        # Send webhook
                        webhook_data = {
                            "event": "draft_order_completed",
                            "deal_id": deal_id,
                            "draft_order_id": draft_order_id.split('/')[-1], # Extract the numeric part of the draft_order_id
                            "order_id": order_id.split('/')[-1],
                            "hubspotLineItems": hubspotLineItems
                        } # Extract the numeric part of the order_id
                            
                        async def process_deal():
                            await send_webhook(webhook_data)
                            logger.info(f"Webhook sent for deal ID {deal_id} with {webhook_data}")
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(process_deal())
                        loop.close()
            else:
                error_message = "No products to add to the draft order."
                asyncio.run(send_error_to_webhook(error_message))
                logger.error(error_message)

    except Exception as e:
        error_message = f"Failed to complete all operations: {e}"
        asyncio.run(send_error_to_webhook(error_message))
    return


    