from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = False
    hashed_password: Optional[str] = None

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class RespUser(BaseModel):
    id: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str]
    is_active: Optional[bool] = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class User(BaseModel):
    hashed_password: Optional[str] = None
    email: Optional[EmailStr] = None


class UserCreateInput(BaseModel):
    email: EmailStr
    name: str
    password: str


class ChangePassword(BaseModel):
    old_password: Optional[str] = None
    new_password: Optional[str] = None


class LoginInput(BaseModel):
    email: EmailStr
    password: str