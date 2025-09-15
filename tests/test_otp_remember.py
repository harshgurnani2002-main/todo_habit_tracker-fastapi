import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from app.models.user import User
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

def test_otp_not_required_within_24_hours(client, db):
    # Create a user with 2FA enabled and recently verified
    hashed_password = get_password_hash("testpassword")
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed_password,
        is_2fa_enabled=True,
        otp_secret="TESTSECRET",
        last_otp_verified=datetime.now()  # Recently verified
    )
    db.add(user)
    db.commit()
    
    # Try to login without OTP - should succeed
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    
    # Should succeed without OTP
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_otp_required_after_24_hours(client, db):
    # Create a user with 2FA enabled but verified more than 24 hours ago
    hashed_password = get_password_hash("testpassword")
    user = User(
        email="test2@example.com",
        username="testuser2",
        hashed_password=hashed_password,
        is_2fa_enabled=True,
        otp_secret="TESTSECRET",
        last_otp_verified=datetime.now() - timedelta(hours=25)  # Verified more than 24 hours ago
    )
    db.add(user)
    db.commit()
    
    # Try to login without OTP - should fail
    response = client.post("/auth/login", json={
        "email": "test2@example.com",
        "password": "testpassword"
    })
    
    # Should fail without OTP
    assert response.status_code == 400
    assert response.json()["detail"] == "OTP code required"

def test_otp_required_when_never_verified(client, db):
    # Create a user with 2FA enabled but never verified
    hashed_password = get_password_hash("testpassword")
    user = User(
        email="test3@example.com",
        username="testuser3",
        hashed_password=hashed_password,
        is_2fa_enabled=True,
        otp_secret="TESTSECRET"
        # last_otp_verified is None
    )
    db.add(user)
    db.commit()
    
    # Try to login without OTP - should fail
    response = client.post("/auth/login", json={
        "email": "test3@example.com",
        "password": "testpassword"
    })
    
    # Should fail without OTP
    assert response.status_code == 400
    assert response.json()["detail"] == "OTP code required"