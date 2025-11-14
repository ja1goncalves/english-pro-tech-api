from pymongo.asynchronous.database import AsyncDatabase
from app.model.entity import RAGDocument
from app.service.service import Service
from database.collections import Table


class RagDocService(Service[RAGDocument]):
    def __init__(self, db: AsyncDatabase):
        super().__init__(db.get_collection(Table.RAG_DOC))
