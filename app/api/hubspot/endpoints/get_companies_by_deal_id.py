from fastapi import APIRouter, Depends, HTTPException
from hubspot.crm.associations.v4 import ApiException
from app.dependencies.hubspot_auth import get_hubspot_client

import logging

router = APIRouter()

# Set up the logger
logger = logging.getLogger(__name__)

@router.get("/deals/{deal_id}/companies", response_model=dict)
async def get_deal_companies(deal_id: str, client=Depends(get_hubspot_client)):
    try:
        api_response = client.crm.associations.v4.basic_api.get_page(object_type="Deals", object_id=deal_id, to_object_type="companies", limit=500)
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

