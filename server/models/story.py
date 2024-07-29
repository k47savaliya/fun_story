import uuid
from datetime import datetime
from sqlalchemy import Column, String, JSON, DateTime
from server.db.base_class import Base


class Story(Base):
    __tablename__ = "stories"
    
    id = Column(String(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    title = Column(String, index=True)
    contributions = Column(JSON)
    created_by = Column(String)
    story_image = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)