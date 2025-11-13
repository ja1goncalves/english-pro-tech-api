import chromadb
from typing import List
from resource.rag_system.data_class.processed_chunk import ProcessedChunk

class RAGVectorStore:
    def __init__(self, vector_db_path: str = "vector_db"):
        self.vector_db_path = vector_db_path

    def setup_vector_store(self, chunks: List[ProcessedChunk]):
        """
        Configura o banco de dados vetorial (exemplo com ChromaDB)
        """
        try:
            client = chromadb.PersistentClient(path=self.vector_db_path)

            # Cria ou obtém a collection
            collection = client.get_or_create_collection(
                name="tech_english_rag",
                metadata={"description": "Technical English learning content"}
            )

            # Prepara dados para inserção
            documents = []
            metadatas = []
            ids = []

            for chunk in chunks:
                documents.append(chunk.content)
                metadatas.append(chunk.metadata)
                ids.append(chunk.chunk_id)

            # Insere no vector store
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            print(f"✅ Vector store configurado com {len(chunks)} chunks")

        except ImportError:
            print("❌ ChromaDB não instalado. Instale com: pip install chromadb")
        except Exception as e:
            print(f"❌ Erro ao configurar vector store: {e}")
