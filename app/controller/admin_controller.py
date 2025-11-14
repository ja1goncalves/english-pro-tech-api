from typing import Annotated

from fastapi import APIRouter, Depends, Request, Query, HTTPException, status

from app.exception.exception import ConflictError
from app.model.dto import UserCreateDTO, UserDTO, UserUpdateDTO, RoleDTO, UserQueryFilter, RoleQueryFilter, \
    RoleCreateDTO, RoleUpdateDTO, ChangePasswordDTO
from app.service.rag_doc_service import RagDocService
from app.service.role_play_service import RolePlayService
from app.service.user_service import UserService
from app.util.security import is_admin

prefix = "/v1/admin"
router = APIRouter(dependencies=[Depends(is_admin)])

user_router = APIRouter()

@user_router.get("/", response_model=UserDTO | list[UserDTO])
async def get_user(request: Request, query_params: Annotated[UserQueryFilter, Query()]):
    service = UserService(request.app.database)
    return await service.get(query_params)

@user_router.post("/", response_model=UserDTO)
async def add_user(request: Request, body: UserCreateDTO):
    try:
        service = UserService(request.app.database)
        return await service.add(body)
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

@user_router.put("/", response_model=None)
async def put_user(request: Request, body: UserUpdateDTO):
    service = UserService(request.app.database)
    return await service.user_update(body)

@user_router.put("/change-password", response_model=None)
async def edit_password_user(request: Request, body: ChangePasswordDTO):
    if body.password != body.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password and confirm password do not match",
            headers={"WWW-Authenticate": "Bearer"}
        )
    service = UserService(request.app.database)
    return await service.change_password(body.user_id, body.password)

@user_router.delete("/{key}", response_model=None)
async def del_user(request: Request, key: str):
    service = UserService(request.app.database)
    return await service.remove(key)

role_play_router = APIRouter()

@role_play_router.get("/", response_model=RoleDTO | list[RoleDTO])
async def get_role_play(request: Request, query_params: Annotated[RoleQueryFilter, Query()]):
    service = RolePlayService(request.app.database)
    return await service.get(query_params)

@role_play_router.post("/", response_model=RoleDTO)
async def add_role_play(request: Request, body: RoleCreateDTO):
    service = RolePlayService(request.app.database)
    return await service.add(body)

@role_play_router.put("/", response_model=None)
async def put_role_play(request: Request, body: RoleUpdateDTO):
    service = RolePlayService(request.app.database)
    return await service.update(body)

@role_play_router.delete("/{key}", response_model=None)
async def del_role_play(request: Request, key: str):
    service = RolePlayService(request.app.database)
    return await service.remove(key)

rag_router = APIRouter()

@rag_router.put("/refresh", response_model=None)
async def refresh_rag(request: Request):
    service = RagDocService(request.app.database)
    return await service.refresh_rag()

router.include_router(user_router, prefix="/user", tags=["User Management"])
router.include_router(rag_router, prefix="/rag", tags=["RAG Management"])
router.include_router(role_play_router, prefix="/role-play", tags=["Role Play Management"])

