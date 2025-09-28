from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    drawings = relationship("Drawing", back_populates="user", cascade="all, delete-orphan")
    ai_results = relationship("AIResult", back_populates="user", cascade="all, delete-orphan")
    flipbooks = relationship("Flipbook", back_populates="user", cascade="all, delete-orphan")

class Drawing(Base):
    __tablename__ = "drawings"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="drawings")

class AIResult(Base):
    __tablename__ = "ai_results"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    input_data = Column(String(5000), nullable=False)  # or whatever max length you expect
    output_filename = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="ai_results")

class Flipbook(Base):
    __tablename__ = "flipbooks"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="flipbooks")
    frames = relationship("FlipbookFrame", back_populates="flipbook", cascade="all, delete-orphan")

class FlipbookFrame(Base):
    __tablename__ = "flipbook_frames"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    flipbook_id = Column(String(36), ForeignKey("flipbooks.id"), nullable=False)
    frame_number = Column(Integer, nullable=False)
    filename = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    flipbook = relationship("Flipbook", back_populates="frames")
