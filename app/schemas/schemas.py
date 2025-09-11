from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    # email: EmailStr
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    username: str
    created_at: datetime  

    class Config:
        orm_mode = True
