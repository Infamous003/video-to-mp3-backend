from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.database.db import wait_for_db
from app.api.routers import auth
from app.services.storage import StorageService

setup_logging()
logger = get_logger(__name__)

storage_service: StorageService | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.APP_NAME} starting in {settings.ENV} mode")
    
    wait_for_db()

    app.state.storage_service = StorageService()
    logger.info("Object Storage service initialized")
    yield
    logger.info("Application shutdown")

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.include_router(
    auth.router
)

@app.get("/")
def root():
    return {"message": f"video-to-mp3 app is running"}
