from typing import Annotated

from fastapi import APIRouter, Depends, Body, Request, Query
from app.model.dto import UserCreateDTO, UserDTO, UserUpdateDTO, RoleDTO, UserQueryFilter, RoleQueryFilter, \
    RoleCreateDTO, RoleUpdateDTO
from app.service.role_play_service import RolePlayService
from app.service.user_service import UserService

prefix = "/v1/admin"
router = APIRouter()

user_router = APIRouter()

@user_router.get("/", response_model=UserDTO | list[UserDTO])
async def get_user(request: Request, query_params: Annotated[UserQueryFilter, Query()]):
    service = UserService(request.app.database)
    return await service.get(query_params)

@user_router.post("/", response_model=UserDTO)
async def add_user(request: Request, body: UserCreateDTO):
    service = UserService(request.app.database)
    return await service.add(body)

@user_router.put("/", response_model=None)
async def put_user(request: Request, body: UserUpdateDTO):
    service = UserService(request.app.database)
    return await service.update(body)

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

@role_play_router.delete("/{key}", response_model=RoleDTO)
async def del_role_play(request: Request, key: str):
    service = RolePlayService(request.app.database)
    return await service.remove(key)

router.include_router(user_router, prefix="/user", tags=["User Management"])
router.include_router(role_play_router, prefix="/role-play", tags=["Role Play Management"])

