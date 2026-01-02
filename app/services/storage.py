from minio import Minio
from minio.error import S3Error
from app.core.config import settings
from app.domain.exceptions import StorageError
from typing import BinaryIO

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
        content_type: str) -> None:
        """
        Uploads a file to an object storage like MinIO or S3.
        """

        try:
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=file,
                length=-1,  # -1 means unknown size, minio will handle it
                content_type=content_type
            )
        except S3Error as e:
            raise StorageError(f"Failed to upload file {object_name}: {e}") from e
    
    def download_file(self, object_name: str) -> bytes:
        """
        Downloads a file from the object storage.
        """

        response = None
        try:
            response = self.client.get_object(
                bucket_name=self.bucket,
                object_name=object_name
            )
            return response.read()
        except S3Error as e:
            raise StorageError(f"Failed to download file {object_name}: {e}") from e
        finally:
            if response:
                response.close()
                response.release_conn()