from fastapi import FastAPI, HTTPException, Form
from .api.hubspot.endpoints.get_line_items_by_deal_id import router as line_items_router
from .api.hubspot.endpoints.get_companies_by_deal_id import router as companies_info_router
from .api.hubspot.endpoints.get_contacts_by_deal_id import router as contacts_info_router
from .api.hubspot.endpoints.get_products_by_deal_id import router as products_info_router
from .api.hubspot.endpoints.company_info import router as company_info_router
from .api.hubspot.endpoints.deal_info import router as deal_info_router
from .api.hubspot.endpoints.product_info import router as product_info_router 
from .api.hubspot.endpoints.line_item_info import router as line_item_router
from .api.hubspot.endpoints.contact_info import router as contact_info_router
from .api.hubspot.endpoints.owner_info import router as owner_info_router
from .dependencies.hubspot_auth import router as hubspot_auth
from .dependencies.celery import router as celry_auth
from app.tasks.deal_tasks import get_line_items_and_create_customers
from app.tasks.new_deal_tasks import get_line_items_and_create_customers_v2

from typing import Optional
from pydantic import BaseModel
import logging

#Middleware
from .middleware.logging import LoggingMiddleware
logger = logging.getLogger(__name__)


app = FastAPI()


class WebhookPayloadForm(BaseModel):
    dealID: int


@app.get("/")
async def root():
   return {"Hey, Brandie!"}


@app.post("/trigger-line-items-task/{deal_id}")
async def trigger_line_items_task(deal_id: str):
    task = get_line_items_and_create_customers.delay(deal_id)
    return {"message": "Task triggered", "task_id": task.id}


@app.post("/trigger-line-items-task_v2/{deal_id}")
async def trigger_line_items_task(deal_id: str):
    task = get_line_items_and_create_customers_v2.delay(deal_id)
    return {"message": "Task triggered", "task_id": task.id}

@app.post("/webhook")
async def hubspot_webhook(dealID: int = Form(...)):
    if dealID:
        # Log that a webhook was received with the deal ID
        logger.info(f"Received webhook with deal ID: {dealID}")
        
        # Trigger the Celery task with the deal ID
        # Assuming get_line_items_and_create_customers is correctly defined and imported
        get_line_items_and_create_customers.delay(dealID)
        
        # Log that the task was successfully triggered
        logger.info(f"Triggered get_line_items_and_create_customers task for deal ID: {dealID}")
        
        return {"status": "success"}
    else:
        # Log that the deal ID was not found in the payload
        logger.error("Deal ID not found in payload")
        raise HTTPException(status_code=422, detail="Deal ID not found in payload")

# Middleware
app.add_middleware(LoggingMiddleware)

# Routers
app.include_router(hubspot_auth)
app.include_router(celry_auth)
app.include_router(line_items_router)
app.include_router(companies_info_router)
app.include_router(contacts_info_router)
app.include_router(products_info_router)
app.include_router(line_item_router)
app.include_router(company_info_router)
app.include_router(contact_info_router)
app.include_router(product_info_router)
app.include_router(deal_info_router)
app.include_router(owner_info_router)
app.include_router(owner_info_router)





