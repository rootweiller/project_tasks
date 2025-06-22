from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Initialize the database by creating all tables according to the defined models.

    This function should be called once when the application is started.
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    FastAPI dependency that yields a database session.

    This dependency uses a context manager to ensure the database session is
    properly closed after it is used. The session is created with the
    `SessionLocal` class, which is a `sessionmaker` configured with the
    `DATABASE_URL` environment variable.

    Returns:
        SessionLocal: A database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()