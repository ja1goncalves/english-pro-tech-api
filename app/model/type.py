from enum import Enum

class UserProfile(Enum):
    ADMIN = 'admin'
    STUDENT = 'student'

class RoleStudent(Enum):
    JR = 'JR'
    PL = 'PL'
    SR = 'SR'
    TL = 'TL'