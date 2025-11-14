from copy import deepcopy
from datetime import datetime, UTC

from pymongo.asynchronous.database import AsyncDatabase

from app.exception.exception import ConflictError
from app.model.dto import UserDTO, UserCreateDTO, UserQueryFilter, UserUpdateDTO, ChangePasswordDTO
from app.model.entity import UserBase, ProcessedChunk
from app.model.type import UserProfile, StudentLevel
from app.service.service import Service, T
from app.util.security import get_password_hash
from database.collections import Table


class RagDocService(Service[ProcessedChunk]):
    def __init__(self, db: AsyncDatabase):
        super().__init__(db.get_collection(Table.RAG_DOC))
