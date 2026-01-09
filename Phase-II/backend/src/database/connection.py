from sqlmodel import create_engine, Session
from typing import Generator
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

# Use database from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./phase_ii_app.db")

# Create engine with appropriate settings
engine = create_engine(
    DATABASE_URL,
    # Additional settings
    echo=True  # Enable SQL logging for debugging
)

@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    Ensures session is properly closed after use.
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_session_dep():
    """
    FastAPI dependency for database sessions.
    """
    with get_session() as session:
        yield session