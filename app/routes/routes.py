from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.crud import crud
from app.database import get_db
from app.models.models import Content, User
from app.auth.auth import get_current_user
from app.schemas.schemas import UserCreate, UserLogin, UserResponse, ContentCreate, ContentResponse
from datetime import timedelta
from app.auth.auth import create_token

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
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if not db_user or not crud.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": db_user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}



# -----------------------------
# Create a new content post (protected route)
# -----------------------------
@router.post("/contents/", response_model=ContentResponse)
def create_content(content: ContentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_content = Content(
        title=content.title,
        description=content.description,
        type=content.type,
        user_id=current_user.id
    )

    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    return new_content


# -----------------------------
# Get all content posts
# -----------------------------
@router.get("/contents/", response_model=List[ContentResponse])
def get_contents(db: Session = Depends(get_db)):
    contents = db.query(Content).all()
    return contents


# -----------------------------
# Get content posts by user
# -----------------------------
@router.get("/users/{user_id}/contents/", response_model=List[ContentResponse])
def get_user_contents(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.contents
