from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlmodel import Session
from app.api.deps import get_db, get_current_user
from app.services.upload import UploadService
from app.services.queue.fake import FakeQueue
from app.services.storage import StorageService
from app.database.models.user import User
from app.schemas.conversion_jobs import ConversionJobRead

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