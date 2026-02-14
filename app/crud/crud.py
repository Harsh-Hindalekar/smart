from sqlalchemy.orm import Session
from sqlalchemy import func
from passlib.context import CryptContext
from app.models.models import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -----------------------------
# User CRUD
# -----------------------------

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def _clean_email(email: str) -> str:
    return (email or "").strip().lower()

def _clean_username(username: str) -> str:
    return (username or "").strip()

def _clean_name(name: str) -> str:
    return (name or "").strip()

def create_user(db: Session, name: str, email: str, username: str, password: str) -> User:
    # Normalize inputs (validation is mostly handled in schemas, but keep safe here too)
    name = _clean_name(name)
    email = _clean_email(email)
    username = _clean_username(username)

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
    email = _clean_email(email)
    # case-insensitive compare
    return db.query(User).filter(func.lower(User.email) == email).first()

def get_user_by_username(db: Session, username: str) -> User:
    username = _clean_username(username)
    # case-insensitive compare to avoid "Harsh" vs "harsh"
    return db.query(User).filter(func.lower(User.username) == username.lower()).first()

def get_user_by_id(db: Session, user_id: str) -> User:
    return db.query(User).filter(User.id == user_id).first()
