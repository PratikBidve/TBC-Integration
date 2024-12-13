from fastapi import APIRouter, Depends, HTTPException
from hubspot.crm.line_items import ApiException  # Assuming this is the correct import for line items
from app.dependencies.hubspot_auth import get_hubspot_client

# Initialize the router
router = APIRouter()

# Define the endpoint to fetch line item data by ID
@router.get("/line_item/{line_item_id}")
async def get_line_item(line_item_id: str, client = Depends(get_hubspot_client)):
    try:
        api_response = client.crm.line_items.basic_api.get_by_id(line_item_id=line_item_id, properties=[ "name", "hs_sku", "price", "hs_discount_percentage", "quantity" ])
        # Check if the response is a dictionary
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
    except ApiException as e:
        # Log the exception for debugging purposes
        print(f"ApiException: {e}")
        raise HTTPException(status_code=400, detail=str(e))