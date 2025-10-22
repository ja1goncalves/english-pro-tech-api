from enum import Enum

class UserProfile(str, Enum):
    ADMIN = 'admin'
    STUDENT = 'student'

class RoleStudent(str, Enum):
    JR = 'JR'
    PL = 'PL'
    SR = 'SR'
    TL = 'TL'

class StudentLevel(str, Enum):
    JR1 = 'JR#1'
    JR2 = 'JR#2'
    JR3 = 'JR#3'
    PL1 = 'PL#1'
    PL2 = 'PL#2'
    PL3 = 'PL#3'
    SR1 = 'SR#1'
    SR2 = 'SR#2'
    SR3 = 'SR#3'
    TL1 = 'TL#1'
    TL2 = 'TL#2'
    TL3 = 'TL#3'