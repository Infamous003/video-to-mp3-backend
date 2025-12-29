from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging, get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.APP_NAME} starting in {settings.ENV} mode")
    yield
    logger.info("Application shutdown")

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

@app.get("/")
def root():
    return {"message": f"video-to-mp3 app is running"}
