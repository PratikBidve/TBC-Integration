from fastapi import APIRouter
from celery import Celery
import os
from dotenv import load_dotenv
import app.tasks.deal_tasks
import app.tasks.new_deal_tasks


load_dotenv()

router = APIRouter()

app = Celery('tasks', broker=os.getenv('BROKER_URL'), backend=os.getenv('CELERY_RESULT_BACKEND'))

# Set the broker_connection_retry_on_startup setting to True
app.conf.broker_connection_retry_on_startup = True

# Optional: Load task modules when the worker starts.
app.autodiscover_tasks(['app.tasks'])
