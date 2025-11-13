from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from resource.rag_system.data_class.processed_chunk import ProcessedChunk

class SimpleVectorStore:
    """
    Vector store simplificado em memória para demonstração
    """
    def __init__(self):
        self.chunks = []
        self.embeddings = []
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.is_fitted = False

    def add_chunks(self, chunks: List[ProcessedChunk]):
        """Adiciona chunks ao vector store"""
        self.chunks.extend(chunks)

        # Gera embeddings TF-IDF
        if chunks:
            contents = [chunk.content for chunk in chunks]
            if not self.is_fitted:
                tfidf_matrix = self.vectorizer.fit_transform(contents)
                self.is_fitted = True
            else:
                tfidf_matrix = self.vectorizer.transform(contents)

            # Converte para array denso e adiciona à lista
            new_embeddings = tfidf_matrix.toarray().tolist()
            self.embeddings.extend(new_embeddings)

            # Atualiza os embeddings nos chunks
            for i, chunk in enumerate(chunks):
                chunk.embedding = new_embeddings[i]

    def search(self, query: str, n_results: int = 5, context_filter: str = None) -> List[Dict]:
        """Busca por similaridade"""
        if not self.chunks or not self.is_fitted:
            return []

        try:
            # Transforma a query em embedding TF-IDF
            query_embedding = self.vectorizer.transform([query]).toarray()

            # Filtra chunks por contexto se especificado
            filtered_chunks = self.chunks
            filtered_embeddings = self.embeddings

            if context_filter:
                indices = [
                    i for i, chunk in enumerate(self.chunks)
                    if context_filter.lower() in str(chunk.metadata.get('professional_context', '')).lower()
                ]
                filtered_chunks = [self.chunks[i] for i in indices]
                filtered_embeddings = [self.embeddings[i] for i in indices]

            if not filtered_chunks:
                return []

            # Calcula similaridades
            similarities = cosine_similarity(query_embedding, filtered_embeddings)[0]

            # Ordena por similaridade
            scored_chunks = list(zip(similarities, filtered_chunks))
            scored_chunks.sort(reverse=True, key=lambda x: x[0])

            # Prepara resultados
            results = []
            for score, chunk in scored_chunks[:n_results]:
                results.append({
                    'content': chunk.content,
                    'source': chunk.metadata.get('title', 'Unknown'),
                    'technology': chunk.metadata.get('technology', 'Unknown'),
                    'relevance_score': float(score),
                    'professional_context': chunk.metadata.get('professional_context', 'Unknown'),
                    'english_level': chunk.metadata.get('english_level', 'Unknown')
                })

            return results

        except Exception as e:
            print(f"❌ Erro na busca: {e}")
            return []
