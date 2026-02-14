from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from app.crud import crud
from app.database import get_db
from app.models.models import User
from app.auth.auth import get_current_user, create_token
from app.schemas.schemas import UserCreate, UserResponse
from app.routes.ai_drawing import router as ai_router

ACCESS_TOKEN_EXPIRE_MINUTES = 1080

router = APIRouter()

# Keep as you have (just note: this makes endpoints /ai/ai/perfect-drawing if your ai_router already has /ai prefix)
router.include_router(ai_router, prefix="/ai", tags=["AI Drawing"])


# -----------------------------
# Register route
# -----------------------------
from sqlalchemy.exc import IntegrityError

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    email = (user.email or "").strip().lower()
    username = (user.username or "").strip()

    if crud.get_user_by_email(db, email):
        raise HTTPException(status_code=409, detail="Email already exists")

    if crud.get_user_by_username(db, username):
        raise HTTPException(status_code=409, detail="Username already exists")

    try:
        new_user = crud.create_user(db, user.name, email, username, user.password)
        return new_user
    except IntegrityError:
        db.rollback()
        # if DB unique constraint triggers anyway
        raise HTTPException(status_code=409, detail="Email or username already exists")


# -----------------------------
# Login route
# -----------------------------
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    username = (form_data.username or "").strip()
    password = form_data.password or ""

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    db_user = crud.get_user_by_username(db, username)
    if not db_user or not crud.verify_password(password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": db_user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

