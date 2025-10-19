import re
from typing import Tuple

from app.model.entity import UserBase, Role, RoleLevel, RolePlay, UserPlayStory
from app.util.role_play import story_play_str
from app.model.dto import RoleDTO, RoleLevelDTO, RolePlayDTO
from resource.gen_ai_api import GenAIAPI


class GenIAService:

    def __init__(self, user: UserBase):
        self.system_message = f"""Você é um assistente de IA especializado em criar desafios práticos para ajudar
        usuários a melhorar suas habilidades em inglês técnico. Meu nome é {user.name}
        e estou no nível {user.level} de desenvolvimento em tecnologia. Considere meu nível de desenvolvimento e
        o desafio proposto para elaborar um desafio adequado ou continuar um desafio existente."""
        self.gen_ia = GenAIAPI(self.system_message)

    async def init_play(self, role: RoleDTO | Role, level: RoleLevelDTO | RoleLevel,
                        task: RolePlayDTO | RolePlay) -> Tuple[str, str]:
        role_name = role.name
        level = level.step
        challenge = task.challenge
        description = task.description or "Explore pontos técnicos relevantes"
        metadata = task.metadata

        question = f"""Por favor, elabore um desafio prático personalizado, para o nível de desenvolvimento {role_name}
        de nível técnico {level}, em que {challenge} onde {description} para que eu possa melhorar minhas habilidades
        em inglês técnico. Use as seguintes informações adicionais para tornar o desafio mais relevante: {metadata}"""

        return question, self.gen_ia.send_prompt(question)

    async def answer_play(self, answer: str, story: list[UserPlayStory],
                          role: RoleDTO | Role, level: RoleLevelDTO | RoleLevel,
                          task: RolePlayDTO | RolePlay) -> Tuple[int, str, str]:
        role_name = role.name
        level = level.step
        challenge = task.challenge
        description = task.description or "Explore pontos técnicos relevantes"
        metadata = task.metadata

        self.system_message += f"""Para isso, leve em consideração que estou no nível de desenvolvimento {role_name}
        de nível técnico {level}, no desafio '{challenge}' onde {description} para que eu possa melhorar minhas habilidades
        em inglês técnico e que já tive o seguinte histórico de progresso em outros desafios: {story_play_str(story)}.
        Use as seguintes informações adicionais para tornar o desafio mais relevante: {metadata}"""

        question = f"""O usuário respondeu ao desafio prático com a seguinte resposta: {answer}.
        Por favor, forneça feedback detalhado sobre a resposta do usuário, destacando pontos fortes e áreas de melhoria,
        e sugira maneiras de aprimorar suas habilidades em inglês técnico com base na resposta fornecida.
        De acordo com a responta, avalie e atribua uma pontuação de XP apropriada entre 0 a {task.xp} no formato 'Pontos=20xp' no inicio do feedback."""

        regex_xp = r'Pontos=(\d+)xp'

        res = self.gen_ia.send_prompt(question)
        xp = re.search(regex_xp, res).group(1)

        res = re.sub(regex_xp, "", res)

        return int(xp), question, res


