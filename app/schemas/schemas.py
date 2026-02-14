from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Any, List, Dict, Optional
import re

# -----------------------------
# User Schemas
# -----------------------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    username: str
    password: str

    @field_validator("name")
    @classmethod
    def name_valid(cls, v: str):
        v = (v or "").strip()
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        if len(v) > 50:
            raise ValueError("Name must be max 50 characters")
        return v

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str):
        v = (v or "").strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(v) > 30:
            raise ValueError("Username must be max 30 characters")
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can contain only letters, numbers, underscore")
        return v

    @field_validator("password")
    @classmethod
    def password_valid(cls, v: str):
        if v is None:
            raise ValueError("Password is required")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 64:
            raise ValueError("Password must be max 64 characters")
        # strong password (same as frontend)
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least 1 uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least 1 lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least 1 number")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("Password must contain at least 1 special character")
        return v


class UserLogin(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def username_login_valid(cls, v: str):
        v = (v or "").strip()
        if not v:
            raise ValueError("Username is required")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v

    @field_validator("password")
    @classmethod
    def password_login_valid(cls, v: str):
        if not v:
            raise ValueError("Password is required")
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    username: str
    created_at: datetime

    class Config:
        from_attributes = True

# -------------------------------------------------
# Google AI Drawing Schema (NEW — required)
# -------------------------------------------------
class Point(BaseModel):
    x: float
    y: float

class PointsRequest(BaseModel):
    points: List[Point]
    smoothing_window: Optional[int] = None
    simplify_eps: Optional[float] = None

    class Config:
        from_attributes = True
        orm_mode = True
