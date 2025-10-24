from copy import deepcopy
from datetime import datetime, UTC

from pymongo.asynchronous.database import AsyncDatabase
from app.model.dto import UserDTO, UserCreateDTO, UserQueryFilter
from app.model.type import UserProfile, StudentLevel
from app.service.service import Service, T
from database.collections import Table


class UserService(Service[UserDTO]):
    def __init__(self, db: AsyncDatabase):
        super().__init__(db.get_collection(Table.USER))

    async def get(self, query_params: UserQueryFilter) -> UserDTO | list[UserDTO] | None:
        params = query_params.model_dump(by_alias=True)
        if "id" in params and params["id"] is not None:
            return UserDTO(**await super().get(params["id"]))

        roles = await self.filtering(params)
        return [UserDTO(**role) for role in roles]

    async def add(self, data: UserCreateDTO) -> UserDTO:
        user = UserDTO(**data.model_dump(by_alias=True))
        if user.profile is UserProfile.STUDENT:
            user.level = data.level if "level" in data else StudentLevel.JR1
            user.xp = 0

        user.created_at = datetime.now(UTC)
        return await super().add(user)
