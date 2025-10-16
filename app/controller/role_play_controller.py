from fastapi import APIRouter, Depends, Body, Request, Response, HTTPException, status
from app.model.dto import BodyResponse, RoleDTO
from app.service.role_play_service import RolePlayService

prefix = "/v1/role-play"
router = APIRouter()

@router.get("/{key}", response_model=RoleDTO)
async def get_role_play(request: Request, key: str, query_params: dict = Depends()):
    service = RolePlayService(request.app.database)
    return await service.get(key, query_params)
