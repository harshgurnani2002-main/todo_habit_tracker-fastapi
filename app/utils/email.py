import random
import string
import redis
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.config import get_settings

settings = get_settings()

# Redis client for OTP storage
redis_client = redis.from_url(settings.redis_url)

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fastmail = FastMail(conf)

def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))

async def send_otp_email(email: str) -> bool:
    try:
        otp = generate_otp()
        
        # Store OTP in Redis with 5-minute expiration
        redis_client.setex(f"otp:{email}", 300, otp)
        
        html_content = f"""
        <html>
            <body>
                <h2>Your OTP Code</h2>
                <p>Your one-time password is: <strong>{otp}</strong></p>
                <p>This code will expire in 5 minutes.</p>
                <p>If you didn't request this code, please ignore this email.</p>
            </body>
        </html>
        """
        
        message = MessageSchema(
            subject="Your OTP Code - Todo Habit Tracker",
            recipients=[email],
            body=html_content,
            subtype="html"
        )
        
        await fastmail.send_message(message)
        return True
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        return False

async def send_password_reset_email(email: str, reset_link: str) -> bool:
    try:
        html_content = f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You have requested to reset your password. Click the link below to reset your password:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </body>
        </html>
        """
        
        message = MessageSchema(
            subject="Password Reset - Todo Habit Tracker",
            recipients=[email],
            body=html_content,
            subtype="html"
        )
        
        await fastmail.send_message(message)
        return True
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False

def verify_otp(email: str, otp_code: str) -> bool:
    stored_otp = redis_client.get(f"otp:{email}")
    if stored_otp and stored_otp.decode() == otp_code:
        redis_client.delete(f"otp:{email}")  # Delete OTP after verification
        return True
    return False
