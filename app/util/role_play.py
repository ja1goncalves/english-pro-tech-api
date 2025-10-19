from app.model.dto import UserDTO, ChallengeDTO
from app.model.entity import UserBase, UserPlayStory
from app.model.type import RoleStudent

ENABLE_CODES = {
    "JR": ["JR"],
    "PL": ["JR", "PL"],
    "SR": ["JR", "PL", "SR"],
    "TL": ["JR", "PL", "SR", "TL"]
}

def get_code_level(user: UserBase | UserDTO):
    role, level = user.level.__str__().split("#")
    return role, int(level)

def role_enable(user: UserBase | UserDTO):
    code, _ = get_code_level(user)
    return ENABLE_CODES[code] if code in ENABLE_CODES else ["JR"]

def is_story_play(p: UserPlayStory, role_code: RoleStudent, role_level: int, level_play: str) -> bool:
    return p.role == role_code and p.level_step == role_level and p.id == level_play

def get_story_play(role_code: RoleStudent, role_level: int, level_play: str,
                   user_role_play: list[UserPlayStory] = []) -> list[UserPlayStory]:
    return [p for p in user_role_play if is_story_play(p, role_code, role_level, level_play)]

def new_story_play(user: UserBase, role_code: RoleStudent, role_level: int, play_id: str,
                   play: ChallengeDTO) -> UserBase:
    user.role_play.append(UserPlayStory(
        role=role_code,
        level_step=role_level,
        xp=play.xp,
        play_id=play_id,
        metadata=[play.model_dump(by_alias=True)]
    ))

    return user

def story_play_str(story: list[UserPlayStory]) -> str:
    story_str = ""
    for s in story:
        metadata_str = "; ".join([f"Usuário: '{m.question}' e Feedback: '{m.response}' com {m.xp} de XP. " for m in s.metadata]) if s.metadata else ""
        story_str += f"Role: {s.role}, Level: {s.level_step}, Play ID: {s.play_id}, XP: {s.xp}.\nHistórico de conversa: {metadata_str}."

    return story_str