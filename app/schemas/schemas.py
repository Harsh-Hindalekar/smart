from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Any, List,Dict, Optional

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

# -------------------------------------------------
# Google AI Drawing Schema (NEW — required)
# -------------------------------------------------
class Point(BaseModel):
    x: float
    y: float

class PointsRequest(BaseModel):
    points: List[Point]
    # optional tuning params
    smoothing_window: Optional[int] = None
    simplify_eps: Optional[float] = None

    
    class Config:
        from_attributes = True
        orm_mode = True