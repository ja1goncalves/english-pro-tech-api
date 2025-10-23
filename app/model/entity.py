from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
import uuid

from app.model.type import UserProfile, RoleStudent, StudentLevel

class Challenge(BaseModel):
    question: str
    response: str
    xp: int
    update_level: Optional[bool] = False

class RolePlay(BaseModel):
    id: ObjectId = Field(default_factory=uuid.uuid4, alias="_id")
    challenge: str
    xp: int = 0
    description: Optional[str] = None
    metadata: Optional[List[dict]] = None
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class RoleLevel(BaseModel):
    id: ObjectId = Field(default_factory=uuid.uuid4, alias="_id")
    step: int = 1
    min_xp: int
    max_xp: int
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class Role(BaseModel):
    id: ObjectId = Field(default_factory=uuid.uuid4, alias="_id")
    code: RoleStudent = RoleStudent.JR
    name: str = 'Junior'
    min_xp: int = 0
    max_xp: int = 0
    level: List[RoleLevel] = []
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class UserPlayStory(BaseModel):
    id: ObjectId = Field(default_factory=uuid.uuid4, alias="_id")
    role: RoleStudent = RoleStudent.JR
    level_step: int = 1
    play_id: str
    xp: int = 0
    metadata: Optional[List[Challenge]] = []
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class UserBase(BaseModel):
    id: ObjectId = Field(default_factory=uuid.uuid4, alias="_id")
    username: str
    email: EmailStr = None
    password: str
    name: str = None
    profile: UserProfile = UserProfile.STUDENT
    document: Optional[str] = None
    level: Optional[StudentLevel] = None
    xp: Optional[int] = 0
    play_story: Optional[List[UserPlayStory]] = None
    token: Optional[str] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )