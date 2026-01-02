from sqlmodel import SQLModel, Field
from enum import Enum
from datetime import datetime, timezone
from uuid import UUID, uuid4

class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"

class ConversionJob(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(index=True)

    input_key: str
    output_key: str | None = None

    status: JobStatus = Field(default=JobStatus.PENDING)
    error: str | None = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
