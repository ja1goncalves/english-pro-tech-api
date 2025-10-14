from fastapi import APIRouter, Depends, Body, Request, Response, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.model.dto import Token

prefix = "/v1/auth"
router = APIRouter()

@router.post("/", response_model=Token)
def login(request: Request, body: OAuth2PasswordRequestForm = Depends()):
    return { "data": body, "db": request.app.database }
