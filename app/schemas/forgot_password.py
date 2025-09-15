from pydantic import BaseModel, EmailStr
from typing import Optional

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class PasswordResetToken(BaseModel):
    email: EmailStr
    token: str
    expires_at: int

    class Config:
        from_attributes = True