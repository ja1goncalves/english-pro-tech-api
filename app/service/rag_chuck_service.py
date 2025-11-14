from pymongo.asynchronous.database import AsyncDatabase
from app.model.entity import ProcessedChunk
from app.service.service import Service
from database.collections import Table


class RagChunkService(Service[ProcessedChunk]):
    def __init__(self, db: AsyncDatabase):
        super().__init__(db.get_collection(Table.RAG_CHUNK))
