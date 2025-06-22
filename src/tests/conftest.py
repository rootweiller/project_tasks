import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api import app
from src.database import get_db
from src.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True
)

TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

@pytest.fixture(scope="session")
def connection():
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        yield conn
    # Limpia después de los tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db(connection):
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()

@pytest.fixture()
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
