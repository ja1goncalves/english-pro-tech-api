from datetime import timedelta
from pymongo.asynchronous.database import AsyncDatabase
from app.exception.exception import CredentialsError, ForbiddenError, UpdateError
from app.model.dto import TokenDTO, UserDTO, ResetPasswordDTO, AskResetPasswordDTO
from app.model.entity import UserBase
from app.service.service import Service, T
from app.util.config import settings
from app.util.security import verify_password, create_access_token, validate_token, get_password_hash
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request
from typing import Callable

import jwt


class AuthService(Service[UserDTO]):
    def __init__(self, db: AsyncDatabase):
        self.db = db
        super().__init__(db.get_collection("user"))

    async def login(self, username: str, password: str) -> TokenDTO:
        user: UserBase = await self.collection.find_one({"username": username})
        if not user or (user and not verify_password(password, user.password)):
            raise CredentialsError()

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )

        user.token = access_token
        updated_user = await self.update(user)
        if not updated_user:
            raise UpdateError("Token was not updated")

        return TokenDTO(access_token=access_token, token_type="bearer")

    async def logout(self, username: str) -> None:
        user: UserBase = await self.collection.find_one({"username": username})
        if not user:
            raise ForbiddenError("User not found")

        user.token = None
        updated_user = await self.update(user)
        if not updated_user:
            raise UpdateError("Token was not updated")

    async def ask_new_password(self, body: AskResetPasswordDTO) -> bool:
        body_field = body.model_dump(by_alias=True)
        user: UserBase = await self.collection.find(body_field).limit(1)[0]
        if not user:
            raise ForbiddenError("User not found")

        return bool(user.email) # TODO send email with reset link or new password

    async def reset_password(self, token: str, body: ResetPasswordDTO) -> bool:
        user = validate_token(self.db, token)
        if user:
            user.password = get_password_hash(body.new_password)
            updated_user = await self.update(user)
            if not updated_user:
                raise UpdateError("Password was not updated")
            return True
        else:
            raise ForbiddenError("Token was not valid")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        # Exclude specific paths from authentication, e.g., login or public routes
        if request.url.path in settings.OPEN_ROUTES:
            response = await call_next(request)
            return response

        # Extract and validate token (e.g., JWT)
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)

        token = auth_header.split(" ")[1]
        try:
            # Replace with your actual token validation logic
            # e.g., decode JWT, verify signature, check expiration
            user_data = validate_token(request.app.database, token)
            request.state.user = user_data # Store user data for later access in routes
        except Exception as e:
            return JSONResponse({"detail": f"Invalid token: {e}"}, status_code=401)

        response = await call_next(request)
        return response
