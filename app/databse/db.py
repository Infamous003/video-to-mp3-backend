# app/db/db.py
from sqlmodel import create_engine, Session, text
from time import sleep
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # log SQL statements if in debug mode
)


def wait_for_db(retries: int = 5, delay: int = 3):
    """
    Wait for the database to become available before starting the app.

    Args:
        retries (int): Number of retry attempts
        delay (int): Seconds to wait between retries
    """
    logger.info("Waiting for the DB availability...")
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("DB is available.")
                return
        except Exception as e:
            logger.warning(f"DB is not available (attempt {attempt}/{retries}): {e}")
            if attempt < retries:
                sleep(delay)
            else:
                logger.error("DB not available after maximum retries")
                raise


def get_db():
    """
    Dependency that provides a DB session.
    """
    with Session(engine) as session:
        yield session
