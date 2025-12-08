from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.crud import crud
from app.database import get_db
from app.models.models import User
from app.auth.auth import get_current_user
from datetime import timedelta
from app.auth.auth import create_token
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.schemas import (UserCreate, UserLogin, UserResponse, PointsRequest)
from app.services.google_ai import perfect_drawing, recognize_google   # NEW

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
@router.post("/ai/perfect-drawing")
async def perfect_drawing_endpoint(
    payload: PointsRequest,
    smoothing_window: Optional[int] = Query(2, ge=0),
    simplify_eps: Optional[float] = Query(2.0, ge=0.0)
):
    """
    Accepts a PointsRequest (points: List[{x,y}]) and returns a perfected drawing:
    - smoothed_points
    - recognized_as
    - confidence
    """
    points = payload.points or []
    if not points or len(points) < 3:
        raise HTTPException(status_code=400, detail="Drawing too small. Draw more strokes.")

    try:
        result = await perfect_drawing(points, smoothing_window=smoothing_window, simplify_eps=simplify_eps)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/ai/recognize-drawing")
async def recognize_drawing_endpoint(payload: PointsRequest):
    """
    Returns raw recognition result from QuickDraw classify API.
    """
    points = payload.points or []
    if not points:
        raise HTTPException(status_code=400, detail="No drawing points provided")

    try:
        recognition = await recognize_google(points)
        return recognition
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI recognition error: {str(e)}")