# video-to-mp3-backend

This is an async backend service for extracting MP3 from videos. The videos are uploaded to object storage (**MinIO**) and processed in the background using **Celery** workers with **RabbitMQ** acting as a message broker.


#### Tech Stack
- FastAPI
- MinIO for storing videos and processed MP3s
- Celery + RabbitMQ for background processing
- PostgreSQL for storing job conversion data

#### Background Processing Flow

1. User uploads a video via FastAPI
2. Video is stored in MinIO
3. A conversion job record is created in PostgreSQL
4. FastAPI enqueues a Celery task using RabbitMQ
5. Celery worker:
   - downloads the video from MinIO
   - extracts audio using FFmpeg
   - uploads the resulting MP3 back to MinIO
   - updates the job status in PostgreSQL


#### Architecture Diagram
![mermaid diagram](./architecture.svg)

#### Endpoints

| Method | Endpoint                    | Auth  | Description                                     |
| ------ | --------------------------- | ----- | ----------------------------------------------- |
| `POST` | `/media/upload`             | YES   | Upload a video file and create a conversion job |
| `GET`  | `/media/{job_id}/status`    | YES   | Get the status of a conversion job              |
| `GET`  | `/media/{job_id}/download`  | YES   | Download the converted MP3 file                 |
| `POST` | `/auth/register`            | NO    | Register a new user                             |
| `POST` | `/auth/login`               | NO    | Authenticate user and return access token       |

1. `POST /media/upload`
Upload a video file to object storage and queue a background conversion job.

- Consumes: `multipart/form-data`
- Allowed formats: `mp4`, `mkv`, `webm`
- Returns: `ConversionJob`
```json
{
  "id": "e28ecc98-b148-4c28-8af1-cee7c5d8747f",
  "status": "PENDING",
  "created_at": "2026-01-28T12:23:19.271914",
  "error": null
}
```

2. `GET /media/{job_id}/status`
Fetches the current status of a conversion job owned by the authenticated user.

Possible statuses:
- PENDING
- PROCESSING
- FAILED
- DONE

3. `GET /media/{job_id}/download`
Downloads the processed MP3 file.

Possible errors:
- Job does not exist or does not belong to the user
- Job is not completed yet
- Output MP3 not found
- Storage access or permission error


#### How to Setup Locally

**Requirements**
- Python 3.13+
- Docker
- PostgreSQL 17+
- Make

1. Clone the repo and cd into  it

2. Set up venv and download the dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Run the migrations
```bash
alembic upgrade head
``` 

4. Configure environment variables in a `.env` file:
```bash
APP_NAME="Video to MP3 Converter"
ENV=development          # development | staging | production
DEBUG=false
LOG_LEVEL=INFO

DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/converter

SECRET_KEY=supersecretkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

STORAGE_ENDPOINT=localhost:9000
STORAGE_ACCESS_KEY=minioadmin
STORAGE_SECRET_KEY=minioadmin
STORAGE_SECURE=false
STORAGE_BUCKET_NAME=media

RABBITMQ_URL=amqp://guest:guest@localhost:5672//
```

4. Pull and run RabbitMQ and MinIO images from docker hub.

5. Run celery app and server
```bash
make run/celery
```
```bash
make run/app
```