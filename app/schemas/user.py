from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email:EmailStr
    full_name:Optional[str]=None   
    username:Optional[str]=None


class UserCreate(UserBase):
    password:str=None


class UserUpdate(UserBase):
    full_name:Optional[str]=None 
    username:Optional[str]=None


class User(UserBase):
    id:int
    is_active:bool
    is_verified:bool
    is_admin:bool
    profile_picture:Optional[str]=None
    created_at:datetime

    class Config:
        from_attributes=True


class UserInDB(User):
    hashed_password:str


class Token(BaseModel):
    access_token:str
    token_type:str


class TokenData(BaseModel):
    email:Optional[str]=None


class LoginRequest(BaseModel):
    email:EmailStr
    password:str


class OTPRequest(BaseModel):
    email:EmailStr


class OTPVerify(BaseModel):
    email:EmailStr
    otp_code:str


    