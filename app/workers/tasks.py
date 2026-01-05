from app.workers.celery_app import celery_app
from sqlmodel import Session
from app.database.db import engine
from app.services.conversion import ConversionService

@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def convert_video(self, job_id: str):
    with Session(engine) as db:
        service = ConversionService(db=db)
        service.process(job_id)