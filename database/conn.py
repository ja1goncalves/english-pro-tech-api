import json

from fastapi import FastAPI
import asyncio

from app.model.type import UserProfile
from app.service.rag_doc_service import RagDocService
from app.util.config import settings
from pymongo import AsyncMongoClient

from app.util.role_play import play_code
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

        if Table.RAG_DOC not in collections:
            await self.app.database.create_collection(Table.RAG_DOC)

        if Table.RAG_CHUNK not in collections:
            await self.app.database.create_collection(Table.RAG_CHUNK)

        await self.populate_initial_data()

    async def _populate_role_plays(self):
        roles_collection = self.app.database.get_collection(Table.ROLE_PLAY)
        existing_roles = await roles_collection.count_documents({})
        with open("./database/role_play.json", "r") as f:
            initial_roles = json.load(f)
            if existing_roles == 0:
                for role in initial_roles["role"]:
                    for level in role["level"]:
                        for i, p in enumerate(level["plays"]):
                            p["code"] = play_code(role['code'], level['step'], i)

                await roles_collection.insert_many(initial_roles["role"])
            else:
                for role in initial_roles["role"]:
                    for level in role["level"]:
                        for i, p in enumerate(level["plays"]):
                            p["code"] = play_code(role['code'], level['step'], i)
                    await roles_collection.update_one({"code": role["code"]}, {"$set": role}, upsert=True)

    async def _populate_users(self):
        user_collection = self.app.database.get_collection(Table.USER)
        existing_users = await user_collection.count_documents({})
        if existing_users == 0:
            admin = {
                "username": "admin",
                "email": "admin@admin.com",
                "password": get_password_hash(settings.ADMIN_PASSWORD),
                "name": "Admin User",
                "profile": UserProfile.ADMIN
            }
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

    async def _populate_rag(self):
        rag_docs_collection = self.app.database.get_collection(Table.RAG_DOC)
        rag_chunk_collection = self.app.database.get_collection(Table.RAG_CHUNK)

        existing_docs = await rag_docs_collection.count_documents({})
        existing_chunk = await rag_chunk_collection.count_documents({})

        if existing_docs == 0 or existing_chunk == 0:
            service = RagDocService(self.app.database)
            result = await service.refresh_rag()
            print(f"RAG initial population build with {'errors' if result else 'success'}.")

    async def populate_initial_data(self):
        await asyncio.gather(
            self._populate_role_plays(),
            self._populate_users(),
            self._populate_rag()
        )
