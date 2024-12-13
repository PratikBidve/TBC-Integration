from fastapi import APIRouter
from hubspot import Client
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

def get_hubspot_client():
    access_token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    if not access_token:
        raise ValueError("HUBSPOT_ACCESS_TOKEN must be set")
    client = Client.create(access_token=access_token)
    # Add line items retrieval functionality here if needed
    return client
