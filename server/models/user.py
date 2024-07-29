import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String

from server.db.base_class import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    name = Column(String)
    email = Column(String, unique=True, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
