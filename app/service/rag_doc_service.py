import asyncio
from dataclasses import asdict

from pymongo.asynchronous.database import AsyncDatabase
from app.model.entity import RAGDocument
from app.service.service import Service
from database.collections import Table
from resource.rag_system.data_ingestion import DataIngestion
from resource.rag_system.rag_data_processor import RAGDataProcessor


class RagDocService(Service[RAGDocument]):
    def __init__(self, db: AsyncDatabase):
        self.db = db
        super().__init__(db.get_collection(Table.RAG_DOC))


    async def refresh_rag(self) -> bool:
        data_ingestion = DataIngestion()
        rag_processor = RAGDataProcessor()

        tech_docs, git_docs = await asyncio.gather(
            data_ingestion.fetch_technical_docs(),
            data_ingestion.extract_github_content()
        )
        docs = tech_docs + git_docs

        docs_failed, chunks = await asyncio.gather(
            self._save_rag_docs(docs),
            rag_processor.process_all_data(docs),
        )

        chunks_failed = await self._save_rag_chucks(chunks)

        return bool(docs_failed + chunks_failed)

    async def _save_rag_chucks(self, chucks):
        chucks_fail_count = 0
        for chunk in chucks:
            try:
                rag_chunk_collection = self.db.get_collection(Table.RAG_CHUNK)
                query_filter = {"chunk_id": chunk.chunk_id}
                update_operation = {
                    "$set": {
                        'chunk_id': chunk.chunk_id,
                        'content': chunk.content,
                        'metadata': chunk.metadata,
                        'embedding': chunk.embedding
                    }
                }
                await rag_chunk_collection.update_one(query_filter, update_operation, upsert=True)
            except Exception as e:
                print(f"❌ Erro ao salvar Chunk RAG: {e}")
                chucks_fail_count += 1
                continue

        return chucks_fail_count


    async def _save_rag_docs(self, docs):
        doc_fail_count = 0
        for doc in docs:
            try:
                rag_docs_collection = self.db.get_collection(Table.RAG_DOC)
                query_filter = {"metadata.url": doc["metadata"].url}
                update_operation = {
                    "$set": {
                        "metadata": asdict(doc.get("metadata")),
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
                continue

        return doc_fail_count