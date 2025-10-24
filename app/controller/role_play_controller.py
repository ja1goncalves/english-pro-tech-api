import json
from typing import List
from fastapi import APIRouter, Request, HTTPException, status

from app.exception.exception import RoleLevelError
from app.model.dto import RoleDTO, PlayTaskDTO, ChallengeDTO
from app.service.role_play_service import RolePlayService

prefix = "/v1/role-play"
router = APIRouter()

@router.get("/", response_model=List[RoleDTO])
async def get_role_play(request: Request):
    service = RolePlayService(request.app.database)
    return await service.get_by_user(request.state.user)

@router.post("/", response_model=ChallengeDTO)
async def play_task(request: Request, play: PlayTaskDTO):
    try:
        service = RolePlayService(request.app.database)
        return await service.play_task(request.state.user, play)
    except RoleLevelError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"}
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Decoding GEnAI response error",
            headers={"WWW-Authenticate": "Bearer"}
        )
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail="Some internal error occurred",
    #         headers={"WWW-Authenticate": "Bearer"}
    #     )
