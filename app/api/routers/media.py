from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from app.api.deps import get_db, get_current_user, get_storage_service
from app.services.media import MediaService
from app.services.storage import StorageService
from app.database.models.user import User
from app.schemas.conversion_jobs import ConversionJobRead
from uuid import UUID
from app.domain.exceptions import (
    ConversionJobNotFoundException,
    JobNotCompletedException,
    ObjectNotFoundError,
    StoragePermissionError,
    StorageUnavailableError,
    StorageError
)

router = APIRouter(prefix="/uploads", tags=["uploads"])

@router.post("/")
def upload_video(
    file: UploadFile,
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage_service),
    current_user: User = Depends(get_current_user),
):
    service = MediaService(db=db, storage=storage)

    try:
        job = service.upload_video(
            user_id=current_user.id,
            file=file.file,
            filename=file.filename,
            content_type=file.content_type,
        )
        return job

    except StoragePermissionError:
        raise HTTPException(403, "Storage access denied")

    except StorageUnavailableError:
        raise HTTPException(503, "Storage unavailable")

    except StorageError:
        raise HTTPException(500, "Failed to upload video")


@router.get("/{id}")
def get_upload_status(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage: StorageService = Depends(get_storage_service),
) -> ConversionJobRead:
    service = MediaService(db=db, storage=storage)

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

@router.get("/{id}/download")
def download_mp3(
    id: UUID,
    db: Session = Depends(get_db),
    storage: StorageService = Depends(get_storage_service),
    current_user: User = Depends(get_current_user),
):
    service = MediaService(db=db, storage=storage)

    try:
        mp3_stream = service.download_mp3(
            job_id=id,
            user_id=current_user.id,
        )
        return StreamingResponse(
            iter_file(mp3_stream),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f'attachment; filename="{id}.mp3"',
                "Accept-Ranges": "bytes",
            },
        )
    except ConversionJobNotFoundException:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")
    
    except JobNotCompletedException:
        raise HTTPException(status.HTTP_409_CONFLICT, "Job is not finished yet")
    
    except ObjectNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "MP3 not found")
    
    except StoragePermissionError:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Storage access denied")

    except StorageUnavailableError:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Storage unavailable")

    except StorageError:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Storage error")


def iter_file(obj):
    try:
        yield from obj.stream(32 * 1024)
    finally:
        obj.close()
        obj.release_conn()