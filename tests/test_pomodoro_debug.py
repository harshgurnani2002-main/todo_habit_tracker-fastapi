import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from app.models.user import User
from app.models.pomodoro import PomodoroSession
from app.utils.security import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user(db):
    hashed_password = get_password_hash("testpassword")
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed_password,
        is_verified=True  # User must be verified to login
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, test_user):
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_pomodoro_analytics_debug(client, db, test_user, auth_headers):
    # Test analytics endpoint and print detailed error
    response = client.get("/pomodoro/analytics", headers=auth_headers)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200