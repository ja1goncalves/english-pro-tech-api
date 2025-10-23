import json

from fastapi import FastAPI

from app.model.type import UserProfile
from app.util.config import settings
from pymongo import AsyncMongoClient

from app.util.security import get_password_hash
from database.collections import Table


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
        if Table.ROLE_PLAY not in collections:
            await self.app.database.create_collection(Table.ROLE_PLAY)

        if Table.USER not in collections:
            await self.app.database.create_collection(Table.USER)

        await self.populate_initial_data()

    async def populate_initial_data(self):
        roles_collection = self.app.database.get_collection(Table.ROLE_PLAY)
        existing_roles = await roles_collection.count_documents({})
        with open("./database/role_play.json", "r") as f:
            initial_roles = json.load(f)
            if existing_roles == 0:
                await roles_collection.insert_many(initial_roles["role"])
            else:
                for role in initial_roles["role"]:
                    await roles_collection.update_one({"code": role["code"]}, {"$set": role}, upsert=True)


        user_collection = self.app.database.get_collection(Table.USER)
        existing_users = await user_collection.count_documents({})
        if existing_users == 0:
            admin = {
                "username": "admin",
                "email": "admin@admin.com",
                "password": get_password_hash(settings.ADMIN_PASSWORD),
                "name": "Admin User",
                "profile": UserProfile.ADMIN
            };
            await user_collection.insert_one(admin)
        else:
            await user_collection.update_one(
                {"username": "admin"},
                {
                    "$set": {
                        "password": get_password_hash(settings.ADMIN_PASSWORD),
                        "profile": UserProfile.ADMIN
                    }
                },
                upsert=True
            )
