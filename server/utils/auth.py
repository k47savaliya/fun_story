from datetime import datetime, timedelta
from typing import Optional


from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from server import crud, schemas
from server.api_v1.deps import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl="auth", tokenUrl="token")

SECRET_KEY = "09d25w7erf656f6yg45ctv4y4yc6vh2c4xdf635d3y33099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 20160


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# authenticate user by email and password
def authenticate_user(db, email: str, password: str):
    user = crud.user.get_by_email(db, email=email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# create access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1) # Token expiration time (adjust as needed)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# create refresh token
def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7) # Token expiration time (adjust as needed)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# create access token from refresh token
def create_access_token_from_refresh_token(refresh_token: str):
    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    access_token = create_access_token(data=payload)
    return access_token


def decode_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    return payload


# get current user from token
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> schemas.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("id")
        if id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # get user by ID
    user = crud.user.get_by_id(db, id=id)
    if user is None:
        raise credentials_exception
    return user
