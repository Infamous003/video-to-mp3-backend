import subprocess
import tempfile
import os
from sqlmodel import Session, select
from app.database.models.conversion_jobs import ConversionJob, JobStatus
from app.services.storage import StorageService
from app.domain.errors import ConversionError
from app.domain.exceptions import (
    ConversionFailedException,
    StorageError
)

class ConversionService:
    def __init__(self, db: Session, storage: StorageService | None = None):
        self.db = db
        self.storage = storage or StorageService()


    def process(self, job_id: str) -> None:
        job = self.db.exec(
            select(ConversionJob).where(ConversionJob.id == job_id)
        ).first()

        if not job:
            return

        job.status = JobStatus.PROCESSING
        self.db.commit()

        try:
            output_key = self._convert(job)
            job.output_key = output_key
            job.status = JobStatus.DONE

        except ConversionFailedException as e:
            job.status = JobStatus.FAILED
            job.error = ConversionError.FFMPEG_FAILED

        except StorageError as e:
            job.status = JobStatus.FAILED
            job.error = ConversionError.STORAGE_ERROR

        except Exception:
            job.status = JobStatus.FAILED
            job.error = ConversionError.UNKNOWN_ERROR
            raise 

        finally:
            self.db.commit()


    def _convert(self, job: ConversionJob) -> str:
        # ffmpeg only works with directories
        # So, we download the video from minio, save it to temp dir
        # Then use ffmpeg to process it, and save the mp3 back to temp dir
        # Then, we open this mp3 in read-binary mode, and upload to minio
        with tempfile.TemporaryDirectory() as tmp:
            input_path = os.path.join(tmp, "input")
            output_path = os.path.join(tmp, "output.mp3")

            self._download_to_file(job.input_key, input_path)
            self._run_ffmpeg(input_path, output_path)

            output_key = f"audio/{job.user_id}/{job.id}.mp3"
            self._upload_mp3(output_path, output_key)

            return output_key


    def _download_to_file(self, key: str, path: str) -> None:
        obj = self.storage.download_file(key)
        try:
            with open(path, "wb") as f:
                for chunk in obj.stream(32 * 1024):
                    f.write(chunk)
        finally:
            obj.close()
            obj.release_conn()
        

    def _upload_mp3(self, path: str, key: str) -> None:
        with open(path, "rb") as f:
            self.storage.upload_file(
                object_name=key,
                file=f,
                content_type="audio/mpeg",
            )


    def _run_ffmpeg(self, input_path: str, output_path: str) -> None:
        cmd = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-vn",
            "-acodec", "libmp3lame",
            output_path,
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            raise ConversionFailedException(
                f"ffmpeg failed: {result.stderr.strip()}"
            )

