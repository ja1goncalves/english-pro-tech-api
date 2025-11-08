from fastapi import APIRouter, Request, HTTPException, status

from app.exception.exception import ConflictError
from app.model.dto import UserDTO, UserCreateDTO, UserUpdateDTO, UserQueryFilter
from app.model.type import UserProfile
from app.service.user_service import UserService

prefix = "/v1/user"
router = APIRouter()

@router.post("/register", response_model=UserDTO)
async def add_user(request: Request, user: UserCreateDTO):
    try:
        service = UserService(request.app.database)
        user.profile = UserProfile.STUDENT
        return await service.add(user)
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.__str__(),
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.put("/", response_model=None)
async def put_user(request: Request, body: UserUpdateDTO):
    service = UserService(request.app.database)
    return await service.user_update(body)

@router.get("/me", response_model=UserDTO)
async def get_user(request: Request):
    service = UserService(request.app.database)
    request.state.user = await service.get(UserQueryFilter(id=str(request.state.user.id), limit=1, offset=0))
    return request.state.user
