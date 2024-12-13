from fastapi import APIRouter
from pyairtable import Api
from dotenv import load_dotenv
import os

load_dotenv() # Load environment variables from .env file

router = APIRouter()

# Initialize the Airtable API with your API key
AIRTABLE_API_KEY = os.getenv('AIRTABLE_TOKEN')
BASE_ID = 'appTsax2s2zTojeRk'
TABLE_NAME = 'tblIEIVROLNVJ393x'

# Define table_instance at the module level
api_instance = Api(AIRTABLE_API_KEY)
table_instance = api_instance.table(BASE_ID, TABLE_NAME)


@router.get("/airtable")
async def get_airtable_data():
    try:
        airtable_data = []
        for records in table_instance.iterate(page_size=100, max_records=10):
            airtable_data.append(records)

        return {"airtable_data": airtable_data}
    except Exception as e:
        return {"error": f"Failed to fetch Airtable data: {str(e)}"}

    
# from pyairtable import Api
# from dotenv import load_dotenv
# import os
# import logging

# load_dotenv() # Load environment variables from .env file

# # Initialize the Airtable API with your API key
# AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
# BASE_ID = os.getenv('AIRTABLE_BASE_ID')
# TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')

# def fetch_airtable_records():
#     api = Api(AIRTABLE_API_KEY)
#     table = api.table(BASE_ID, TABLE_NAME)

#     try:
#         records = table.all()
#         logging.info(f"Fetched {len(records)} records from Airtable.")
#     except Exception as e:
#         logging.error(f"Failed to fetch records from Airtable: {e}")

#     try:
#         for record in table.iterate(page_size=50, max_records=10):
#             logging.info(record)
#     except Exception as e:
#         logging.error(f"Failed to iterate over records: {e}")

# # Call the function to fetch records
# fetch_airtable_records()

# def get_product_info(product_id):
#     """Fetch product information from Airtable based on the product ID."""
#     # Replace 'Product ID' with the actual field name in your Airtable base
#     record = table.search('Product ID', product_id)[0]
#     return record['fields']

# def update_product_info(record_id, updated_fields):
#     """Update product information in Airtable."""
#     table.update(record_id, updated_fields)

# def create_new_product(product_data):
#     """Create a new product record in Airtable."""
#     table.insert(product_data)

# Add other functions as needed for your operations

