import json
import os
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Any
from data_class.processed_chunk import ProcessedChunk

class RAGDataProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_all_data(self, tech_docs_dir: str = "technical_docs", github_dir: str = "github_data") -> List[Dict]:
        """
        Carrega todos os dados coletados
        """
        all_documents = []

        # Carrega documentações técnicas
        if Path(tech_docs_dir).exists():
            for file_path in Path(tech_docs_dir).glob("*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    doc = json.load(f)
                    doc['source_type'] = 'technical_docs'
                    all_documents.append(doc)

        # Carrega dados do GitHub
        if Path(github_dir).exists():
            for file_path in Path(github_dir).glob("*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    doc = json.load(f)
                    doc['source_type'] = 'github'
                    all_documents.append(doc)

        print(f"📂 Total de documentos carregados: {len(all_documents)}")
        return all_documents

    def clean_text(self, text: str) -> str:
        """
        Limpa e normaliza o texto
        """
        # Remove múltiplos espaços e quebras de linha
        text = re.sub(r'\s+', ' ', text)

        # Remove caracteres especiais mas mantém pontuação básica
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)

        # Normaliza espaços around punctuation
        text = re.sub(r'\s+([.,!?;:)])', r'\1', text)
        text = re.sub(r'([(])\s+', r'\1', text)

        return text.strip()

    def intelligent_chunking(self, content: str, metadata: Dict) -> List[ProcessedChunk]:
        """
        Divisão inteligente do conteúdo mantendo contexto semântico
        """
        chunks = []

        # Estratégias diferentes baseadas no tipo de conteúdo
        content_type = metadata.get('content_type', '')

        if content_type == 'technical_documentation':
            chunks = self._chunk_technical_docs(content, metadata)
        elif content_type == 'github_documentation':
            chunks = self._chunk_github_content(content, metadata)
        elif content_type == 'forum_qa':
            chunks = self._chunk_forum_content(content, metadata)
        else:
            chunks = self._chunk_generic(content, metadata)

        return chunks

    def _chunk_technical_docs(self, content: str, metadata: Dict) -> List[ProcessedChunk]:
        """
        Divisão para documentação técnica (preserva estrutura de tópicos)
        """
        chunks = []

        # Divide por headings (##, ###)
        sections = re.split(r'(?=\n#{2,3}\s+)', content)

        current_chunk = ""
        for section in sections:
            if len(current_chunk) + len(section) <= self.chunk_size:
                current_chunk += section
            else:
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, metadata))

                # Se a seção individual for muito grande, divide por sentenças
                if len(section) > self.chunk_size:
                    sub_chunks = self._split_by_sentences(section, metadata)
                    chunks.extend(sub_chunks)
                else:
                    current_chunk = section

        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, metadata))

        return chunks

    def _chunk_github_content(self, content: str, metadata: Dict) -> List[ProcessedChunk]:
        """
        Divisão para conteúdo do GitHub (READMEs, código, etc.)
        """
        chunks = []

        # Para READMEs, preserva estrutura de markdown
        if metadata.get('file_type') == 'markdown':
            return self._chunk_markdown_content(content, metadata)
        # Para código, preserva funções/métodos completos
        elif metadata.get('file_type') == 'code':
            return self._chunk_code_content(content, metadata)
        else:
            return self._chunk_generic(content, metadata)

    def _chunk_markdown_content(self, content: str, metadata: Dict) -> List[ProcessedChunk]:
        """
        Divisão para conteúdo Markdown
        """
        chunks = []

        # Divide por headers de markdown
        sections = re.split(r'(?=\n#+\s+)', content)

        for section in sections:
            if len(section) <= self.chunk_size:
                chunks.append(self._create_chunk(section, metadata))
            else:
                # Seção muito grande, divide por parágrafos
                paragraphs = section.split('\n\n')
                current_chunk = ""

                for para in paragraphs:
                    if len(current_chunk) + len(para) <= self.chunk_size:
                        current_chunk += para + "\n\n"
                    else:
                        if current_chunk:
                            chunks.append(self._create_chunk(current_chunk, metadata))
                        current_chunk = para + "\n\n"

                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, metadata))

        return chunks

    def _chunk_code_content(self, content: str, metadata: Dict) -> List[ProcessedChunk]:
        """
        Divisão para conteúdo de código
        """
        chunks = []

        # Tenta dividir por funções/classes (para várias linguagens)
        patterns = [
            r'(?=\n(?:def|class)\s+)',  # Python
            r'(?=\n(?:function|class)\s+)',  # JavaScript
            r'(?=\n(?:public|private|protected)\s+)',  # Java/C#
        ]

        for pattern in patterns:
            if re.search(pattern, content):
                sections = re.split(pattern, content)
                for section in sections:
                    if 50 < len(section) <= self.chunk_size:
                        chunks.append(self._create_chunk(section, metadata))
                break
        else:
            # Fallback: divisão por linhas
            return self._chunk_generic(content, metadata)

        return chunks

    def _chunk_forum_content(self, content: str, metadata: Dict) -> List[ProcessedChunk]:
        """
        Divisão para conteúdo de fórum (Q&A)
        """
        chunks = []

        # Divide por perguntas e respostas
        if "PERGUNTA:" in content and "RESPOSTA" in content:
            parts = content.split("RESPOSTA")
            for part in parts:
                if part.strip():
                    chunks.append(self._create_chunk(part.strip(), metadata))
        else:
            chunks = self._chunk_generic(content, metadata)

        return chunks

    def _chunk_generic(self, content: str, metadata: Dict) -> List[ProcessedChunk]:
        """
        Divisão genérica por sentenças
        """
        return self._split_by_sentences(content, metadata)

    def _split_by_sentences(self, text: str, metadata: Dict) -> List[ProcessedChunk]:
        """
        Divide texto por sentenças mantendo contexto
        """
        chunks = []

        # Divisão por sentenças (., !, ?)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk.strip(), metadata))
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(self._create_chunk(current_chunk.strip(), metadata))

        return chunks

    def _create_chunk(self, content: str, metadata: Dict) -> ProcessedChunk:
        """
        Cria um chunk processado com metadados
        """
        clean_content = self.clean_text(content)

        # Cria ID único baseado no conteúdo e metadados
        chunk_id = hashlib.md5(
            f"{clean_content}{metadata.get('url', '')}".encode()
        ).hexdigest()

        # Metadados enriquecidos
        enhanced_metadata = {
            **metadata,
            'chunk_length': len(clean_content),
            'word_count': len(clean_content.split()),
            'language': 'en',  # Assumindo inglês para seu caso
            'processing_timestamp': str(os.times().elapsed)
        }

        return ProcessedChunk(
            content=clean_content,
            metadata=enhanced_metadata,
            chunk_id=chunk_id
        )

    def process_all_data(self, tech_docs_dir: str = "technical_docs", github_dir: str = "github_data") -> List[ProcessedChunk]:
        """
        Processa todos os dados e retorna chunks prontos para o RAG
        """
        documents = self.load_all_data(tech_docs_dir, github_dir)

        all_chunks = []

        for doc in documents:
            try:
                content = doc.get('content', '')
                metadata = doc.get('metadata', {})
                source_type = doc.get('source_type', 'unknown')

                # Adiciona source_type aos metadados
                metadata['source_type'] = source_type

                chunks = self.intelligent_chunking(content, metadata)
                all_chunks.extend(chunks)

                print(f"✅ Processado: {metadata.get('title', 'Unknown')} -> {len(chunks)} chunks")

            except Exception as e:
                print(f"❌ Erro ao processar documento: {e}")
                continue

        print(f"\n🎯 Total de chunks gerados: {len(all_chunks)}")

        # Estatísticas
        self._print_statistics(all_chunks)

        return all_chunks

    def _print_statistics(self, chunks: List[ProcessedChunk]):
        """Exibe estatísticas dos chunks processados"""
        sources = {}
        content_types = {}
        tech_categories = {}
        chunk_sizes = []

        for chunk in chunks:
            source = chunk.metadata.get('source_type', 'unknown')
            content_type = chunk.metadata.get('content_type', 'unknown')
            technology = chunk.metadata.get('technology', 'unknown')

            sources[source] = sources.get(source, 0) + 1
            content_types[content_type] = content_types.get(content_type, 0) + 1
            tech_categories[technology] = tech_categories.get(technology, 0) + 1
            chunk_sizes.append(len(chunk.content))

        print("\n📊 Estatísticas do Processamento:")
        print(f"📁 Fontes: {sources}")
        print(f"📄 Tipos de Conteúdo: {content_types}")
        print(f"🔧 Tecnologias: {tech_categories}")
        print(f"📏 Tamanho médio dos chunks: {sum(chunk_sizes) / len(chunk_sizes):.0f} caracteres")

    def save_processed_chunks(self, chunks: List[ProcessedChunk], output_dir: str = "rag_chunks"):
        """
        Salva os chunks processados para uso no RAG
        """
        BASE_PATH = Path(__file__).resolve().parents[2]
        OUTPUT_PATH = os.path.join(BASE_PATH, 'output', output_dir)
        Path(OUTPUT_PATH).mkdir(exist_ok=True)

        # Salva como JSONL (uma linha por chunk)
        output_file = Path(OUTPUT_PATH) / "processed_chunks.jsonl"

        with open(output_file, 'w', encoding='utf-8') as f:
            for chunk in chunks:
                chunk_dict = {
                    'chunk_id': chunk.chunk_id,
                    'content': chunk.content,
                    'metadata': chunk.metadata,
                    'embedding': chunk.embedding
                }
                f.write(json.dumps(chunk_dict, ensure_ascii=False) + '\n')

        print(f"💾 Chunks salvos em: {output_file}")


