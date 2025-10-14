from fastapi import APIRouter, Depends, Body, Request, Response, HTTPException, status
from app.model.dto import BodyResponse

prefix = "/v1/admin"
router = APIRouter()

user_router = APIRouter()
@user_router.post("/", response_model=BodyResponse)
def add_user(request: Request, body = Body(...)):
    return { "data": body, "db": request.app.database }

role_play_router = APIRouter()
@role_play_router.post("/", response_model=BodyResponse)
def add_role_play(request: Request, body = Body(...)):
    return { "data": body, "db": request.app.database }

router.include_router(user_router, prefix="/user", tags=["User Management"])
router.include_router(role_play_router, prefix="/role-play", tags=["Role Play Management"])

