from fastapi import APIRouter, Depends, HTTPException
from hubspot.crm.deals import ApiException
from app.dependencies.hubspot_auth import get_hubspot_client

# Initialize the router
router = APIRouter()

# Define the endpoint to fetch deal data by ID
@router.get("/deal/{deal_id}")
async def get_deal(deal_id: str, client = Depends(get_hubspot_client)):
    try:
        api_response = client.crm.deals.basic_api.get_by_id(deal_id=deal_id, properties=['dealname', 'amount', 'billing_address', 'billing_city', 'billing_postal_code', 'billing_country_region', 'delivery_address','delivery_city','delivery_country','delivery_zip', 'payment_condition','discount_percentage'], archived=False)
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