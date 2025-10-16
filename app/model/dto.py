from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime

from app.model.entity import UseRolePlay, RoleLevel
from app.model.type import UserProfile, RoleStudent


class Token(BaseModel):
    access_token: str
    token_type: str

class BodyResponse(BaseModel):
    pass

class RoleDTO(BaseModel):
    id: str
    code: RoleStudent
    name: str
    min_xp: int = 0
    max_xp: int = 0
    level: List[RoleLevel] = []

class UserDTO(BaseModel):
    id: str
    username: str
    email: EmailStr = None
    name: str = None
    profile: UserProfile
    document: Optional[str] = None
    level: Optional[str] = None
    xp: Optional[int] = 0
    role_play: Optional[List[UseRolePlay]] = None
    token: Optional[str] = None
    created_at: Optional[datetime] = None

class UserCreateDTO(BaseModel):
    username: str
    email: EmailStr = None
    password: str
    name: str = None
    profile: UserProfile = UserProfile.STUDENT
    document: Optional[str] = None