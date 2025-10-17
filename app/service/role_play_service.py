from app.util.role_play import role_enable, get_code_level
from pymongo.asynchronous.database import AsyncDatabase
from app.model.dto import UserDTO, UserCreateDTO, RoleDTO
from app.model.type import UserProfile, StudentLevel
from app.service.service import Service, T
from app.service.user_service import UserService


class RolePlayService(Service[RoleDTO]):
    def __init__(self, db: AsyncDatabase):
        self.db = db
        super().__init__(self.db.get_collection("role_play"))

    async def get(self, key: str | None, params: dict = {}) -> RoleDTO | list[RoleDTO] | None:
        if key:
            return await super().get(key)
        return await super().all(
            params,
            params["limit"] if "limit" in params else 100,
            params["offset"] if "offset" in params else 0
        )

    async def get_by_user(self, user_id: str) -> list[RoleDTO] | None:
        user_service = UserService(self.db)
        user = await user_service.get(user_id)
        user_code, user_level = get_code_level(user)
        enable_roles = role_enable(user)

        roles = await super().all()
        for role in roles:
            role["disabled"] = user_code not in enable_roles
            for role_level in role.level:
                role_level["disabled"] = user_level < role_level
