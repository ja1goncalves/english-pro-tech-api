from fastapi import APIRouter, Depends, Body, Request, Response, HTTPException, status
from app.model.dto import BodyResponse

prefix = "/v1/user"
router = APIRouter()

@router.post("/", response_model=BodyResponse)
def register(request: Request, body = Body(...)):
    return { "data": body, "db": request.app.database }
