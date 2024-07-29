from typing import Generator
from fastapi.security import HTTPBasic
from server.db.session import SessionLocal

security = HTTPBasic()


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


