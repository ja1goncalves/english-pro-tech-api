from enum import Enum


class Table(str, Enum):
    USER = "user"
    ROLE_PLAY = "role_play"
    RAG_DOC = "rag_docs"
    RAG_CHUNK = "rag_chunks"