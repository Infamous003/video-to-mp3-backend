from app.services.storage import StorageService
from app.database.models.conversion_jobs import ConversionJob, JobStatus
from sqlmodel import Session
from sqlalchemy.exc import SQLAlchemyError 
from typing import BinaryIO

class UploadService:
    def __init__(self, queue, storage: StorageService, db: Session):
        self.storage = storage
        self.db = db
        self.queue = queue
    
    def upload_video(
        self,
        user_id: int,
        file: BinaryIO,
        filename: str,
        content_type: str,
    ) -> ConversionJob:
        """
        Uploads a video to object storage and creates a conversion job row
        """

        input_key = f"videos/{user_id}/{filename}"
        job = ConversionJob(
            user_id=user_id,
            input_key=input_key,
        )

        try:
            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)
        except SQLAlchemyError:
            self.db.rollback()
            raise

        try:
            file.seek(0)
            self.storage.upload_file(
                object_name=input_key,
                file=file,
                content_type=content_type,
            )

            self.queue.publish({
                "job_id": str(job.id),
            })
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            self.db.commit()
            raise

        return job
        