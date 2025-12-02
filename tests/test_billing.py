from fastapi.testclient import TestClient
from src.api.main import app
from src.api.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.api.database import get_db
import pytest
import os

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_billing.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # Cleanup file
    if os.path.exists("./test_billing.db"):
        os.remove("./test_billing.db")

def test_get_plans():
    # Plans are seeded on first get
    response = client.get("/billing/plans")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert data[0]['name'] == "Basic"

client = TestClient(app)
