from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import secrets
import redis
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema, Token, LoginRequest, OTPRequest, OTPVerify
from pydantic import BaseModel

class GoogleLoginRequest(BaseModel):
    id_token: str
from app.schemas.forgot_password import ForgotPasswordRequest, ResetPasswordRequest
from app.utils.security import (
    verify_password, get_password_hash, create_access_token
)
from app.utils.email import send_otp_email, verify_otp
from app.auth.google_oauth import google_oauth
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from app.auth.dependencies import get_current_user
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["authentication"])

# Redis client for password reset tokens
redis_client = redis.from_url(settings.redis_url)

# Traditional email/password registration
@router.post("/register", response_model=UserSchema)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password) if user.password else None
    db_user = User(
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

from datetime import datetime, timedelta
# Login with email/password
@router.post("/login", response_model=Token)
async def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Google OAuth2 login URL
@router.get("/google/login")
async def google_login():
    login_url = google_oauth.get_login_url()
    return {"url": login_url}

# Google OAuth2 callback
@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    try:
        user_info = await google_oauth.get_user_info(code)
        
        # Check if user exists
        user = db.query(User).filter(User.email == user_info["email"]).first()
        
        if not user:
            # Create new user from Google info
            user = User(
                email=user_info["email"],
                full_name=user_info.get("name"),
                google_id=user_info["id"],
                profile_picture=user_info.get("picture"),
                is_verified=user_info.get("verified_email", False)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update existing user's Google info
            user.google_id = user_info["id"]
            user.profile_picture = user_info.get("picture")
            if user_info.get("verified_email"):
                user.is_verified = True
            db.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {str(e)}"
        )

# Send OTP via email
@router.post("/send-otp")
async def send_otp(request: OTPRequest):
    success = await send_otp_email(request.email)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP"
        )
    return {"message": "OTP sent successfully"}

# Verify OTP and login
@router.post("/verify-otp", response_model=Token)
async def verify_otp_login(request: OTPVerify, db: Session = Depends(get_db)):
    if not verify_otp(request.email, request.otp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP code"
        )
    
    # Check if user exists, create if not
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        user = User(
            email=request.email,
            is_verified=True  # Email verified via OTP
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Update last OTP verified time
    user.last_otp_verified = datetime.now(datetime.timezone.utc)
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Forgot password - send reset token
@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # We don't reveal if the email exists for security reasons
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    token_key = f"password_reset:{reset_token}"
    
    # Store token in Redis with 1-hour expiration
    redis_client.setex(token_key, 3600, request.email)
    
    # Send reset email
    reset_link = f"{settings.app_url}/reset-password?token={reset_token}"
    
    # Send email
    from app.utils.email import send_password_reset_email
    success = await send_password_reset_email(request.email, reset_link)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reset email"
        )
    
    return {"message": "If the email exists, a reset link has been sent"}

# Reset password with token
@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_key = f"password_reset:{request.token}"
    
    # Check if token exists
    email = redis_client.get(token_key)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    email = email.decode()
    
    # Get user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is a Google user (no password)
    if user.google_id and not user.hashed_password:
        # For Google users, we still allow password reset to enable email/password login
        pass
    
    # Hash new password
    hashed_password = get_password_hash(request.new_password)
    user.hashed_password = hashed_password
    
    # Save changes
    db.commit()
    
    # Delete token
    redis_client.delete(token_key)
    
    return {"message": "Password reset successfully"}

# Get current user info
@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Google ID token login
@router.post("/google", response_model=Token)
async def google_id_token_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(request.id_token, google_requests.Request(), settings.google_client_id)

        # ID token is valid. Get the user's Google Account information from the decoded token.
        userid = idinfo['sub']
        email = idinfo['email']
        name = idinfo.get('name')
        picture = idinfo.get('picture')
        verified_email = idinfo.get('email_verified', False)

        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create new user from Google info
            user = User(
                email=email,
                full_name=name,
                google_id=userid,
                profile_picture=picture,
                is_verified=verified_email
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update existing user's Google info
            user.google_id = userid
            user.profile_picture = picture
            if verified_email:
                user.is_verified = True
            db.commit()
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except ValueError:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ID token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {str(e)}"
        )
