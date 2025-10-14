from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str

class BodyResponse(BaseModel):
    pass