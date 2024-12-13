from fastapi import APIRouter, Response, HTTPException
from app.dependencies.airtable_auth import table_instance
from typing import List

router = APIRouter()

@router.get("/filtered_airtable_data")
async def get_product_info(product_code: str) -> List[dict]:
    try:
        # Create a formula to filter on the extracted product code
        formula = f"{{Code}} = '{product_code}'"

        # Fetch filtered data from Airtable
        airtable_data = [record for record in table_instance.iterate(formula=formula)]

        return airtable_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching filtered Airtable data: {str(e)}")


# from fastapi import APIRouter, Response, HTTPException
# from app.dependencies.airtable_auth import table_instance
# from fastapi import APIRouter

# router = APIRouter()

# airtable_data = []

# product_code = "Burger Box-1067521"

# @router.get("/filtered_airtable_data")
# async def get_stock_info():
#         # Create a formula to filter on the extracted product code 
#         formula = f"{{Code}} = '{product_code}'"

#         for record in table_instance.iterate(formula=formula):
#             airtable_data.append(record)

#         return airtable_data
