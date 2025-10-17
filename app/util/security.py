from datetime import datetime, timedelta, UTC
from typing import Optional
import jwt
from pymongo.asynchronous.database import AsyncDatabase

from app.exception.exception import ForbiddenError
from app.model.entity import UserBase
from app.util.config import settings
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def validate_token(db: AsyncDatabase, token: str) -> UserBase:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise ForbiddenError("Invalid token")

        user_collection = db.get_collection("user")
    except jwt.PyJWTError:
        raise ForbiddenError()
    user = user_collection.find({"username": username}).limit(1)[0]
    if user is None:
        raise ForbiddenError("Invalid token or user does not exist")
    return user

def test_password_hashing():
    plain_password = "superduper"
    hashed_password = get_password_hash(plain_password)
    assert verify_password(plain_password, hashed_password) == True
    assert verify_password("wrongpassword", hashed_password) == False

test_password_hashing()