# # app/dependencies/shopify_auth.py
# from fastapi import HTTPException, APIRouter
# import shopify
# from dotenv import load_dotenv
# import os

# router = APIRouter()

# load_dotenv()

# def get_shopify_client() -> dict:
#     try:
#         token = os.getenv('TOKEN')
#         merchant = 'devbrandingclub.myshopify.com'

#         api_session = shopify.Session(merchant, '2023-04', token)
#         shopify.ShopifyResource.activate_session(api_session)
#         shop = shopify.Shop.current()
#         return {
#             'base_url': f"https://{merchant}/admin/api/2023-04",
#             'token': token,
#             'api_version': '2023-04'
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to authenticate with Shopify: {str(e)}")




# app/dependencies/shopify_auth.py
from fastapi import HTTPException, APIRouter
import shopify
from dotenv import load_dotenv
import os

router = APIRouter()

load_dotenv()

def get_shopify_client() -> dict:
    try:
        token = os.getenv('TOKEN')
        merchant = 'thebrandingclub.myshopify.com'

        api_session = shopify.Session(merchant, '2023-04', token)
        shopify.ShopifyResource.activate_session(api_session)
        shop = shopify.Shop.current()
        return {
            'base_url': f"https://{merchant}/admin/api/2023-04",
            'token': token,
            'api_version': '2023-04'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to authenticate with Shopify: {str(e)}")



# ... other code ...



# print(get_shopify_client().execute('query { shop { name } }'))
# Global variable to store contact and quotation information
# contact_and_quotation_info = {}

# def update_contact_and_quotation_info(contact_info, quotation_info):
#     global contact_and_quotation_info
#     contact_and_quotation_info = {
#         'contact_info': contact_info,
#         'quotation_info': quotation_info
#     }

# def get_contact_and_quotation_info():
#     return contact_and_quotation_info

# # Check data after hitting deals.py route
# print(get_contact_and_quotation_info())


# webhook = shopify.Webhook()
# webhook.topic = 'customers/create' # Specify the event you want to listen for
# webhook.address = 'pubsub://automation-shopify-webhook:insights' # Specify the Pub/Sub topic URL
# webhook.format = 'json'
# webhook.save()


# from fastapi import Depends, HTTPException, APIRouter
# import os
# import shopify
# from dotenv import load_dotenv

# router = APIRouter()

# load_dotenv()

# token = os.getenv('TOKEN')
# merchant = 'devbrandingclub.myshopify.com'

# api_session = shopify.Session(merchant, '2023-04', token)
# shopify.ShopifyResource.activate_session(api_session)

# def get_access_token():
#     if not api_session.valid:
#         raise HTTPException(status_code=400, detail="Invalid Shopify session")
#     return api_session.request_headers['X-Shopify-Access-Token']
#     print(api_session.request_headers['X-Shopify-Access-Token'])



















# # app/dependencies/shopify_auth.py
# from fastapi import HTTPException, APIRouter
# import shopify
# from dotenv import load_dotenv
# import os

# router = APIRouter()

# load_dotenv()

# def get_shopify_client() -> dict:
#     try:
#         token = os.getenv('TOKEN')
#         merchant = 'thebrandingclub.myshopify.com'

#         api_session = shopify.Session(merchant, '2023-04', token)
#         shopify.ShopifyResource.activate_session(api_session)
#         shop = shopify.Shop.current()
#         return {
#             'base_url': f"https://{merchant}/admin/api/2023-04",
#             'token': token,
#             'api_version': '2023-04'
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to authenticate with Shopify: {str(e)}")


# ... other code ...



# print(get_shopify_client().execute('query { shop { name } }'))
# Global variable to store contact and quotation information
# contact_and_quotation_info = {}

# def update_contact_and_quotation_info(contact_info, quotation_info):
#     global contact_and_quotation_info
#     contact_and_quotation_info = {
#         'contact_info': contact_info,
#         'quotation_info': quotation_info
#     }

# def get_contact_and_quotation_info():
#     return contact_and_quotation_info

# # Check data after hitting deals.py route
# print(get_contact_and_quotation_info())


# webhook = shopify.Webhook()
# webhook.topic = 'customers/create' # Specify the event you want to listen for
# webhook.address = 'pubsub://automation-shopify-webhook:insights' # Specify the Pub/Sub topic URL
# webhook.format = 'json'
# webhook.save()


# from fastapi import Depends, HTTPException, APIRouter
# import os
# import shopify
# from dotenv import load_dotenv

# router = APIRouter()

# load_dotenv()

# token = os.getenv('TOKEN')
# merchant = 'devbrandingclub.myshopify.com'

# api_session = shopify.Session(merchant, '2023-04', token)
# shopify.ShopifyResource.activate_session(api_session)

# def get_access_token():
#     if not api_session.valid:
#         raise HTTPException(status_code=400, detail="Invalid Shopify session")
#     return api_session.request_headers['X-Shopify-Access-Token']
#     print(api_session.request_headers['X-Shopify-Access-Token'])


