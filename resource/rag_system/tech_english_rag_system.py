import json
from pathlib import Path
from typing import List, Dict
from resource.rag_system.rag_data_processor import RAGDataProcessor
from resource.rag_system.data_class.processed_chunk import ProcessedChunk
from resource.rag_system.simple_vector_store import SimpleVectorStore

class TechEnglishRAGSystem:
    def __init__(self, chunks:List[ProcessedChunk]=[], docs:List[Dict]=[]):
        self.chunks = chunks
        self.docs_to_process = docs
        self.vector_store = SimpleVectorStore()
        # self.setup_rag_system(docs)

    @classmethod
    async def create_and_setup(cls, chunks:List[ProcessedChunk]=[], docs:List[Dict]=[]):
        instance = cls(chunks, docs)
        await instance.setup_rag_system()
        return instance

    async def setup_rag_system(self):
        """Configura o sistema RAG completo"""
        try:
            print("🔄 Configurando sistema RAG...")

            # Carrega chunks processados
            # self.chunks = self._load_processed_chunks()

            if not self.chunks:
                print("⚠️  Nenhum chunk encontrado. Processando dados...")
                processor = RAGDataProcessor()
                self.chunks = await processor.process_all_data(self.docs_to_process)
                # processor.save_processed_chunks(self.chunks)

            self.vector_store.add_chunks(self.chunks)

            print(f"✅ Sistema RAG configurado com {len(self.chunks)} chunks")

        except Exception as e:
            print(f"❌ Erro na configuração do RAG: {e}")

    def _load_processed_chunks(self) -> List[ProcessedChunk]:
        """Carrega chunks processados"""
        chunks = []
        try:
            if Path(self.chunks_path).exists():
                with open(self.chunks_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        data = json.loads(line)
                        chunks.append(ProcessedChunk(
                            content=data['content'],
                            metadata=data['metadata'],
                            chunk_id=data['chunk_id'],
                            embedding=data.get('embedding')
                        ))
                print(f"📂 Carregados {len(chunks)} chunks do arquivo")
            else:
                print("📂 Arquivo de chunks não encontrado")
        except Exception as e:
            print(f"❌ Erro ao carregar chunks: {e}")
        return chunks

    def _setup_embedding_model(self):
        """Configura modelo de embeddings"""
        try:
            from sentence_transformers import SentenceTransformer
            return SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            print("❌ SentenceTransformers não instalado")
            return None

    def query_rag(self, question: str, context: str = "development", n_results: int = 5):
        """
        Consulta o sistema RAG para conteúdo relevante
        """
        try:
            if not self.vector_store:
                return {
                    'question': question,
                    'context_chunks': [],
                    'total_chunks_found': 0,
                    'error': 'Vector store não inicializado'
                }

            # Busca no vector store
            results = self.vector_store.search(
                query=question,
                n_results=n_results,
                context_filter=context
            )

            return {
                'question': question,
                'context_chunks': results,
                'total_chunks_found': len(results),
                'success': True
            }

        except Exception as e:
            print(f"❌ Erro na consulta RAG: {e}")
            return {
                'question': question,
                'context_chunks': [],
                'total_chunks_found': 0,
                'error': str(e),
                'success': False
            }

    def _format_rag_response(self, question: str, results) -> Dict:
        """Formata a resposta do RAG"""
        context_chunks = []

        for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
            context_chunks.append({
                'content': doc,
                'source': metadata.get('title', 'Unknown'),
                'technology': metadata.get('technology', 'Unknown'),
                'relevance_score': metadata.get('score', 0)
            })

        return {
            'question': question,
            'context_chunks': context_chunks,
            'total_chunks_found': len(context_chunks)
        }


