import json

from fastapi import FastAPI

from app.model.type import UserProfile
from app.util.config import settings
from pymongo import AsyncMongoClient

from app.util.security import get_password_hash


class Connection:

    def __init__(self, app: FastAPI):
        self.app = app

    async def startup_db_client(self):
        self.app.mongodb_client = AsyncMongoClient(settings.DB_URI)
        self.app.database = self.app.mongodb_client[settings.DB_NAME]

        await self.init_collections()

    async def shutdown_db_client(self):
        await self.app.mongodb_client.close()

    async def init_collections(self):
        collections = await self.app.database.list_collection_names()
        if "role" not in collections:
            await self.app.database.create_collection("role_play")

        if "user" not in collections:
            await self.app.database.create_collection("user")

        await self.populate_initial_data()

    async def populate_initial_data(self):
        roles_collection = self.app.database.get_collection("role")
        existing_roles = await roles_collection.count_documents({})
        if existing_roles == 0:
            initial_roles = json.load(open("./role_play.json"))
            await roles_collection.insert_many(initial_roles)

        user_collection = self.app.database.get_collection("user")
        existing_users = await user_collection.count_documents({})
        if existing_users == 0:
            admin = {
                "username": "admin",
                "email": "admin@admin.com",
                "password": get_password_hash(settings.DB_NAME),
                "name": "Admin User",
                "profile": UserProfile.ADMIN
            };
            await user_collection.insert_one(admin)
