import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

# configuration settings
class Settings(BaseSettings):
    debug: bool = bool(os.environ.get("DEBUG"))
    SQLALCHEMY_DATABASE_URI: str = os.environ.get("SQLALCHEMY_DATABASE_URI")

    IMAGEKIT_PUBLIC_KEY: str = os.environ.get("IMAGEKIT_PUBLIC_KEY")
    IMAGEKIT_PRIVATE_KEY: str = os.environ.get("IMAGEKIT_PRIVATE_KEY")
    IMAGEKIT_UPLOAD_URL: str = os.environ.get("IMAGEKIT_UPLOAD_URL")
    
    STATIC_FILE: str = "static"

settings = Settings()
