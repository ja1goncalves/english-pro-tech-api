import requests
import base64
import time
import os
import json
from typing import List, Dict, Optional
from pathlib import Path
from resource.rag_system.data_class.github_doc_metadata import GitHubDocMetadata

class GitHubDataFetcher:
    def __init__(self, delay: float = 1.5, github_token: Optional[str] = None, aggressive_mode: bool = False):
        self.delay = delay
        self.github_token = github_token
        self.aggressive_mode = aggressive_mode  # Modo mais agressivo para mais dados
        self.session = requests.Session()

        # Headers para a API do GitHub
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'TechEnglish-RAG-Bot/1.0'
        }
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        self.session.headers.update(headers)

        # ESTRATÉGIA HÍBRIDA - Mais abrangente mas com controles
        self.target_repos = {
            "react": {
                "owner": "facebook",
                "repo": "react",
                "paths": [
                    "README.md",
                    "docs/",
                    "packages/react/README.md",
                    "packages/react-dom/README.md",
                    "packages/react-reconciler/README.md"
                ],
                "tech_category": "frontend",
                "max_depth": 2 if aggressive_mode else 1
            },
            "typescript": {
                "owner": "microsoft",
                "repo": "TypeScript",
                "paths": [
                    "README.md",
                    "doc/",
                    "documentation/",
                    "src/",
                    "lib/"
                ],
                "tech_category": "programming_language",
                "max_depth": 2 if aggressive_mode else 1
            },
            "docker_docs": {
                "owner": "docker",
                "repo": "docs",
                "paths": [
                    "README.md",
                    "get-started/",
                    "guides/",
                    "config/",
                    "compose/",
                    "engine/",
                    "storage/",
                    "network/"
                ],
                "tech_category": "devops",
                "max_depth": 2 if aggressive_mode else 1
            },
            "gitignore": {
                "owner": "github",
                "repo": "gitignore",
                "paths": [
                    "README.md",
                    "*.gitignore"
                ],
                "tech_category": "tools",
                "max_depth": 1
            }
        }

    async def fetch_all_repos_data(self) -> List[Dict]:
        """
        Coleta dados de todos os repositórios com estratégia balanceada
        """
        all_documents = []

        for repo_name, repo_config in self.target_repos.items():
            print(f"🔍 Coletando dados de: {repo_config['owner']}/{repo_config['repo']}")

            try:
                # Verificação de rate limit inteligente
                if not self._check_rate_limit():
                    wait_time = 30 if self.github_token else 60
                    print(f"   ⏳ Rate limit baixo, aguardando {wait_time}s...")
                    time.sleep(wait_time)

                documents = await self._fetch_repository_data(
                    repo_config['owner'],
                    repo_config['repo'],
                    repo_config['paths'],
                    repo_config['tech_category'],
                    repo_name,
                    repo_config.get('max_depth', 1)
                )
                all_documents.extend(documents)
                print(f"   ✅ {len(documents)} documentos coletados")

                time.sleep(self.delay)

            except Exception as e:
                print(f"   ❌ Erro ao coletar {repo_name}: {str(e)}")
                continue

        return all_documents

    def _check_rate_limit(self) -> bool:
        """Verifica rate limit com margem de segurança"""
        try:
            response = self.session.get("https://api.github.com/rate_limit")
            if response.status_code == 200:
                data = response.json()
                core_limit = data['resources']['core']
                remaining = core_limit['remaining']
                limit = core_limit['limit']

                # Margem mais agressiva no modo agressivo
                threshold = 5 if self.aggressive_mode else 10
                print(f"   📊 Rate Limit: {remaining}/{limit}")
                return remaining > threshold
        except Exception as e:
            print(f"   ⚠️ Erro ao verificar rate limit: {e}")
        return True

    async def _fetch_repository_data(self, owner: str, repo: str, paths: List[str], tech_category: str, repo_alias: str, max_depth: int = 1) -> List[Dict]:
        """
        Coleta dados com estratégia adaptativa baseada no modo
        """
        documents = []
        files_processed = 0
        max_files = 50 if self.aggressive_mode else 20

        for path in paths:
            if files_processed >= max_files:
                print(f"   ⏹️  Limite de {max_files} arquivos atingido para {repo_alias}")
                break

            try:
                print(f"   📁 Processando caminho: {path}")

                if path.endswith('/'):
                    # Diretório - estratégia baseada no modo
                    dir_docs = self._fetch_directory_contents_adaptive(
                        owner, repo, path, tech_category, repo_alias, max_depth
                    )
                    documents.extend(dir_docs)
                    files_processed += len(dir_docs)
                elif '*' in path:
                    # Padrão de arquivos
                    pattern_docs = self._fetch_files_by_pattern_adaptive(
                        owner, repo, path, tech_category, repo_alias
                    )
                    documents.extend(pattern_docs)
                    files_processed += len(pattern_docs)
                else:
                    # Arquivo específico
                    file_doc = self._fetch_single_file(owner, repo, path, tech_category, repo_alias)
                    if file_doc:
                        documents.append(file_doc)
                        files_processed += 1

                # Delay adaptativo
                delay = self.delay * 0.3 if self.aggressive_mode else self.delay * 0.5
                time.sleep(delay)

            except Exception as e:
                print(f"      ⚠️ Erro no caminho {path}: {str(e)}")
                continue

        return documents

    def _fetch_directory_contents_adaptive(self, owner: str, repo: str, directory: str, tech_category: str, repo_alias: str, max_depth: int) -> List[Dict]:
        """
        Busca conteúdo de diretório com estratégia adaptativa
        """
        documents = []
        try:
            if not self._check_rate_limit():
                return documents

            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{directory}"
            response = self.session.get(url)

            if response.status_code != 200:
                self._handle_api_error(response.status_code, directory)
                return documents

            contents = response.json()

            # Estratégia baseada no modo
            file_limit = 15 if self.aggressive_mode else 8
            processed_files = 0

            for item in contents:
                if processed_files >= file_limit:
                    break

                if item['type'] == 'file' and self._is_valuable_file(item['name']):
                    file_doc = self._fetch_single_file(owner, repo, item['path'], tech_category, repo_alias)
                    if file_doc:
                        documents.append(file_doc)
                        processed_files += 1

                    time.sleep(self.delay * 0.2)

                elif item['type'] == 'dir' and max_depth > 0:
                    # Recursão limitada
                    sub_docs = self._fetch_directory_contents_adaptive(
                        owner, repo, item['path'], tech_category, repo_alias, max_depth - 1
                    )
                    documents.extend(sub_docs)
                    processed_files += len(sub_docs)

        except Exception as e:
            print(f"      ❌ Erro no diretório {directory}: {str(e)}")

        return documents

    def _fetch_files_by_pattern_adaptive(self, owner: str, repo: str, pattern: str, tech_category: str, repo_alias: str) -> List[Dict]:
        """
        Busca arquivos por padrão de forma adaptativa
        """
        documents = []
        try:
            # Especialmente para gitignore
            if pattern == "*.gitignore" and repo_alias == "gitignore":
                url = f"https://api.github.com/repos/{owner}/{repo}/contents"
                response = self.session.get(url)

                if response.status_code == 200:
                    contents = response.json()

                    # Limite baseado no modo
                    file_limit = 20 if self.aggressive_mode else 10
                    gitignore_files = [
                                          item for item in contents
                                          if item['type'] == 'file'
                                             and item['name'].endswith('.gitignore')
                                      ][:file_limit]

                    for item in gitignore_files:
                        file_doc = self._fetch_single_file(owner, repo, item['path'], tech_category, repo_alias)
                        if file_doc:
                            documents.append(file_doc)
                        time.sleep(self.delay * 0.2)

        except Exception as e:
            print(f"      ❌ Erro no padrão {pattern}: {str(e)}")

        return documents

    def _is_valuable_file(self, filename: str) -> bool:
        """Identifica arquivos valiosos para coleta"""
        name_lower = filename.lower()

        # Extensões de documentação
        doc_extensions = ['.md', '.rst', '.txt', '.adoc', '.asciidoc']

        # Arquivos de configuração importantes
        config_files = ['dockerfile', 'docker-compose', 'package.json', 'tsconfig.json']

        # Palavras-chave em nomes de arquivos
        doc_keywords = [
            'readme', 'license', 'contributing', 'docs', 'guide', 'tutorial',
            'getting-started', 'quickstart', 'api', 'reference', 'manual'
        ]

        return (
                any(name_lower.endswith(ext) for ext in doc_extensions) or
                any(keyword in name_lower for keyword in doc_keywords) or
                any(config in name_lower for config in config_files)
        )

    def _handle_api_error(self, status_code: int, path: str):
        """Trata erros da API de forma inteligente"""
        if status_code == 403:
            print(f"      ⚠️  Acesso proibido (403) em: {path}")
        elif status_code == 404:
            print(f"      🔍 Caminho não encontrado (404): {path}")
        elif status_code == 429:
            print(f"      ⏳ Rate limit atingido em: {path}")
            wait = 30 if self.github_token else 60
            print(f"      💤 Aguardando {wait} segundos...")
            time.sleep(wait)
        else:
            print(f"      ⚠️  Erro {status_code} em: {path}")

    def _fetch_single_file(self, owner: str, repo: str, file_path: str, tech_category: str, repo_alias: str) -> Optional[Dict]:
        """
        Busca um arquivo individual (mantido da versão anterior)
        """
        try:
            if not self._check_rate_limit():
                return None

            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
            response = self.session.get(url)

            if response.status_code != 200:
                self._handle_api_error(response.status_code, file_path)
                return None

            file_info = response.json()
            content = self._extract_file_content(file_info)

            if not content or len(content.strip()) < 10:
                return None

            # Metadados
            title = self._extract_title(file_path, content)
            professional_context = self._determine_professional_context(content, tech_category)
            english_level = self._estimate_english_level(content)

            metadata = GitHubDocMetadata(
                title=title,
                url=file_info['html_url'],
                repo=f"{owner}/{repo}",
                file_path=file_path,
                file_type=self._get_file_type(file_path),
                technology=repo_alias,
                professional_context=professional_context,
                english_level=english_level,
                content_type="github_documentation",
                last_updated=str(time.time())
            )

            return {
                "metadata": metadata,
                "content": content,
                "raw_content": content,
                "word_count": len(content.split()),
                "key_terms": self._extract_key_terms(content),
                "file_info": {
                    "size": file_info.get('size', 0),
                    "sha": file_info.get('sha', ''),
                    "download_url": file_info.get('download_url', '')
                }
            }

        except Exception as e:
            print(f"      ❌ Erro no arquivo {file_path}: {str(e)}")
            return None

    # Métodos auxiliares mantidos da versão anterior
    def _extract_file_content(self, file_info: Dict) -> Optional[str]:
        try:
            if file_info.get('encoding') == 'base64':
                return base64.b64decode(file_info['content']).decode('utf-8')
            else:
                download_url = file_info.get('download_url')
                if download_url:
                    response = self.session.get(download_url)
                    if response.status_code == 200:
                        return response.text
            return None
        except:
            return None

    def _extract_title(self, file_path: str, content: str) -> str:
        if file_path.lower().endswith('readme.md'):
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('# '):
                    return line.replace('# ', '').strip()
        return Path(file_path).name

    def _get_file_type(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        if ext == '.md':
            return 'markdown'
        elif ext in ['.js', '.ts', '.py']:
            return 'code'
        elif ext in ['.yml', '.yaml', '.json']:
            return 'configuration'
        else:
            return 'documentation'

    def _determine_professional_context(self, content: str, tech_category: str) -> str:
        content_lower = content.lower()
        context_keywords = {
            "getting_started": ["getting started", "quickstart", "installation"],
            "api_reference": ["api", "reference", "interface", "method"],
            "configuration": ["config", "setup", "environment", "settings"],
            "best_practices": ["best practice", "guideline", "recommendation"],
            "tutorial": ["tutorial", "example", "walkthrough", "guide"]
        }
        scores = {context: 0 for context in context_keywords}
        for context, keywords in context_keywords.items():
            for keyword in keywords:
                if keyword in content_lower: scores[context] += 1
        return max(scores.items(), key=lambda x: x[1])[0] if max(scores.values()) > 0 else "documentation"

    def _estimate_english_level(self, content: str) -> str:
        words = content.lower().split()
        if len(words) == 0: return "B1"
        technical_terms = {"implementation", "configuration", "optimization", "architecture"}
        complex_words = sum(1 for word in words if word in technical_terms)
        complex_ratio = complex_words / len(words)
        if complex_ratio > 0.03:
            return "C1"
        elif complex_ratio > 0.01:
            return "B2"
        else:
            return "B1"

    def _extract_key_terms(self, content: str) -> List[str]:
        technical_terms = {
            "function", "method", "class", "object", "variable", "parameter",
            "import", "export", "interface", "implementation", "configuration",
            "deployment", "database", "api", "endpoint", "authentication",
            "component", "state", "props", "hook", "docker", "container",
            "repository", "branch", "commit", "merge", "typescript", "interface"
        }
        words = set(content.lower().split())
        return [term for term in technical_terms if term in words][:15]

    def save_documents(self, documents: List[Dict], output_dir: str = "github_data"):
        # Path(output_dir).mkdir(exist_ok=True)
        BASE_PATH = Path(__file__).resolve().parents[2]
        OUTPUT_PATH = os.path.join(BASE_PATH, 'output', output_dir)
        Path(OUTPUT_PATH).mkdir(exist_ok=True)

        for i, doc in enumerate(documents):
            repo_name = doc["metadata"].repo.replace('/', '_')
            filename = f"{repo_name}_{i}.json"
            filepath = Path(OUTPUT_PATH) / filename
            doc_dict = {
                "metadata": {
                    "title": doc["metadata"].title,
                    "url": doc["metadata"].url,
                    "repo": doc["metadata"].repo,
                    "file_path": doc["metadata"].file_path,
                    "file_type": doc["metadata"].file_type,
                    "technology": doc["metadata"].technology,
                    "professional_context": doc["metadata"].professional_context,
                    "english_level": doc["metadata"].english_level,
                    "content_type": doc["metadata"].content_type,
                    "last_updated": doc["metadata"].last_updated
                },
                "content": doc["content"],
                "word_count": doc["word_count"],
                "key_terms": doc["key_terms"],
                "file_info": doc["file_info"]
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(doc_dict, f, indent=2, ensure_ascii=False)
