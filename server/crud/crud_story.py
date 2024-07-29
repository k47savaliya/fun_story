from typing import List, Optional

from sqlalchemy.orm import Session

from server.crud.base import CRUDBase
from server.models.story import Story
from server.schemas.story import StoryUpdate, StoryCreate


class CRUDSTORY(CRUDBase[Story, StoryCreate, StoryUpdate]):
    """
    CRUD for Story
    """
    
    def get_all(self, db: Session, limit: int, offset: int) -> List[Story]:
        return db.query(Story).offset(offset).limit(limit).all()

    def get_by_id(self, db: Session, *, id: str) -> Story:
        return db.query(Story).filter(Story.id == id).first()

    def create(self, db: Session, *, obj_in: StoryCreate) -> Story:
        return super().create(db, obj_in=obj_in)

    def update(self, db: Session, *, db_obj: Story, obj_in: StoryUpdate) -> Story:
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def remove(self, db: Session, *, id: str) -> Optional[Story]:
        return super().remove(db, id=id)


story = CRUDSTORY(Story)
