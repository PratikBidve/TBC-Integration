# get_line_items_by_deal_id.py
from fastapi import APIRouter, Depends, HTTPException
from hubspot.crm.associations.v4 import ApiException
from app.dependencies.hubspot_auth import get_hubspot_client

import logging

router = APIRouter()

# Set up the logger
logger = logging.getLogger(__name__)

@router.get("/deals/{deal_id}/line_items", response_model=dict)
async def get_deal_line_items(deal_id: str, client=Depends(get_hubspot_client)):
    try:
        api_response = client.crm.associations.v4.basic_api.get_page(object_type="Deals", object_id=deal_id, to_object_type="line_items", limit=500)
        return process_response(api_response)
    except ApiException as e:
        logger.error(f"ApiException: {e}")
        raise HTTPException(status_code=400, detail=str(e))

def process_response(api_response):
    if isinstance(api_response, dict):
        return api_response
    else:
        # If the response is not a dictionary, attempt to convert it to a dictionary
        # This assumes that the response object has a to_dict() method
        if hasattr(api_response, 'to_dict'):
            return api_response.to_dict()
        else:
            # If the response cannot be converted to a dictionary, raise an appropriate error
            raise TypeError(f"Expected a dictionary, got {type(api_response).__name__} instead.")




# from fastapi import APIRouter, Depends, HTTPException
# from hubspot.crm.deals import ApiException as DealsApiException
# from hubspot.crm.associations.v4 import ApiException
# from app.dependencies.hubspot_auth import get_hubspot_client
# from app.dependencies.hubspot_auth import hubspot_client
# from pprint import pprint

# from pydantic import BaseModel
# import logging

# router = APIRouter()

# #Set up the logger
# logger = logging.getLogger(__name__)



# try:
#     api_response = hubspot_client.crm.associations.v4.basic_api.get_page(object_type="Deals", object_id="10599910087", to_object_type="line_items", limit=500)
#     pprint(api_response)
# except ApiException as e:
#     print("Exception when calling basic_api->get_page: %s\n" % e)








# from fastapi import APIRouter, Depends, HTTPException
# from hubspot.crm.deals import ApiException as DealsApiException
# from hubspot.crm.line_items import ApiException as LineItemsApiException
# from app.dependencies.hubspot_auth import get_hubspot_client
# from pydantic import BaseModel
# from typing import List
# import logging

# router = APIRouter()

# # Set up the logger
# logger = logging.getLogger(__name__)

# class LineItem(BaseModel):
#     id: str
#     price: float
#     quantity: int
#     name: str
#     # Add any additional line item properties here
#     mrr: float
#     margin: float

# class Deal(BaseModel):
#     id: str
#     amount: float
#     dealstage: str
#     dealname: str
#     pipeline: str
#     closedate: str
#     probability: float
#     hubspot_owner_id: str

# class DealResponse(BaseModel):
#     deal: Deal
#     line_items: List[LineItem]

# def get_line_items_by_deal(client, deal_id):
#     all_line_items = []
#     try:
#         # Use the 'get_page' method with the 'associations' parameter to filter by deal
#         line_items_response = client.crm.line_items.basic_api.get_page(
#             associations={'deal': deal_id},
#             properties=["price", "quantity", "name", "mrr", "margin"]
#         )
#         for item in line_items_response.results:
#             line_item = LineItem(
#                 id=item.id,
#                 price=item.properties.get('price', 0),
#                 quantity=item.properties.get('quantity', 0),
#                 name=item.properties.get('name', ''),
#                 mrr=item.properties.get('mrr', 0.0),
#                 margin=item.properties.get('margin', 0.0) if item.properties.get('margin') is not None else 0.0
#             )
#             all_line_items.append(line_item)
#     except LineItemsApiException as e:
#         logger.error(f"LineItems ApiException: {e}")
#         raise HTTPException(status_code=400, detail=f"LineItems ApiException: {str(e)}")

#     return all_line_items



# @router.post("/read_line_items_by_deal", response_model=dict)
# async def read_line_items_by_deal(deal_id: str, client=Depends(get_hubspot_client)):
#     if not deal_id:
#         raise HTTPException(status_code=400, detail="Deal ID is required")

#     try:
#         # Fetch deal properties
#         deal_response = client.crm.deals.basic_api.get_by_id(
#             deal_id=deal_id,
#             properties=["amount", "dealstage", "dealname", "pipeline", "closedate", "probability", "hubspot_owner_id"],
#             archived=False
#         )
#         deal_properties = deal_response.to_dict().get('properties', {})

#         # Fetch line items
#         line_items = get_line_items_by_deal(client, deal_id)

#         # Build response
#         response_data = {
#             "deal": Deal(
#                 id=deal_id,
#                 amount=deal_properties.get('amount', 0.0),
#                 dealstage=deal_properties.get('dealstage', ''),
#                 dealname=deal_properties.get('dealname', ''),
#                 pipeline=deal_properties.get('pipeline', ''),
#                 closedate=deal_properties.get('closedate', ''),
#                 probability=deal_properties.get('probability', 0.0),
#                 hubspot_owner_id=deal_properties.get('hubspot_owner_id', '')
#             ),
#             "line_items": line_items
#         }
        
#         return response_data
#     except DealsApiException as e:
#         logger.error(f"Deals ApiException: {e}")
#         raise HTTPException(status_code=400, detail=f"Deals ApiException: {str(e)}")
#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")


# from fastapi import APIRouter, Depends, HTTPException
# from hubspot import HubSpot
# from hubspot.crm.line_items import ApiException as LineItemsApiException
# from ....dependencies.hubspot_auth import get_hubspot_client  # Corrected import path
# from pydantic import BaseModel
# import logging
# from typing import List, Optional

# router = APIRouter()

# # Set up the logger
# logger = logging.getLogger(__name__)

# class LineItem(BaseModel):
#     id: str
#     price: float
#     quantity: int
#     name: str

# def get_all_line_items(client, deal_id, properties=None):
#     all_line_items = []
#     after = None
#     while True:
#         try:
#             line_items_response = client.crm.line_items.basic_api.get_page(
#                 associations={'deal': deal_id},
#                 properties=properties,
#                 after=after
#             )
#             all_line_items.extend(line_items_response.results)
#             if line_items_response.paging and line_items_response.paging.next:
#                 after = line_items_response.paging.next.after
#             else:
#                 break
#         except LineItemsApiException as e:
#             logger.error(f"LineItems ApiException: {e}")
#             raise HTTPException(status_code=400, detail=f"LineItems ApiException: {str(e)}")

#     return all_line_items

# @router.get("/deals/{deal_id}/line-items", response_model=List[LineItem])
# def get_deal_line_items(deal_id: str, client=Depends(get_hubspot_client)):
#     if not deal_id:
#         raise HTTPException(status_code=400, detail="Deal ID is required")

#     try:
#         line_items = get_all_line_items(client, deal_id, properties=["price", "quantity", "name"])
#         return line_items
#     except Exception as e:
#         logger.error(f"An unexpected error occurred: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")

# from fastapi import APIRouter, Depends, HTTPException
# from hubspot.crm.deals import ApiException
# from hubspot.crm.line_items import BasicApi as LineItemsBasicApi
# from ....dependencies.hubspot_auth import get_hubspot_client
# from pydantic import BaseModel

# router = APIRouter()

# class LineItem(BaseModel):
#     id: str
#     price: float
#     quantity: int
#     name: str

# class DealResponse(BaseModel):
#     id: str
#     name: str
#     stage: str
#     amount: float
#     pipeline: str
#     close_date: str
#     probability: float
#     deal_owner: str
#     line_items: list[LineItem]

# # This function assumes you have a custom implementation to get line items by deal ID
# def get_line_items_by_deal_id(client, deal_id, properties=None):
#     # Replace with your actual implementation
#     pass

# @router.get("/deals/{deal_id}", response_model=DealResponse)
# async def get_deal(deal_id: str, client = Depends(get_hubspot_client)):
#     try:
#         api_response = client.crm.deals.basic_api.get_by_id(
#             deal_id=deal_id,
#             properties=["amount", "dealstage", "dealname", "pipeline", "closedate", "probability", "hubspot_owner_id"],
#             archived=False
#         )
#         api_response_dict = api_response.to_dict()
#         properties_dict = api_response_dict.get('properties', {})
        
#         # Get line items associated with the deal
#         line_items = get_line_items_by_deal_id(client, deal_id, properties=["price", "quantity", "name"])
        
#         # Check if line_items is None and handle it appropriately
#         if line_items is None:
#             line_items = []
        
#         line_items_data = [LineItem(id=item.id, price=item.properties.get('price',   0.0), quantity=item.properties.get('quantity',   0), name=item.properties.get('name', '')) for item in line_items]
        
#         response = DealResponse(
#             id=api_response_dict['id'],
#             name=properties_dict.get('dealname', ''),
#             stage=properties_dict.get('dealstage', ''),
#             amount=properties_dict.get('amount',   0.0),
#             pipeline=properties_dict.get('pipeline', ''),
#             close_date=properties_dict.get('closedate', ''),
#             probability=properties_dict.get('probability',   0.0),
#             deal_owner=properties_dict.get('hubspot_owner_id', ''),
#             line_items=line_items_data
#         )
#         return response
#     except ApiException as e:
#         print(f"ApiException: {e}")
#         raise HTTPException(status_code=400, detail=str(e))



# from fastapi import APIRouter, Depends, HTTPException
# from hubspot.crm.deals import ApiException
# from hubspot.crm.line_items import ApiException as LineItemsApiException
# from ....dependencies.hubspot_auth import get_hubspot_client
# from pydantic import BaseModel

# # Initialize the router
# router = APIRouter()

# class DealResponse(BaseModel):
#     # Define the fields you want to include in the response
#     id: str
#     name: str
#     stage: str
#     amount: float
#     pipeline: str
#     line_items: list

# def get_all_line_items(client, deal_id, properties=None):
#     all_line_items = []
#     after = None
#     while True:
#         line_items_response = client.crm.line_items.basic_api.get_page(
#             associations={'deal': deal_id},
#             properties=properties,
#             after=after
#         )
#         all_line_items.extend(line_items_response.results)
#         if line_items_response.paging and line_items_response.paging.next:
#             after = line_items_response.paging.next.after
#         else:
#             break
#     return all_line_items

# @router.get("/deals/{deal_id}", response_model=DealResponse)
# async def get_deal(deal_id: str, client = Depends(get_hubspot_client)):
#     try:
#         # Fetch the deal by ID with the specified properties
#         api_response = client.crm.deals.basic_api.get_by_id(
#             deal_id=deal_id,
#             properties=["amount", "dealstage", "dealname", "pipeline"],
#             archived=False
#         )
#         # Convert the response to a dictionary
#         api_response_dict = api_response.to_dict()

#         # Access the properties dictionary directly
#         properties_dict = api_response_dict.get('properties', {})

#         # Fetch all line items associated with the deal
#         line_items = get_all_line_items(client, deal_id, properties=["price", "quantity", "name"])

#         # Convert the line items into a serializable format
#         line_items_data = [item.to_dict() for item in line_items]

#         # Create a response model instance with the necessary fields
#         response = DealResponse(
#             id=api_response_dict['id'],
#             name=properties_dict.get('dealname', ''),
#             stage=properties_dict.get('dealstage', ''),
#             amount=properties_dict.get('amount',   0.0),
#             pipeline=properties_dict.get('pipeline', ''),
#             line_items=line_items_data
#         )
#         return response
#     except (ApiException, LineItemsApiException) as e:
#         # Log the exception for debugging purposes
#         # Replace 'print' with a proper logging framework
#         print(f"ApiException: {e}")
#         raise HTTPException(status_code=400, detail=str(e))


# from fastapi import APIRouter, Depends, HTTPException
# from hubspot.crm.deals import ApiException
# from hubspot.crm.line_items import ApiException as LineItemsApiException
# from ....dependencies.hubspot_auth import get_hubspot_client
# from pydantic import BaseModel

# # Initialize the router
# router = APIRouter()

# class DealResponse(BaseModel):
#     # Define the fields you want to include in the response
#     id: str
#     name: str
#     stage: str
#     amount: float
#     pipeline: str
#     line_items: list

# def get_all_line_items(client, deal_id, properties=None):
#     all_line_items = []
#     after = None
#     while True:
#         line_items_response = client.crm.line_items.basic_api.get_page(
#             associations={'deal': deal_id},
#             properties=properties,
#             after=after
#         )
#         all_line_items.extend(line_items_response.results)
#         if line_items_response.paging and line_items_response.paging.next:
#             after = line_items_response.paging.next.after
#         else:
#             break
#     return all_line_items

# @router.get("/deals/{deal_id}", response_model=DealResponse)
# async def get_deal(deal_id: str, client = Depends(get_hubspot_client)):
#     try:
#         # Fetch the deal by ID with the specified properties
#         api_response = client.crm.deals.basic_api.get_by_id(
#             deal_id=deal_id,
#             properties=["amount", "dealstage", "dealname", "pipeline"],
#             archived=False
#         )
#         # Convert the response to a dictionary
#         api_response_dict = api_response.to_dict()

#         # Access the properties dictionary directly
#         properties_dict = api_response_dict.get('properties', {})

#         # Fetch all line items associated with the deal
#         line_items = get_all_line_items(client, deal_id, properties=["price", "quantity", "name"])

#         # Convert the line items into a serializable format
#         line_items_data = [item.to_dict() for item in line_items]

#         # Create a response model instance with the necessary fields
#         response = DealResponse(
#             id=api_response_dict['id'],
#             name=properties_dict.get('dealname', ''),
#             stage=properties_dict.get('dealstage', ''),
#             amount=properties_dict.get('amount',   0.0),
#             pipeline=properties_dict.get('pipeline', ''),
#             line_items=line_items_data
#         )
#         return response
#     except (ApiException, LineItemsApiException) as e:
#         # Log the exception for debugging purposes
#         # Replace 'print' with a proper logging framework
#         print(f"ApiException: {e}")
#         raise HTTPException(status_code=400, detail=str(e))
# from fastapi import APIRouter, Depends, HTTPException
# from hubspot.crm.deals import ApiException
# from hubspot.crm.line_items import ApiException as LineItemsApiException
# from ....dependencies.hubspot_auth import get_hubspot_client
# from pydantic import BaseModel

# # Initialize the router
# router = APIRouter()

# class DealResponse(BaseModel):
#     # Define the fields you want to include in the response
#     id: str
#     name: str
#     stage: str
#     amount: float
#     pipeline: str
#     line_items: list

# def get_all_line_items(client, deal_id, properties=None):
#     all_line_items = []
#     after = None
#     while True:
#         line_items_response = client.crm.line_items.basic_api.get_page(
#             associations={'deal': deal_id},
#             properties=properties,
#             after=after
#         )
#         all_line_items.extend(line_items_response.results)
#         if line_items_response.paging and line_items_response.paging.next:
#             after = line_items_response.paging.next.after
#         else:
#             break
#     return all_line_items

# @router.get("/deals/{deal_id}", response_model=DealResponse)
# async def get_deal(deal_id: str, client = Depends(get_hubspot_client)):
#     try:
#         # Fetch the deal by ID with the specified properties
#         api_response = client.crm.deals.basic_api.get_by_id(
#             deal_id=deal_id,
#             properties=["amount", "dealstage", "dealname", "pipeline"],
#             archived=False
#         )
#         # Convert the response to a dictionary
#         api_response_dict = api_response.to_dict()

#         # Access the properties dictionary directly
#         properties_dict = api_response_dict.get('properties', {})

#         # Fetch all line items associated with the deal
#         line_items = get_all_line_items(client, deal_id, properties=["price", "quantity", "name"])

#         # Convert the line items into a serializable format
#         line_items_data = [item.to_dict() for item in line_items]

#         # Create a response model instance with the necessary fields
#         response = DealResponse(
#             id=api_response_dict['id'],
#             name=properties_dict.get('dealname', ''),
#             stage=properties_dict.get('dealstage', ''),
#             amount=properties_dict.get('amount',   0.0),
#             pipeline=properties_dict.get('pipeline', ''),
#             line_items=line_items_data
#         )
#         return response
#     except (ApiException, LineItemsApiException) as e:
#         # Log the exception for debugging purposes
#         # Replace 'print' with a proper logging framework
#         print(f"ApiException: {e}")
#         raise HTTPException(status_code=400, detail=str(e))
# from fastapi import APIRouter, Depends, HTTPException
# from hubspot.crm.deals import ApiException
# from hubspot.crm.line_items import ApiException as LineItemsApiException
# from ....dependencies.hubspot_auth import get_hubspot_client
# from pydantic import BaseModel

# # Initialize the router
# router = APIRouter()

# class DealResponse(BaseModel):
#     # Define the fields you want to include in the response
#     id: str
#     name: str
#     stage: str
#     amount: float
#     pipeline: str
#     line_items: list

# @router.get("/deals/{deal_id}", response_model=DealResponse)
# async def get_deal(deal_id: str, client = Depends(get_hubspot_client)):
#     try:
#         # Fetch the deal by ID with the specified properties
#         api_response = client.crm.deals.basic_api.get_by_id(
#             deal_id=deal_id,
#             properties=["amount", "dealstage", "dealname", "pipeline"],
#             archived=False
#         )
#         # Convert the response to a dictionary
#         api_response_dict = api_response.to_dict()

#         # Access the properties dictionary directly
#         properties_dict = api_response_dict.get('properties', {})

#         # Fetch line items associated with the deal
#         line_items_response = client.crm.line_items.basic_api.get_page(
#             associations={'deal': deal_id},
#             properties=["price", "quantity", "name"]  # Add the properties you want to fetch
#         )
#         # Convert the line items into a serializable format
#         line_items = [item.to_dict() for item in line_items_response.results]

#         # Create a response model instance with the necessary fields
#         response = DealResponse(
#             id=api_response_dict['id'],
#             name=properties_dict.get('dealname', ''),
#             stage=properties_dict.get('dealstage', ''),
#             amount=properties_dict.get('amount',   0.0),
#             pipeline=properties_dict.get('pipeline', ''),
#             line_items=line_items
#         )
#         return response
#     except (ApiException, LineItemsApiException) as e:
#         # Log the exception for debugging purposes
#         # Replace 'print' with a proper logging framework
#         print(f"ApiException: {e}")
#         raise HTTPException(status_code=400, detail=str(e))

# from fastapi import APIRouter, Depends, HTTPException
# from hubspot.crm.deals import ApiException
# from ....dependencies.hubspot_auth import get_hubspot_client
# from pydantic import BaseModel

# # Initialize the router
# router = APIRouter()

# class DealResponse(BaseModel):
#     # Define the fields you want to include in the response
#     id: str
#     name: str
#     stage: str
#     amount: float
#     pipeline: str
#     line_items: list

# @router.get("/deals/{deal_id}", response_model=DealResponse)
# async def get_deal(deal_id: str, client = Depends(get_hubspot_client)):
#     try:
#         # Fetch the deal by ID with the specified properties
#         api_response = client.crm.deals.basic_api.get_by_id(
#             deal_id=deal_id,
#             properties=["amount", "dealstage", "dealname", "pipeline"],
#             archived=False
#         )
#         # Convert the response to a dictionary
#         api_response_dict = api_response.to_dict()

#         # Access the properties dictionary directly
#         properties_dict = api_response_dict.get('properties', {})

#         # Fetch line items associated with the deal
#         line_items_response = client.crm.line_items.basic_api.get_page(
#             associations={'deal': deal_id}
#         )
#         # Extract the line item IDs from the response
#         line_item_ids = [item.id for item in line_items_response.results]

#         # Create a response model instance with the necessary fields
#         response = DealResponse(
#             id=api_response_dict['id'],
#             name=properties_dict.get('dealname', ''),
#             stage=properties_dict.get('dealstage', ''),
#             amount=properties_dict.get('amount',   0.0),
#             pipeline=properties_dict.get('pipeline', ''),
#             line_items=line_item_ids  # Include only the line item IDs
#         )
#         return response
#     except ApiException as e:
#         # Log the exception for debugging purposes
#         # Replace 'print' with a proper logging framework
#         print(f"ApiException: {e}")
#         raise HTTPException(status_code=400, detail=str(e))

# from fastapi import APIRouter, Depends, HTTPException
# from hubspot.crm.deals import ApiException
# from ....dependencies.hubspot_auth import get_hubspot_client
# from pydantic import BaseModel

# # Initialize the router
# router = APIRouter()

# class DealResponse(BaseModel):
#     # Define the fields you want to include in the response
#     id: str
#     name: str
#     stage: str
#     amount: float
#     pipeline: str
#     line_items: list

# @router.get("/deals/{deal_id}", response_model=DealResponse)
# async def get_deal(deal_id: str, client = Depends(get_hubspot_client)):
#     try:
#         # Fetch the deal by ID with the specified properties
#         api_response = client.crm.deals.basic_api.get_by_id(
#             deal_id=deal_id,
#             properties=["amount", "dealstage", "dealname", "pipeline"],
#             archived=False
#         )
#         # Convert the response to a dictionary
#         api_response_dict = api_response.to_dict()

#         # Access the properties dictionary directly
#         properties_dict = api_response_dict.get('properties', {})

#         # Fetch line items associated with the deal
#         line_items_response = client.crm.line_items.basic_api.get_page(
#             associations={'deal': deal_id}
#         )
#         # Extract the line item IDs from the response
#         line_item_ids = [item.id for item in line_items_response.results]

#         # Create a response model instance with the necessary fields
#         response = DealResponse(
#             id=api_response_dict['id'],
#             name=properties_dict.get('dealname', ''),
#             stage=properties_dict.get('dealstage', ''),
#             amount=properties_dict.get('amount',   0.0),
#             pipeline=properties_dict.get('pipeline', ''),
#             line_items=line_item_ids  # Include only the line item IDs
#         )
#         return response
#     except ApiException as e:
#         # Log the exception for debugging purposes
#         # Replace 'print' with a proper logging framework
#         print(f"ApiException: {e}")
#         raise HTTPException(status_code=400, detail=str(e))
# this one worksfine:
# from fastapi import APIRouter, Depends, HTTPException
# from hubspot.crm.deals import ApiException
# from ....dependencies.hubspot_auth import get_hubspot_client
# from pydantic import BaseModel

# # Initialize the router
# router = APIRouter()

# class DealResponse(BaseModel):
#     # Define the fields you want to include in the response
#     id: str
#     name: str
#     stage: str
#     amount: float
#     pipeline: str
#     line_items: list

# @router.get("/deals/{deal_id}", response_model=DealResponse)
# async def get_deal(deal_id: str, client = Depends(get_hubspot_client)):
#     try:
#         # Fetch the deal by ID with the specified properties
#         api_response = client.crm.deals.basic_api.get_by_id(
#             deal_id=deal_id,
#             properties=["amount", "dealstage", "dealname", "pipeline"],
#             archived=False
#         )
#         # Convert the response to a dictionary
#         api_response_dict = api_response.to_dict()

#         # Access the properties dictionary directly
#         properties_dict = api_response_dict.get('properties', {})

#         # Fetch line items associated with the deal
#         line_items_response = client.crm.line_items.basic_api.get_page(associations={'deal': deal_id})
#         # Convert the line items into a serializable format
#         line_items = [item.to_dict() for item in line_items_response.results]

#         # Create a response model instance with the necessary fields
#         response = DealResponse(
#             id=api_response_dict['id'],
#             name=properties_dict.get('dealname', ''),
#             stage=properties_dict.get('dealstage', ''),
#             amount=properties_dict.get('amount',   0.0),
#             pipeline=properties_dict.get('pipeline', ''),
#             line_items=line_items
#         )
#         return response
#     except ApiException as e:
#         # Log the exception for debugging purposes
#         # Replace 'print' with a proper logging framework
#         print(f"ApiException: {e}")
#         raise HTTPException(status_code=400, detail=str(e))







# class DealResponse(BaseModel):
#     # Define the fields you want to include in the response
#     id: str
#     name: str
#     # ... other fields you want to include
#     line_items: list

# @router.get("/deals/{deal_id}", response_model=DealResponse)
# async def get_deal(deal_id: str, client = Depends(get_hubspot_client)):
#     try:
#         api_response = client.crm.deals.basic_api.get_by_id(deal_id=deal_id, archived=False)
#         # Convert the response to a dictionary
#         api_response_dict = api_response.to_dict()
#         # Fetch line items associated with the deal
#         line_items_response = client.crm.line_items.basic_api.get_page(associations={'deal': deal_id})
#         # Convert the line items into a serializable format
#         line_items = [item.to_dict() for item in line_items_response.results]
#         # Create a response model instance with the necessary fields
#         response = DealResponse(id=api_response_dict['id'], name=api_response_dict.get('name', ''), line_items=line_items)
#         return response
#     except ApiException as e:
#         # Log the exception for debugging purposes
#         # Replace 'print' with a proper logging framework
#         print(f"ApiException: {e}")
#         raise HTTPException(status_code=400, detail=str(e))

# # Define the endpoint to fetch deal data by ID
# # @router.get("/deals/{deal_id}")
# # async def get_deal(deal_id: str, client = Depends(get_hubspot_client)):
# #     try:
# #         api_response = client.crm.deals.basic_api.get_by_id(deal_id=deal_id, archived=False)
# #         # Check if the response is a dictionary
# #         if isinstance(api_response, dict):
# #             return api_response
# #         else:
# #             # If the response is not a dictionary, attempt to convert it to a dictionary
# #             # This assumes that the response object has a to_dict() method
# #             if hasattr(api_response, 'to_dict'):
# #                 return api_response.to_dict()
# #             else:
# #                 # If the response cannot be converted to a dictionary, raise an appropriate error
# #                 raise TypeError(f"Expected a dictionary, got {type(api_response).__name__} instead.")
# #     except ApiException as e:
# #         # Log the exception for debugging purposes
# #         print(f"ApiException: {e}")
# #         raise HTTPException(status_code=400, detail=str(e))