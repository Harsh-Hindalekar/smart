from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime
from app.models.models import User, Content

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -----------------------------
# User CRUD
# -----------------------------

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_user(db: Session, name: str, email: str, username: str, password: str) -> User:
    hashed_password = hash_password(password)
    db_user = User(
        name=name,
        email=email,
        username=username,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str) -> User:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: str) -> User:
    return db.query(User).filter(User.id == user_id).first()


# -----------------------------
# Content CRUD
# -----------------------------

def create_content(db: Session, title: str, description: str, user_id: str) -> Content:
    new_content = Content(
        title=title,
        description=description,
        user_id=user_id,
    )
    db.add(new_content)
    db.commit()
    db.refresh(new_content)
    return new_content

def get_contents(db: Session, user_id: int):
    return db.query(Content).filter(
        Content.user_id == user_id
    ).all()

def get_all_contents(db: Session):
    return db.query(Content).all()

def get_content_by_id(db: Session, content_id: str):
    return db.query(Content).filter(Content.id == content_id).first()

def get_contents_by_user(db: Session, user_id: str):
    return db.query(Content).filter(Content.user_id == user_id).all()
