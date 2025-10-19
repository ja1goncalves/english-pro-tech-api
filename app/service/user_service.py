from copy import deepcopy
from datetime import datetime, UTC

from pymongo.asynchronous.database import AsyncDatabase
from app.model.dto import UserDTO, UserCreateDTO
from app.model.type import UserProfile, StudentLevel
from app.service.service import Service, T


class UserService(Service[UserDTO]):
    def __init__(self, db: AsyncDatabase):
        super().__init__(db.get_collection("user"))

    async def get(self, key: str | None, params: dict = {}) -> UserDTO | list[UserDTO] | None:
        if key:
            return await super().get(key)
        return await super().all(
            params,
            params["limit"] if "limit" in params else 100,
            params["offset"] if "offset" in params else 0
        )

    async def add(self, data: UserCreateDTO) -> T:
        user = deepcopy(data)
        if user.profile is UserProfile.STUDENT:
            data["level"] = data["level"] if "level" in data else StudentLevel.JR1
            data["xp"] = 0
            data["role_play"] = []

        user["created_at"] = datetime.now(UTC).isoformat()
        return super().add(user)
