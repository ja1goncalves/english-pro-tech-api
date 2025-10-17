from typing import List
from fastapi import APIRouter, Request
from app.model.dto import RoleDTO, PlayTaskDTO
from app.service.role_play_service import RolePlayService

prefix = "/v1/role-play"
router = APIRouter()

@router.get("/", response_model=List[RoleDTO])
async def get_role_play(request: Request):
    service = RolePlayService(request.app.database)
    return await service.get_by_user(request.state.user)

@router.post("/", response_model=RoleDTO)
async def play_task(request: Request, play: PlayTaskDTO):
    service = RolePlayService(request.app.database)
    return await service.play_task(request.state.user, play)
