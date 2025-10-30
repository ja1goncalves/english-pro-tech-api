from fastapi import APIRouter, Depends, Body, Request, Response, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.exception.exception import CredentialsError, UpdateError, ForbiddenError
from app.model.dto import TokenDTO, ResetPasswordDTO, AskResetPasswordDTO
from app.model.entity import UserBase
from app.service.auth_service import AuthService

prefix = "/v1/auth"
router = APIRouter()

@router.post("/token", response_model=TokenDTO)
async def login(request: Request, body: OAuth2PasswordRequestForm = Depends()):
    try:
        return await AuthService(request.app.database).login(body.username, body.password)
    except CredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except UpdateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token was not updated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.__str__(),
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.delete("/", response_model=None)
async def logout(request: Request):
    try:
        return await AuthService(request.app.database).logout(request.state.user)
    except ForbiddenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can't logout user",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except UpdateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token was not updated",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.post("/reset-password", response_model=None)
async def ask_new_password(request: Request, body: AskResetPasswordDTO):
    try:
        return await AuthService(request.app.database).ask_new_password(body)
    except ForbiddenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password was not updated",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.put("/reset-password", response_model=None)
async def reset_password(request: Request, body: ResetPasswordDTO, query_params = Depends()):
    try:
        if body.password != body.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password and confirm password do not match",
                headers={"WWW-Authenticate": "Bearer"}
            )

        token = query_params.get("token")
        return await AuthService(request.app.database).reset_password(token, body)
    except ForbiddenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password was not updated",
            headers={"WWW-Authenticate": "Bearer"}
        )