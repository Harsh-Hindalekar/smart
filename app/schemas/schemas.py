from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional


# -----------------------------
# User Schemas
# -----------------------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    username: str
    created_at: datetime

    class Config:
        from_attributes = True
