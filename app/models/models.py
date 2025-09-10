from sqlalchemy import (
    Column, String, Float, Text, Enum, Boolean, ForeignKey,
    Integer, DateTime, CHAR, Table, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)