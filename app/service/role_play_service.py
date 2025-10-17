from app.model.entity import UserBase
from app.util.role_play import role_enable, get_code_level
from pymongo.asynchronous.database import AsyncDatabase
from app.model.dto import UserDTO, UserCreateDTO, RoleDTO, PlayTaskDTO
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

    async def get_by_user(self, user: UserBase) -> list[RoleDTO] | None:
        user_code, user_level = get_code_level(user)
        enable_roles = role_enable(user)

        roles = await super().all()
        for role in roles:
            role["disabled"] = user_code not in enable_roles
            for role_level in role.level:
                role_level["disabled"] = user_level < role_level

    async def play_task(self, user: UserBase, play: PlayTaskDTO) -> RoleDTO:
        user_service = UserService(self.db)
        role = await self.get(play.role_id)
        if not role or role.disabled:
            raise Exception("Role not found or disabled")

        level = next((lvl for lvl in role.level if lvl.id == play.level_id and not lvl.disabled), None)
        if not level:
            raise Exception("Level not found or disabled")

        task = next((tsk for tsk in level.play if tsk.id == play.play_id and not tsk.disabled), None)
        if not task:
            raise Exception("Play task not found or disabled")

        # Here you would implement the logic to check the answer
        # For simplicity, let's assume any answer is correct
        user.xp += task.xp

        # Update user level based on new XP
        user_code, user_level = get_code_level(user)
        user.level = StudentLevel(user_level)

        await user_service.update(user.model_dump(by_alias=True))
        return role
