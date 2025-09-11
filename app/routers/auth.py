from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema, Token, LoginRequest, OTPRequest, OTPVerify
from app.utils.security import (
    verify_password, get_password_hash, create_access_token, 
    generate_otp_secret, generate_qr_code, verify_otp_code
)
from app.utils.email import send_otp_email, verify_otp
from app.auth.google_oauth import google_oauth
from app.auth.dependencies import get_current_user
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["authentication"])

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

# Login with email/password
@router.post("/login", response_model=Token)
async def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if 2FA is enabled
    if user.is_2fa_enabled:
        if not login_data.otp_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP code required"
            )
        if not verify_otp_code(user.otp_secret, login_data.otp_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid OTP code"
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
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Enable 2FA
@router.post("/enable-2fa")
async def enable_2fa(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.is_2fa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA already enabled"
        )
    
    # Generate secret and QR code
    secret = generate_otp_secret()
    qr_code = generate_qr_code(current_user.email, secret)
    
    # Save secret (temporarily, until user verifies)
    current_user.otp_secret = secret
    db.commit()
    
    return {
        "secret": secret,
        "qr_code": qr_code,
        "message": "Scan the QR code with your authenticator app and verify with an OTP"
    }

# Verify 2FA setup
@router.post("/verify-2fa")
async def verify_2fa_setup(
    otp_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.otp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA setup not initiated"
        )
    
    if not verify_otp_code(current_user.otp_secret, otp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP code"
        )
    
    # Enable 2FA
    current_user.is_2fa_enabled = True
    db.commit()
    
    return {"message": "2FA enabled successfully"}

# Get current user info
@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user
