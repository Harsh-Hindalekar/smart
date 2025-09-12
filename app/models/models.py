from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"   
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Content(Base):
    __tablename__ = "contents" 
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000))
    type = Column(String(50))  # Blog, Article, Motivational Post


class EmergencyContact(Base):
    __tablename__ = "emergency_contacts" 
    id = Column(Integer, primary_key=True, autoincrement=True)
    helpline_name = Column(String(255))
    helpline_number = Column(String(50))
