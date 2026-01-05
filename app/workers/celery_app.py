from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "video_to_mp3",
    broker=settings.RABBITMQ_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # <-- fixed typo
)

# Celery needs to know where task functions are defind
# It automatically looks for files named 'tasks.py'
celery_app.autodiscover_tasks(["app.workers"])