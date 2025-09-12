from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.crud import crud
from app.database import get_db
from app.models.models import Content, User
from app.auth.auth import get_current_user
from datetime import timedelta
from app.auth.auth import create_token
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.schemas import (UserCreate, UserLogin,
                                UserResponse, ContentCreate,
                                ContentResponse)


ACCESS_TOKEN_EXPIRE_MINUTES = 1080 # its time of login token exipiration

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

# -----------------------------
# Create a new content post (protected route by user)
# -----------------------------

@router.post("/contents/", response_model=ContentResponse)
def create_content(
    content: ContentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_content = crud.create_content(
        db,
        title=content.title,
        description=content.description,
        user_id=current_user.id
    )
    return new_content

# -----------------------------
# Get content post by user itself (protected route by user)
# -----------------------------

@router.get("/contents/", response_model=List[ContentResponse])
def read_contents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contents = crud.get_contents(db, user_id=current_user.id)
    return contents

# -----------------------------
# Admin
# -----------------------------

# Get content post of specific user by user_id (protected route used by admin)
@router.get("/admin/users/{user_id}/contents/", response_model=List[ContentResponse])
def get_user_contents(user_id: str, db: Session = Depends(get_db)):
    return crud.get_contents_by_user(db, user_id)

# Get content post (protected route used by admin)
@router.get("/admin/contents/", response_model=List[ContentResponse])
def get_contents(db: Session = Depends(get_db)):
    return crud.get_all_contents(db)
