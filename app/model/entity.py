from datetime import datetime

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
import uuid
from app.model.type import UserProfile, RoleStudent, StudentLevel


class RolePlay(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    challenge: str
    xp: int = 0
    description: Optional[str] = None
    metadata: Optional[List[dict]] = None

class RoleLevel(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    step: int = 1
    min_xp: int
    max_xp: int
    play: List[RolePlay] = []

class Role(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    code: RoleStudent = RoleStudent.JR
    name: str = 'Junior'
    min_xp: int = 0
    max_xp: int = 0
    level: List[RoleLevel] = []

class UserRolePlay(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    role: RoleStudent = RoleStudent.JR
    level_step: int = 1
    xp: int = 0
    plays: Optional[List[RolePlay]] = None

class UserBase(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    username: str
    email: EmailStr = None
    password: str
    name: str = None
    profile: UserProfile = UserProfile.STUDENT
    document: Optional[str] = None
    level: Optional[StudentLevel] = None
    xp: Optional[int] = 0
    role_play: Optional[List[UserRolePlay]] = None
    token: Optional[str] = None
    created_at: Optional[datetime] = None