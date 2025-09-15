from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import pyotp
import qrcode
from io import BytesIO
import base64
from app.config import get_settings

settings = get_settings()

# Configure passlib to use bcrypt with explicit version handling
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None

def generate_otp_secret():
    return pyotp.random_base32()

def generate_qr_code(email: str, secret: str):
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=email,
        issuer_name=settings.app_name
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    qr_image = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    qr_image.save(buffer, format="PNG")
    buffer.seek(0)
    
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{qr_code_base64}"

def verify_otp_code(secret: str, otp_code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(otp_code, valid_window=1)
