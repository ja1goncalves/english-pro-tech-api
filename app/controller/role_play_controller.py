from fastapi import APIRouter, Depends, Body, Request, Response, HTTPException, status
from app.model.dto import BodyResponse

prefix = "/v1/role-play"
router = APIRouter()

@router.post("/", response_model=BodyResponse)
def play(request: Request, body = Body(...)):
    return { "data": body, "db": request.app.database }
