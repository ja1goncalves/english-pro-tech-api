import uuid
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, UTC
from app.model.entity import UserPlayStory
from app.model.pydantic_object_id import PydanticObjectId
from app.model.type import UserProfile, RoleStudent, StudentLevel

class ChallengeDTO(BaseModel):
    question: str
    response: str
    xp: int
    update_level: Optional[bool] = False
    created_at: datetime = datetime.now(UTC)

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

class ChangePasswordDTO(ResetPasswordDTO):
    user_id: str

class RolePlayCreateDTO(BaseModel):
    code: Optional[str] = None
    challenge: str
    xp: int = 0
    description: Optional[str] = None
    metadata: Optional[List[dict]] = None

class RoleLevelCreateDTO(BaseModel):
    step: int = 1
    min_xp: int
    max_xp: int
    plays: Optional[List[RolePlayCreateDTO]] = []

class RoleCreateDTO(BaseModel):
    code: RoleStudent
    name: str
    min_xp: int = 0
    max_xp: int = 0
    level: Optional[List[RoleLevelCreateDTO]] = []

class RoleUpdateDTO(RoleCreateDTO):
    id: str

class RolePlayDTO(BaseModel):
    code: str
    challenge: str
    xp: int = 0
    description: Optional[str] = None
    metadata: Optional[List[dict]] = None
    disabled: Optional[bool] = True

class RoleLevelDTO(BaseModel):
    step: int = 1
    min_xp: int
    max_xp: int
    plays: Optional[List[RolePlayDTO]] = []
    disabled: Optional[bool] = False

class RoleDTO(BaseModel):
    id: PydanticObjectId = Field(default_factory=uuid.uuid4, alias="_id")
    code: RoleStudent
    name: str
    min_xp: int = 0
    max_xp: int = 0
    level: Optional[List[RoleLevelDTO]] = []
    disabled: Optional[bool] = True

class RoleQueryFilter(BaseModel):
    id: Optional[str] = None
    code: Optional[RoleStudent] = None
    name: Optional[str] = Field(default_factory=str)

class PlayTaskDTO(BaseModel):
    role_id: str
    level_num: int
    play_code: str
    answer: Optional[str] = None

class UserDTO(BaseModel):
    id: PydanticObjectId = Field(default_factory=uuid.uuid4, alias="_id")
    username: str
    email: EmailStr = None
    name: str = None
    profile: UserProfile
    document: Optional[str] = None
    level: Optional[StudentLevel] = None
    xp: Optional[int] = 0
    play_story: Optional[List[UserPlayStory]] = []
    created_at: datetime = datetime.now(UTC)

class UserQueryFilter(BaseModel):
    id: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(default_factory=str)
    profile: Optional[UserProfile] = None
    document: Optional[str] = None
    level: Optional[StudentLevel] = None
    limit: Optional[int] = Field(100, gt=0, le=100)
    offset: Optional[int] = Field(0, ge=0)

class UserCreateDTO(BaseModel):
    username: str
    email: EmailStr = None
    password: str
    name: str = None
    profile: UserProfile = UserProfile.STUDENT
    document: Optional[str] = None
    level: Optional[StudentLevel]

class UserUpdateDTO(BaseModel):
    id: str
    email: EmailStr | None = None
    name: str | None = None
    xp: int | None = None
    profile: UserProfile | None = None
    level: StudentLevel | None = None