from app.exception.exception import RoleLevelError
from app.model.entity import UserBase
from app.service.gen_ia_service import GenIAService
from app.util.role_play import role_enable, get_code_level, get_story_play, is_story_play, new_story_play
from pymongo.asynchronous.database import AsyncDatabase
from app.model.dto import RoleDTO, PlayTaskDTO, RoleLevelDTO, RolePlayDTO, ChallengeDTO
from app.model.type import StudentLevel, RoleStudent
from app.service.service import Service
from app.service.user_service import UserService
from database.collections import Table


class RolePlayService(Service[RoleDTO]):
    def __init__(self, db: AsyncDatabase):
        self.db = db
        super().__init__(self.db.get_collection(Table.ROLE_PLAY))

    async def get(self, key: str | None, params: dict = {}) -> RoleDTO | list[RoleDTO] | None:
        if key:
            return await super().get(key)
        return await super().all(
            params,
            params["limit"] if "limit" in params else 1000,
            params["offset"] if "offset" in params else 0
        )

    async def get_by_user(self, user: UserBase) -> list[RoleDTO] | None:
        user_service = UserService(self.db)
        user_db = await user_service.get(user.id)
        user_code, user_level = get_code_level(user_db)
        enable_roles = role_enable(user_db)

        roles = await super().all()
        for role in roles:
            role["disabled"] = user_code not in enable_roles
            for role_level in role.level:
                role_level["disabled"] = user_level < role_level

    async def play_task(self, user: UserBase, data: PlayTaskDTO) -> ChallengeDTO:
        role: RoleDTO = await self.get(data.role_id)
        level: RoleLevelDTO = next(lvl for lvl in role.level if lvl.id == data.level_id)
        play: RolePlayDTO = next(pl for pl in level.plays if pl.id == data.play_id)

        user_role_code, user_role_level = get_code_level(user)

        if role.code == user_role_code and level.step == user_role_level:
            user_play_history = user.play_story or []
            user_role_play = get_story_play(role.code, level.step, data.play_id, user_play_history)
            gen_ia_service = GenIAService(user)

            if not user_role_play:
                question, response = await gen_ia_service.init_play(role, level, play)
                res = ChallengeDTO(question=question, response=response, xp=0)
                finished = await self.update_user_role_play(user, role.code, level.step, data.play_id, res)
                res.update_level = finished
                return res
            else:
                xp, question, response = await gen_ia_service.answer_play(data.answer, user_role_play, role, level, play)
                res = ChallengeDTO(question=question, response=response, xp=xp)
                finished = await self.update_user_role_play(user, role.code, level.step, data.play_id, res)
                res.update_level = finished
                return res
        else:
            raise RoleLevelError("User role does not match the requested role play")

    async def update_user_role_play(self, user: UserBase, role_code: RoleStudent, role_level: int, play_id: str,
                                    play: ChallengeDTO) -> bool:
        if not user.play_story:
            user.play_story = []
            user = new_story_play(user, role_code, role_level, play_id, play)
        else:
            for story in user.play_story:
                if is_story_play(story, role_code, role_level, play_id):
                    story.xp = (story.xp or 0) + play.xp
                    if story.metadata:
                        story.metadata.append(play.model_dump(by_alias=True))
                    else:
                        story.metadata = [play.model_dump(by_alias=True)]
                    break
                else:
                    user = new_story_play(user, role_code, role_level, play_id, play)

        user.xp = (user.xp or 0) + play.xp
        old_user_level = user.level
        user.level = await self.classifier_user(user)

        user_service = UserService(self.db)
        await user_service.update(user)

        return old_user_level != user.level

    async def classifier_user(self, user: UserBase) -> StudentLevel:
        roles = await self.get(None)
        new_role = None
        new_level = None

        for role in roles:
            if role.min_xp <= user.xp <= role.max_xp:
                new_role = role.code
                for level in role.level:
                    if level.min_xp <= user.xp <= level.max_xp:
                        new_level = level.step
                        break
                break

        return f"{new_role}#{new_level}" if new_role and new_level else user.level
