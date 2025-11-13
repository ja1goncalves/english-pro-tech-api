import os
from pathlib import Path
from technical_docs_fetcher import TechnicalDocsFetcher
from github_data_fetcher import GitHubDataFetcher
from rag_data_processor import RAGDataProcessor
from rag_vectors_store import RAGVectorStore
from tech_english_rag_system import TechEnglishRAGSystem

class DataIngestion:
    def fetch_technical_docs(self):
        fetcher = TechnicalDocsFetcher(delay=1.0, max_pages_per_source=20)
        # fetcher.debug_django_structure()
        print("🚀 Iniciando coleta de documentação técnica...")
        documents = fetcher.fetch_technical_docs()

        print(f"✅ Coleta concluída! {len(documents)} documentos coletados.")
        fetcher.save_documents(documents)

        # Estatísticas
        categories = {}
        technologies = {}
        for doc in documents:
            category = doc["metadata"].category
            tech = doc["metadata"].technology

            categories[category] = categories.get(category, 0) + 1
            technologies[tech] = technologies.get(tech, 0) + 1

        print("\n📊 Estatísticas da Coleta:")
        print(f"📁 Categorias: {categories}")
        print(f"🔧 Tecnologias: {technologies}")

    def extract_github_content(self):
        GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

        # 🔥 MODO AGRESSIVO para mais dados
        fetcher = GitHubDataFetcher(
            delay=1.0,
            github_token=GITHUB_TOKEN,
            aggressive_mode=False
        )

        print("🚀 Iniciando coleta AGRESSIVA de dados do GitHub...")
        print("⚡ Modo: AGRESSIVO (mais dados, maior risco de rate limiting)")

        documents = fetcher.fetch_all_repos_data()
        print(f"\n✅ Coleta concluída! {len(documents)} documentos coletados.")

        if documents:
            fetcher.save_documents(documents)

            # Estatísticas detalhadas
            repos = {};
            file_types = {};
            contexts = {}
            for doc in documents:
                repo = doc["metadata"].repo
                file_type = doc["metadata"].file_type
                context = doc["metadata"].professional_context
                repos[repo] = repos.get(repo, 0) + 1
                file_types[file_type] = file_types.get(file_type, 0) + 1
                contexts[context] = contexts.get(context, 0) + 1

            print("\n📊 Estatísticas da Coleta AGRESSIVA:")
            print(f"📁 Repositórios: {repos}")
            print(f"📄 Tipos de Arquivo: {file_types}")
            print(f"🎯 Contextos: {contexts}")
            print(f"💾 Total de documentos: {len(documents)}")

    def process_video_transcripts(self):
        # Tutorials, technical talks
        pass

    # Pipeline Completo
    def run_full_rag_pipeline2(self):
        """
        Executa o pipeline completo de processamento RAG
        """
        print("🚀 Iniciando pipeline RAG completo...")
        BASE_PATH = Path(__file__).resolve().parents[2]
        tech_docs_dir = os.path.join(BASE_PATH, 'output', 'technical_docs')
        github_dir = os.path.join(BASE_PATH, 'output', 'github_data')

        # 1. Processamento dos dados
        processor = RAGDataProcessor(chunk_size=800, chunk_overlap=150)
        chunks = processor.process_all_data(tech_docs_dir, github_dir)

        # 2. Salva chunks processados
        processor.save_processed_chunks(chunks)

        # 3. Configura vector store (opcional)
        vector_db_path = os.path.join(BASE_PATH, 'vector_db')
        vector_store = RAGVectorStore(vector_db_path=vector_db_path)
        vector_store.setup_vector_store(chunks)

        print("🎉 Pipeline RAG concluído!")
        return chunks

    def run_full_rag_pipeline(self) -> TechEnglishRAGSystem:
        """
        Executa o pipeline completo - VERSÃO CORRIGIDA
        """
        print("🚀 Iniciando pipeline RAG completo...")

        try:
            # 1. Processa os dados
            processor = RAGDataProcessor()
            chunks = processor.process_all_data()

            # 2. Salva chunks processados
            processor.save_processed_chunks(chunks)

            # 3. Inicializa sistema RAG
            rag_system = TechEnglishRAGSystem()

            print("🎉 Pipeline RAG concluído com sucesso!")
            return rag_system

        except Exception as e:
            print(f"❌ Erro no pipeline RAG: {e}")
            # Retorna sistema RAG mesmo com erro (pode ter alguns chunks)
            return TechEnglishRAGSystem()

    # Exemplo de uso prático
    def demonstrate_rag_usage(self):
        """Demonstra como usar o sistema RAG de forma robusta"""
        print("🧪 Demonstrando uso do RAG...")

        # Inicializa o sistema RAG
        rag_system = self.run_full_rag_pipeline()

        if not rag_system.vector_store or not rag_system.chunks:
            print("❌ Sistema RAG não foi inicializado corretamente")
            return

        # Exemplos de consultas práticas para aprendizado de inglês técnico
        example_queries = [
            "How to explain a bug to my team?",
            "What is the difference between function and method?",
            "How to ask for help in code review?",
            "Explain API documentation",
            "Daily standup meeting phrases",
            "How to describe technical problems?",
            "Git commit message examples",
            "Code review comments in English"
        ]

        print("\n🔍 Testando consultas RAG...")

        for i, query in enumerate(example_queries, 1):
            print(f"\n{i}. ❓ '{query}'")

            results = rag_system.query_rag(query, context="development", n_results=3)

            if results['success'] and results['context_chunks']:
                print(f"   ✅ Encontrados {results['total_chunks_found']} resultados:")

                for j, chunk in enumerate(results['context_chunks'][:2], 1):
                    print(f"      {j}. 📚 [{chunk['technology']}] {chunk['content'][:80]}...")
                    print(f"         🎯 Contexto: {chunk['professional_context']}")
                    print(f"         📊 Relevância: {chunk['relevance_score']:.3f}")
            else:
                print(f"   ❌ Nenhum resultado encontrado")
                if 'error' in results:
                    print(f"      Erro: {results['error']}")
