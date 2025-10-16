from pydantic import BaseModel
from pymongo.asynchronous.database import AsyncDatabase
from app.model.dto import UserDTO
from app.service.service import Service


class UserService(Service[UserDTO]):
    def __init__(self, db: AsyncDatabase):
        super().__init__(db.collection("user"))