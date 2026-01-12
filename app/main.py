from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.database.db import wait_for_db
from app.api.routers import auth
from app.services.storage import StorageService
from app.api.routers import media
from app.domain.exceptions import StorageError, StoragePermissionError, StorageUnavailableError
from sys import exit

setup_logging()
logger = get_logger(__name__)

storage_service: StorageService | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.APP_NAME} starting in {settings.ENV} mode")

    wait_for_db()

    try:
        app.state.storage_service = StorageService()
        logger.info("Object Storage service initialized")
    except StoragePermissionError:
        logger.critical(f"Storage permission error at startup")
        exit(1)
    except StorageUnavailableError as e:
        logger.critical(f"Storage unavailable at startup")
        exit(1)
    except StorageError as e:
        logger.critical(f"Storage initialization failed")
        exit(1)

    yield
    logger.info("Application shutdown")


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.include_router(auth.router)
app.include_router(media.router)

@app.get("/")
def root():
    return {"message": f"video-to-mp3 app is running"}
