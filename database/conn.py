import json

from fastapi import FastAPI
import asyncio

from app.model.type import UserProfile
from app.util.config import settings
from pymongo import AsyncMongoClient
from resource.rag_system.data_ingestion import DataIngestion
from app.util.role_play import play_code
from app.util.security import get_password_hash
from database.collections import Table
from resource.rag_system.rag_data_processor import RAGDataProcessor


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

        if Table.RAG_DOCS not in collections:
            await self.app.database.create_collection(Table.RAG_DOC)

        if Table.RAG_CHUNKS not in collections:
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

    async def _save_rag_docs(self, docs):
        doc_fail_count = 0
        try:
            for doc in docs:
                rag_docs_collection = self.app.database.get_collection(Table.RAG_DOC)
                query_filter = {"metadata.url": doc["metadata"].url}
                update_operation = {
                    "$set": {
                        "metadata": doc.get("metadata").dict(),
                        "content": doc.get("content"),
                        "word_count": doc.get("word_count"),
                        "key_terms": doc.get("key_terms"),
                        "file_info": doc.get("file_info", {})
                    }
                }
                await rag_docs_collection.update_one(query_filter, update_operation, upsert=True)
        except Exception as e:
            print(f"❌ Erro ao salvar documentos RAG: {e}")
            doc_fail_count += 1

        return doc_fail_count

    async def _save_rag_chucks(self, chucks):
        chucks_fail_count = 0
        try:
            for chunk in chucks:
                rag_chuck_collection = self.app.database.get_collection(Table.RAG_CHUNK)
                query_filter = {"chunk_id": chunk.chunk_id}
                update_operation = {
                    "$set": {
                        'chunk_id': chunk.chunk_id,
                        'content': chunk.content,
                        'metadata': chunk.metadata,
                        'embedding': chunk.embedding
                    }
                }
                await rag_chuck_collection.update_one(query_filter, update_operation, upsert=True)
        except Exception as e:
            print(f"❌ Erro ao salvar documentos RAG: {e}")
            chucks_fail_count += 1

        return chucks_fail_count

    async def _populate_rag(self):
        data_ingestion = DataIngestion()
        rag_processor = RAGDataProcessor()

        tech_docs, git_docs = await asyncio.gather(
            data_ingestion.fetch_technical_docs(),
            data_ingestion.extract_github_content()
        )
        all_docs = tech_docs + git_docs

        chunks, _ =await asyncio.gather(
            rag_processor.process_all_data(all_docs),
            self._save_rag_docs(all_docs),
        )

        await self._save_rag_chucks(chunks)

    async def populate_initial_data(self):
        await asyncio.gather(
            self._populate_role_plays(),
            self._populate_users(),
            self._populate_rag()
        )
