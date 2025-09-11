from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud import crud
from app.database import get_db

from app.schemas.schemas import(
    UserCreate, UserLogin, UserResponse
)

router = APIRouter()

# Register route
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email) or crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Email or username already exists")
    
    new_user = crud.create_user(db, user.name, user.email, user.username, user.password)
    return new_user

# Login route
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if not db_user or not crud.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    return {"message": f"Welcome {db_user.name}"}
