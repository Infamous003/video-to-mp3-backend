from minio import Minio
from minio.error import S3Error
from app.core.config import settings
from app.domain.exceptions import (
    StorageError, 
    ObjectNotFoundError, 
    StoragePermissionError, 
    StorageUnavailableError,
)
from typing import BinaryIO, IO
import os
from urllib3.exceptions import MaxRetryError, NewConnectionError


class StorageService:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.STORAGE_ENDPOINT,
            access_key=settings.STORAGE_ACCESS_KEY,
            secret_key=settings.STORAGE_SECRET_KEY,
            secure=settings.STORAGE_SECURE,
        )

        self.bucket = settings.STORAGE_BUCKET_NAME
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """
        Ensures that the storage bucket exists; creates it if it does not.
        """
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as e:
            raise StorageError(f"Failed to initialize storage: {e}") from e


    def upload_file(
        self,
        object_name: str,
        file: BinaryIO,
        content_type: str,
    ) -> None:
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)

        try:
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=file,
                length=size,
                content_type=content_type,
            )

        except S3Error as e:
            if e.code in ("AccessDenied", "InvalidAccessKeyId"):
                raise StoragePermissionError(
                    f"Access denied for object: {object_name}"
                ) from e

            if e.code in ("SlowDown", "ServiceUnavailable"):
                raise StorageUnavailableError(
                    "Object storage temporarily unavailable"
                ) from e

            raise StorageError(
                f"Failed to upload file {object_name}"
            ) from e
        
        except (MaxRetryError, NewConnectionError) as e:
            raise StorageUnavailableError("Object storage unavailable") from e


    def download_file(self, object_name: str) -> IO[bytes]:
        try:
            return self.client.get_object(
                bucket_name=self.bucket,
                object_name=object_name,
            )

        except S3Error as e:
            if e.code == "NoSuchKey":
                raise ObjectNotFoundError(
                    f"Object not found: {object_name}"
                ) from e

            if e.code in ("AccessDenied", "InvalidAccessKeyId"):
                raise StoragePermissionError(
                    f"Access denied for object: {object_name}"
                ) from e

            if e.code in ("SlowDown", "ServiceUnavailable"):
                raise StorageUnavailableError(
                    "Object storage temporarily unavailable"
                ) from e

            raise StorageError(
                f"Storage error while downloading {object_name}"
            ) from e
        
        except (MaxRetryError, NewConnectionError) as e:
            raise StorageUnavailableError("Object storage unavailable") from e

