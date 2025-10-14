from fastapi import APIRouter
import app.controller.auth_controller as auth
import app.controller.user_controller as user
import app.controller.admin_controller as admin
import app.controller.role_play_controller as play

api = APIRouter()

api.include_router(auth.router, prefix=auth.prefix, tags=["Authentication"])
api.include_router(admin.router, prefix=admin.prefix, tags=["Admin Management"])
api.include_router(user.router, prefix=user.prefix, tags=["User Management"])
api.include_router(play.router, prefix=play.prefix, tags=["Roles Plays"])
