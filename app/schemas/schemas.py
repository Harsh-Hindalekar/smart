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


# -----------------------------
# Content Schemas
# -----------------------------
class ContentCreate(BaseModel):
    # title: str
    description: Optional[str] = None
    # type: str


class ContentResponse(BaseModel):
    # id: int
    # title: str
    description: Optional[str] = None
    # type: str
    user_id: str   # foreign key to User

    class Config:
        from_attributes = True


# -----------------------------
# Emergency Contact Schemas
# -----------------------------
class EmergencyContactCreate(BaseModel):
    helpline_name: str
    helpline_number: str


class EmergencyContactResponse(BaseModel):
    id: int
    helpline_name: str
    helpline_number: str

    class Config:
        from_attributes = True


# -----------------------------
# Nested Relationship Responses
# -----------------------------
class UserWithContents(UserResponse):
    contents: List[ContentResponse] = []  # user -> list of content
