from celery import Celery
from app.core.config import settings

# Initialize the Celery application
celery_app = Celery(
    "tx_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"] # Tell Celery where to find our task functions
)

# Standard configuration for JSON serialization
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)