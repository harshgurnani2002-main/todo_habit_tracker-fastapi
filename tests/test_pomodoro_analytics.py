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

def test_pomodoro_analytics_with_data(client, db, test_user, auth_headers):
    # Create some pomodoro sessions
    for i in range(3):
        session = PomodoroSession(
            title=f"Test Session {i}",
            description=f"Description {i}",
            duration=25,
            owner_id=test_user.id,
            created_at=datetime.now() - timedelta(days=i)
        )
        db.add(session)
    
    # Create a completed session
    completed_session = PomodoroSession(
        title="Completed Session",
        description="Completed description",
        duration=30,
        completed_at=datetime.now(),
        owner_id=test_user.id,
        created_at=datetime.now()
    )
    db.add(completed_session)
    db.commit()
    
    # Test analytics endpoint
    response = client.get("/pomodoro/analytics", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_sessions"] == 4
    assert data["completed_sessions"] == 1
    assert data["completion_rate"] >= 0
    assert data["average_duration"] >= 0
    assert data["total_time"] >= 0

def test_pomodoro_analytics_empty(client, db, test_user, auth_headers):
    # Test analytics endpoint with no sessions
    response = client.get("/pomodoro/analytics", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_sessions"] == 0
    assert data["completed_sessions"] == 0
    assert data["completion_rate"] == 0
    assert data["average_duration"] == 0
    assert data["total_time"] == 0