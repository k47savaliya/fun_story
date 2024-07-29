from typing import List, Optional

from sqlalchemy.orm import Session

from server.crud.base import CRUDBase
from server.models.user import User
from server.schemas.user import UserCreate, UserUpdate


class CRUDUSER(CRUDBase[User, UserCreate, UserUpdate]):
    """
    CRUD for User
    """


    def get_all(self, db: Session, limit: int, offset: int) -> List[User]:
        return db.query(User).offset(offset).limit(limit).all()
    
    def get_total_users_count(self, db: Session) -> User:
        return db.query(User).count()

    def get_by_id(self, db: Session, *, id: str) -> User:
        return db.query(User).filter(User.id == id).first()

    def get_by_email(self, db: Session, *, email: str) -> User:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        return super().create(db, obj_in=obj_in)

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        return super().update(db, db_obj=db_obj, obj_in=obj_in)

    def remove(self, db: Session, *, id: str) -> Optional[User]:
        return super().remove(db, id=id)


user = CRUDUSER(User)
