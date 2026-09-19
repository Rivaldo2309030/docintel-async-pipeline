from celery import Celery
from config import settings

celery_app = Celery(
    "docintel_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["tasks.document_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Failure handling & worker crash resilience settings
    task_acks_late=True,  # Ensure task is re-queued if worker crashes mid-task
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,  # Prevent worker from hoarding un-processed tasks
    task_time_limit=300,  # Hard timeout 5 minutes
    task_soft_time_limit=270,  # Soft timeout
)
