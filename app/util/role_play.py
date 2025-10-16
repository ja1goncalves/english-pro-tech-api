from app.model.dto import UserDTO
from app.model.entity import UserBase

ENABLE_CODES = {
    "JR": ["JR"],
    "PL": ["JR", "PL"],
    "SR": ["JR", "PL", "SR"],
    "TL": ["JR", "PL", "SR", "TL"]
}

def get_code_level(user: UserBase | UserDTO):
    return user.level.__str__().split("#")

def role_enable(user: UserBase | UserDTO):
    code, _ = get_code_level(user)
    return ENABLE_CODES[code] if code in ENABLE_CODES else ["JR"]