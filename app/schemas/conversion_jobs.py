from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from app.database.models.conversion_jobs import JobStatus

class ConversionJobRead(BaseModel):
    id: UUID
    status: JobStatus
    created_at: datetime

    class Config:
        from_attributes = True
