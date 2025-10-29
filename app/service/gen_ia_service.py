import re
from typing import Tuple

from app.model.entity import UserBase, Role, RoleLevel, RolePlay, UserPlayStory
from app.util.role_play import story_play_str
from app.model.dto import RoleDTO, RoleLevelDTO, RolePlayDTO
from resource.gen_ai_api import GenAIAPI


class GenIAService:

    def __init__(self, user: UserBase):
        self.system_message = f"""You are an AI assistant specializing in creating practical challenges to help users
        improve their technical English skills. My name is {user.name} and I am at the {user.level} level of development
        in technology. Consider my development level and the proposed challenge to create a suitable challenge or
        continue an existing one."""
        self.gen_ia = GenAIAPI(self.system_message)

    async def init_play(self, role: RoleDTO | Role, level: RoleLevelDTO | RoleLevel,
                        task: RolePlayDTO | RolePlay) -> Tuple[int, str, str]:
        role_name = role.name
        step = level.step
        challenge = task.challenge
        description = task.description or "Explore relevant technical points."
        metadata = task.metadata

        question = f"""Please create a custom practical challenge for the {role_name} development role from the
        technical level {step}, where {challenge} is {description} so that I can improve my skills in technical English.
        Use the following additional information to make the challenge more relevant: {metadata}"""

        return 0, question, self.gen_ia.send_prompt(question)

    async def answer_play(self, answer: str, story: list[UserPlayStory],
                          role: RoleDTO | Role, level: RoleLevelDTO | RoleLevel,
                          task: RolePlayDTO | RolePlay) -> Tuple[int, str, str]:
        role_name = role.name
        step = level.step
        challenge = task.challenge
        description = task.description or "Explore relevant technical points."
        metadata = task.metadata

        self.system_message += f"""For this, please consider that I am at the {role_name} development role from
        technical level {step} in the '{challenge}' challenge where {description} so that I can improve my skills
        in technical English and that I have already had the following progress history in other challenges: {story_play_str(story)}.
        Use the following additional information to make the challenge more relevant: {metadata}."""

        question = f"""The user replied to the practice challenge with the following answer: {answer}.
        Please provide detailed feedback on the user's answer, highlighting strengths and areas for improvement,
        and suggest ways to improve their technical English skills based on the answer provided.
        Based on the answer, evaluate and assign an appropriate XP score between 0 and {task.xp} in the format
        'Points=20xp' at the beginning of the feedback. Like this example: 'Points=15xp. Your answer demonstrates...'."""

        res = self.gen_ia.send_prompt(question)

        regex_xp = r'Points=(\d+)xp'
        get_points = re.search(regex_xp, res)
        xp = int(get_points.group(1)) if get_points else task.xp / 4

        res = re.sub(regex_xp, "", res)

        return xp, question, res


