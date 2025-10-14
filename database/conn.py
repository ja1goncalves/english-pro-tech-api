from fastapi import FastAPI
from app.util.config import settings
from pymongo import AsyncMongoClient


class Connection:

    def __init__(self, app: FastAPI):
        self.app = app

    async def startup_db_client(self):
        self.app.mongodb_client = AsyncMongoClient(settings.DB_URI)
        self.app.database = self.app.mongodb_client[settings.DB_NAME]

    async def shutdown_db_client(self):
        await self.app.mongodb_client.close()