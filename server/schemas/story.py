from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class Contribution(BaseModel):
    user_id: str
    content: str

class StoryBase(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    contributions: List[Contribution] = []
    created_by: Optional[str] = None
    story_image: Optional[str] = None
    
    class Config:
        orm_mode = True

class StoryCreate(StoryBase):
    pass

class StoryUpdate(StoryBase):
    pass
