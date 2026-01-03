from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlmodel import Session
from app.api.deps import get_db, get_current_user
from app.services.upload import UploadService
from app.services.queue.fake import FakeQueue
from app.services.storage import StorageService
from app.database.models.user import User
from app.schemas.conversion_jobs import ConversionJobRead
from uuid import UUID
from app.domain.exceptions import ConversionJobNotFoundException

router = APIRouter(prefix="/uploads", tags=["uploads"])

queue = FakeQueue()
storage = StorageService()

@router.post("/")
def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversionJobRead:
    if not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only video files are allowed",
        )

    service = UploadService(
        queue=queue,
        storage=storage,
        db=db,
    )

    job = service.upload_video(
        user_id=current_user.id,
        file=file.file,
        filename=file.filename,
        content_type=file.content_type,
    )

    return job

@router.get("/{id}")
def get_upload_status(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversionJobRead:
    service = UploadService(db=db, storage=storage, queue=queue)

    try:
        job = service.get_status(
            job_id=id,
            user_id=current_user.id,
        )
        return job
    except ConversionJobNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )