from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.crud import crud
from app.database import get_db
from app.models.models import User
from app.auth.auth import get_current_user
from datetime import timedelta
from app.auth.auth import create_token
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.schemas import (UserCreate, UserLogin, UserResponse, PointsRequest)
from app.services.google_ai import recognize_google   # NEW

ACCESS_TOKEN_EXPIRE_MINUTES = 1080

router = APIRouter()
# -----------------------------
# Register route 
# -----------------------------
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email) or crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Email or username already exists")
    new_user = crud.create_user(db, user.name, user.email, user.username, user.password)
    return new_user

# ----------------------------- 
# Login route 
# -----------------------------
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, form_data.username)
    if not db_user or not crud.verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": db_user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

#-------------------------------- 
#Profile route
#--------------------------------
@router.get("/user/profile", response_model=UserResponse)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    db_user = crud.get_user_by_id(db, current_user.id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# -----------------------------
# Google AI Drawing Recognition
# -----------------------------
@router.post("/recognize_google")
async def recognize_google_shape(
    req: PointsRequest,
    current_user: User = Depends(get_current_user)
):
    result = await recognize_google(req.points)
    return {
        "predictions": result.get("recognized", []),
        "top": result.get("recognized", [{}])[0] if result.get("recognized") else {}
    }
