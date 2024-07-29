from sqlalchemy.ext.declarative import as_declarative


@as_declarative()
class Base:
    __name__: str
    __tablename__: str
       