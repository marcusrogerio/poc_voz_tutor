# models.py
from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
import uuid

from pgvector.sqlalchemy import Vector

from db import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True)  # google_id
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    current_lesson = Column(String, nullable=True)
    profile = Column(JSONB, nullable=False, server_default="{}")

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))  # para RAG no futuro
    created_at = Column(DateTime(timezone=True), server_default=func.now())
