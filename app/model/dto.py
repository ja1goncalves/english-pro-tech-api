from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime

from app.model.entity import UserRolePlay
from app.model.type import UserProfile, RoleStudent, StudentLevel

class LoginDTO(BaseModel):
    username: str
    password: str

class TokenDTO(BaseModel):
    access_token: str
    token_type: str

class AskResetPasswordDTO(BaseModel):
    username: str
    email: EmailStr

class ResetPasswordDTO(BaseModel):
    password: str
    confirm_password: str

class BodyResponse(BaseModel):
    pass

class RolePlayDTO(BaseModel):
    id: Optional[str]
    challenge: str
    xp: int = 0
    description: Optional[str] = None
    metadata: Optional[List[dict]] = None
    disabled: bool = True

class RoleLevelDTO(BaseModel):
    id: Optional[str]
    step: int = 1
    min_xp: int
    max_xp: int
    play: Optional[List[RolePlayDTO]] = []
    disabled: bool = False

class RoleDTO(BaseModel):
    id: Optional[str]
    code: RoleStudent
    name: str
    min_xp: int = 0
    max_xp: int = 0
    level: Optional[List[RoleLevelDTO]] = []
    disabled: bool = True

class UserDTO(BaseModel):
    id: str
    username: str
    email: EmailStr = None
    name: str = None
    profile: UserProfile
    document: Optional[str] = None
    level: Optional[StudentLevel] = None
    xp: Optional[int] = 0
    role_play: Optional[List[UserRolePlay]] = None
    token: Optional[str] = None
    created_at: Optional[datetime] = None

class UserCreateDTO(BaseModel):
    username: str
    email: EmailStr = None
    password: str
    name: str = None
    profile: UserProfile = UserProfile.STUDENT
    document: Optional[str] = None
    level: Optional[StudentLevel]

class UserUpdateDTO(UserCreateDTO):
    _id: str
    xp: Optional[int]