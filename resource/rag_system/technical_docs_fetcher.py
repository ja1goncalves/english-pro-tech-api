import requests
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin, urlparse
import os
from pathlib import Path
from typing import List, Dict, Optional
from data_class.document_metadata import DocumentMetadata

class TechnicalDocsFetcher:
    def __init__(self, delay: float = 1.0, max_pages_per_source: int = 50):
        self.delay = delay  # Delay entre requisições
        self.max_pages = max_pages_per_source
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # Configuração de fontes técnicas organizadas por categoria
        self.technical_sources = {
            "programming_languages": {
                "python": {
                    "base_url": "https://docs.python.org/3/",
                    "start_urls": [
                        "https://docs.python.org/3/tutorial/index.html",
                        "https://docs.python.org/3/library/index.html",
                        "https://docs.python.org/3/howto/index.html"
                    ],
                    "selectors": {
                        "content": ".body",
                        "links": ".sphinxsidebar a.reference",  # Seletor mais específico
                        "pagination": None
                    },
                    "valid_paths": ["/tutorial/", "/library/", "/howto/", "/reference/"]
                },
                "javascript": {
                    "base_url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
                    "start_urls": [
                        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
                        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference",
                        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects"
                    ],
                    "selectors": {
                        "content": ".article-content, .main-page-content, main",
                        "links": ".sidebar .toggle li a, .sidebar-nav a, .prev-next a, .sidebar a[href*='/JavaScript/']"
                    },
                    "valid_paths": ["/JavaScript/Guide/", "/JavaScript/Reference/"],
                    "max_depth": 2
                },
                "typescript": {
                    "base_url": "https://www.typescriptlang.org/docs/",
                    "start_urls": [
                        "https://www.typescriptlang.org/docs/handbook/intro.html",
                        "https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes.html"
                    ],
                    "selectors": {
                        "content": ".docs-content, main, article",
                        "links": ".docs-sidebar a, nav a[href*='/handbook/']"
                    },
                    "valid_paths": ["/handbook/", "/docs/"],
                    "max_depth": 2
                },
                "go": {
                    "base_url": "https://go.dev/doc/",
                    "start_urls": [
                        "https://go.dev/doc/tutorial/getting-started",
                        "https://go.dev/doc/effective_go"
                    ],
                    "selectors": {
                        "content": ".Documentation, main, article",
                        "links": ".Navigation a, nav a"
                    },
                    "valid_paths": ["/doc/", "/tutorial/"],
                    "max_depth": 2
                },
                "rust": {
                    "base_url": "https://doc.rust-lang.org/book/",
                    "start_urls": [
                        "https://doc.rust-lang.org/book/ch01-00-getting-started.html",
                        "https://doc.rust-lang.org/rust-by-example/"
                    ],
                    "selectors": {
                        "content": ".content, main, .chapter",
                        "links": ".sidebar a, .chapter a"
                    },
                    "valid_paths": ["/book/", "/rust-by-example/"],
                    "max_depth": 2
                }
            },

            "frameworks": {
                "react": {
                    "base_url": "https://react.dev/",
                    "start_urls": [
                        "https://react.dev/learn",
                        "https://react.dev/learn/installation",
                        "https://react.dev/reference/react"
                    ],
                    "selectors": {
                        "content": ".docSearch-content, article, [data-language='js']",
                        "links": "nav a[href^='/'], .sidebar a, a[href*='/learn/'], a[href*='/reference/']"
                    },
                    "valid_paths": ["/learn/", "/reference/"],
                    "max_depth": 2
                },
                "django": {
                    "base_url": "https://docs.djangoproject.com/en/stable",
                    "start_urls": [
                        "https://docs.djangoproject.com/en/stable/intro/tutorial01/",
                        "https://docs.djangoproject.com/en/stable/topics/db/models/"
                    ],
                    "selectors": {
                        "content": "article",  # ✅ Seletor que funciona - encontrou conteúdo
                        "links": "a.reference.internal"  # ✅ Seletor que funciona - encontrou 25 links
                    },
                    "valid_paths": ["/intro/", "/topics/", "/ref/", "/howto/"],
                    "max_depth": 2
                },
                "vue": {
                    "base_url": "https://vuejs.org/guide/",
                    "start_urls": [
                        "https://vuejs.org/guide/introduction.html",
                        "https://vuejs.org/guide/essentials/application.html"
                    ],
                    "selectors": {
                        "content": ".content, main, .theme-default-content",
                        "links": ".sidebar a, .toc a"
                    },
                    "valid_paths": ["/guide/", "/api/"],
                    "max_depth": 2
                },
                "express": {
                    "base_url": "https://expressjs.com/",
                    "start_urls": [
                        "https://expressjs.com/en/starter/installing.html",
                        "https://expressjs.com/en/guide/routing.html"
                    ],
                    "selectors": {
                        "content": ".content, main, .doc",
                        "links": ".sidebar a, nav a"
                    },
                    "valid_paths": ["/en/", "/guide/"],
                    "max_depth": 2
                },
                "flask": {
                    "base_url": "https://flask.palletsprojects.com/",
                    "start_urls": [
                        "https://flask.palletsprojects.com/en/stable/quickstart/",
                        "https://flask.palletsprojects.com/en/stable/tutorial/"
                    ],
                    "selectors": {
                        "content": ".body, .section, main",
                        "links": ".sidebar a, .toctree a"
                    },
                    "valid_paths": ["/quickstart/", "/tutorial/", "/patterns/"],
                    "max_depth": 2
                }
            },

            "devops_cloud": {
                "docker": {
                    "base_url": "https://docs.docker.com/",
                    "start_urls": [
                        "https://docs.docker.com/get-started/",
                        "https://docs.docker.com/engine/",
                        "https://docs.docker.com/compose/"
                    ],
                    "selectors": {
                        "content": ".content, .docArticle, main, article, .docs-content",
                        "links": ".docs-sidebar a, .sidebar a, nav a[href*='/get-started/'], nav a[href*='/engine/'], nav a[href*='/compose/']"
                    },
                    "valid_paths": ["/get-started/", "/engine/", "/compose/", "/reference/"],
                    "max_depth": 2
                },
                "aws": {
                    "base_url": "https://docs.aws.amazon.com",
                    "start_urls": [
                        "https://docs.aws.amazon.com/lambda/latest/dg/welcome.html",
                        "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html",
                        "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html"
                    ],
                    "selectors": {
                        "content": "#main-col-body, .section, .chapter, main, .awsui-documentation",
                        "links": ".table-of-contents a, .nav-item a, .toc a, .awsui-toc a"
                    },
                    "valid_paths": ["/lambda/", "/s3/", "/ec2/", "/userguide/", "/dg/", "/UserGuide/"],
                    "max_depth": 1
                },
                "kubernetes": {
                    "base_url": "https://kubernetes.io/docs/",
                    "start_urls": [
                        "https://kubernetes.io/docs/concepts/",
                        "https://kubernetes.io/docs/tutorials/"
                    ],
                    "selectors": {
                        "content": ".content, .docs-content, main",
                        "links": ".docs-sidebar a, nav a[href*='/docs/']"
                    },
                    "valid_paths": ["/concepts/", "/tutorials/", "/tasks/"],
                    "max_depth": 2
                },
                "terraform": {
                    "base_url": "https://developer.hashicorp.com/terraform/docs",
                    "start_urls": [
                        "https://developer.hashicorp.com/terraform/intro",
                        "https://developer.hashicorp.com/terraform/language"
                    ],
                    "selectors": {
                        "content": ".docs-page, main, .content",
                        "links": ".sidebar a, .docs-sidebar a"
                    },
                    "valid_paths": ["/intro/", "/language/", "/cli/"],
                    "max_depth": 2
                },
                "gcp": {
                    "base_url": "https://cloud.google.com/docs",
                    "start_urls": [
                        "https://cloud.google.com/compute/docs",
                        "https://cloud.google.com/storage/docs"
                    ],
                    "selectors": {
                        "content": ".devsite-article, main, .content",
                        "links": ".devsite-nav a, .sidebar a"
                    },
                    "valid_paths": ["/compute/", "/storage/", "/functions/"],
                    "max_depth": 1
                }
            },

            "tools_platforms": {
                "git": {
                    "base_url": "https://git-scm.com/docs/",
                    "start_urls": ["https://git-scm.com/docs/gittutorial"],
                    "selectors": {
                        "content": "#main",
                        "links": ".sidebar a"
                    }
                },
                "github": {
                    "base_url": "https://docs.github.com/en",
                    "start_urls": [
                        "https://docs.github.com/en/get-started/quickstart/hello-world",
                        "https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests",
                        "https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository"
                    ],
                    "selectors": {
                        "content": ".container-lg, main, article, #main-content, .markdown-body",
                        "links": ".sidebar a, nav[aria-label='Main'] a, .SideNav a, a[href^='/en/']"
                    },
                    "valid_paths": ["/get-started/", "/pull-requests/", "/repositories/", "/issues/"],
                    "max_depth": 2
                },
                "vscode": {
                    "base_url": "https://code.visualstudio.com/docs",
                    "start_urls": [
                        "https://code.visualstudio.com/docs/getstarted/introvideos",
                        "https://code.visualstudio.com/docs/editor/codebasics"
                    ],
                    "selectors": {
                        "content": ".content, main, .body",
                        "links": ".sidebar a, .nav a"
                    },
                    "valid_paths": ["/getstarted/", "/editor/", "/languages/"],
                    "max_depth": 2
                },
                "postman": {
                    "base_url": "https://learning.postman.com/docs/",
                    "start_urls": [
                        "https://learning.postman.com/docs/getting-started/introduction/",
                        "https://learning.postman.com/docs/sending-requests/requests/"
                    ],
                    "selectors": {
                        "content": ".content, main, .docs-content",
                        "links": ".sidebar a, .nav-docs a"
                    },
                    "valid_paths": ["/getting-started/", "/sending-requests/"],
                    "max_depth": 2
                },
                "npm": {
                    "base_url": "https://docs.npmjs.com/",
                    "start_urls": [
                        "https://docs.npmjs.com/about-npm",
                        "https://docs.npmjs.com/creating-a-package-json-file"
                    ],
                    "selectors": {
                        "content": ".content, main, .documentation",
                        "links": ".sidebar a, nav a"
                    },
                    "valid_paths": ["/about-", "/creating-", "/configuring-"],
                    "max_depth": 2
                }
            },
            "database_technologies": {
                "mongodb": {
                    "base_url": "https://www.mongodb.com/docs/",
                    "start_urls": [
                        "https://www.mongodb.com/docs/manual/introduction/",
                        "https://www.mongodb.com/docs/manual/crud/"
                    ],
                    "selectors": {
                        "content": ".content, main, .docs-body",
                        "links": ".sidebar a, .nav a"
                    },
                    "valid_paths": ["/manual/", "/drivers/"],
                    "max_depth": 2
                },
                "postgresql": {
                    "base_url": "https://www.postgresql.org/docs/",
                    "start_urls": [
                        "https://www.postgresql.org/docs/current/tutorial-start.html",
                        "https://www.postgresql.org/docs/current/sql.html"
                    ],
                    "selectors": {
                        "content": "#docContent, .content, main",
                        "links": ".sidebar a, .NAVITEM a"
                    },
                    "valid_paths": ["/tutorial-", "/sql-"],
                    "max_depth": 2
                }
            }
        }

        self.technical_sources2 = {
            "programming_languages": {
                "python": {
                    "base_url": "https://docs.python.org/3/",
                    "start_urls": [
                        "https://docs.python.org/3/tutorial/index.html",
                        "https://docs.python.org/3/library/index.html",
                        "https://docs.python.org/3/howto/index.html"
                    ],
                    "selectors": {
                        "content": ".body",
                        "links": ".sphinxsidebar a.reference",  # Seletor mais específico
                        "pagination": None
                    },
                    "valid_paths": ["/tutorial/", "/library/", "/howto/", "/reference/"]
                }
            }
        }

    def fetch_technical_docs(self) -> List[Dict]:
        """
        Coordena a coleta de documentação técnica de múltiplas fontes
        """
        all_documents = []

        for category, sources in self.technical_sources.items():
            print(f"📂 Coletando documentos da categoria: {category}")

            for tech_name, source_config in sources.items():
                print(f"  🔍 Processando: {tech_name}")

                try:
                    documents = self._process_technical_source(
                        tech_name,
                        source_config,
                        category
                    )
                    all_documents.extend(documents)

                    print(f"  ✅ {tech_name}: {len(documents)} documentos coletados")
                    time.sleep(self.delay)

                except Exception as e:
                    print(f"  ❌ Erro em {tech_name}: {str(e)}")
                    continue

        return all_documents

    def debug_django_structure(self):
        """
        Método para investigar a estrutura real do site docs.djangoproject.com
        """
        from urllib.parse import urljoin
        test_url = "https://docs.djangoproject.com/en/stable/intro/tutorial01/"

        try:
            response = self.session.get(test_url, timeout=10)
            print(f"📡 Status Code: {response.status_code}")

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # 1. Analisar possíveis seletores de CONTEÚDO
                print("\n🔎 Analisando seletores de CONTEÚDO:")
                content_selectors = ["main", "article", ".section", "div.section", "div.body", "div.document"]
                for selector in content_selectors:
                    elements = soup.select(selector)
                    print(f"   Seletor '{selector}': {len(elements)} elemento(s) encontrado(s)")
                    if elements:
                        text_preview = elements[0].get_text(strip=True)[:150]
                        print(f"      Prévia: '{text_preview}...'")

                # 2. Analisar possíveis seletores de LINKS
                print("\n🔎 Analisando seletores de LINKS:")
                link_selectors = ["a.reference.internal", "li.toctree-l1 a", ".sphinxsidebar a", "nav a", ".sidebar a"]
                for selector in link_selectors:
                    elements = soup.select(selector)
                    print(f"   Seletor '{selector}': {len(elements)} link(s) encontrado(s)")
                    if elements:
                        for i, link in enumerate(elements[:3]):
                            href = link.get('href', '')
                            full_url = urljoin(test_url, href)
                            print(f"      Exemplo {i + 1}: {full_url}")
                            print(f"         Texto: {link.get_text(strip=True)}")

        except Exception as e:
            print(f"❌ Erro durante o debug: {e}")

    def _process_technical_source(self, tech_name: str, source_config: Dict, category: str) -> List[Dict]:
        """
        Processa uma fonte técnica específica
        """
        documents = []
        visited_urls = set()

        for start_url in source_config["start_urls"]:
            try:
                # Coleta páginas recursivamente
                new_docs = self._crawl_technical_pages(
                    start_url,
                    source_config,
                    tech_name,
                    category,
                    visited_urls,
                    depth=0,
                    max_depth=3
                )
                documents.extend(new_docs)

                # Limite de páginas por fonte
                if len(documents) >= self.max_pages:
                    documents = documents[:self.max_pages]
                    break

            except Exception as e:
                print(f"    ⚠️  Erro na URL {start_url}: {str(e)}")
                continue

        return documents

    def _crawl_technical_pages(self, url: str, source_config: Dict, tech_name: str,
                               category: str, visited_urls: set, depth: int, max_depth: int) -> List[Dict]:
        """
        Crawl recursivo em páginas técnicas
        """
        if (depth > max_depth or url in visited_urls or
                not self._is_valid_technical_url(url, source_config["base_url"])):
            return []

        visited_urls.add(url)
        documents = []

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extrai o conteúdo principal da página
            content_element = soup.select_one(source_config["selectors"]["content"])
            if content_element:
                document = self._extract_technical_content(
                    content_element, url, tech_name, category
                )
                if document:
                    documents.append(document)

            # Encontra e segue links para páginas relacionadas
            if depth < max_depth:
                links = soup.select(source_config["selectors"]["links"])
                for link in links[:10]:  # Limita para não explodir
                    href = link.get('href')
                    if href:
                        full_url = urljoin(source_config["base_url"], href)
                        if full_url not in visited_urls:
                            time.sleep(self.delay * 0.5)  # Delay menor entre subpáginas

                            sub_documents = self._crawl_technical_pages(
                                full_url, source_config, tech_name, category,
                                visited_urls, depth + 1, max_depth
                            )
                            documents.extend(sub_documents)

        except Exception as e:
            print(f"      Erro no crawl de {url}: {str(e)}")

        return documents

    def _extract_technical_content(self, content_element, url: str, tech_name: str, category: str) -> Optional[Dict]:
        """
        Extrai e estrutura o conteúdo técnico de uma página
        """
        try:
            # Remove elementos indesejados
            for element in content_element.select('script, style, nav, header, footer'):
                element.decompose()

            # Extrai título
            title = self._extract_title(content_element)
            if not title:
                return None

            # Extrai texto limpo
            text_content = self._clean_text_content(content_element)
            if len(text_content) < 200:  # Ignora conteúdo muito curto
                return None

            # Determina contexto profissional e nível de inglês
            professional_context = self._determine_professional_context(text_content, tech_name)
            english_level = self._estimate_english_level(text_content)

            return {
                "metadata": DocumentMetadata(
                    title=title,
                    url=url,
                    technology=tech_name,
                    category=category,
                    english_level=english_level,
                    professional_context=professional_context,
                    content_type="technical_documentation",
                    last_updated=str(time.time())
                ),
                "content": text_content,
                "raw_html": str(content_element),
                "word_count": len(text_content.split()),
                "key_terms": self._extract_key_terms(text_content)
            }

        except Exception as e:
            print(f"      Erro na extração de conteúdo: {str(e)}")
            return None

    def _extract_title(self, soup) -> str:
        """Extrai título da página"""
        title_selectors = ['h1', '.page-title', 'title']
        for selector in title_selectors:
            element = soup.select_one(selector) if selector != 'title' else soup.find('title')
            if element and element.get_text().strip():
                return element.get_text().strip()
        return "Untitled"

    def _clean_text_content(self, soup) -> str:
        """Limpa e extrai texto do conteúdo"""
        # Remove código muito extenso (mantém explicações)
        for code_block in soup.select('pre, code'):
            if len(code_block.get_text()) > 100:
                code_block.decompose()

        text = soup.get_text(separator='\n', strip=True)

        # Limpeza do texto
        lines = []
        for line in text.splitlines():
            line = line.strip()
            if (line and
                    not line.startswith('//') and
                    len(line) > 10 and  # Ignora linhas muito curtas
                    not line.isupper()):  # Ignora headers em uppercase
                lines.append(line)

        return '\n'.join(lines)

    def _determine_professional_context(self, text: str, technology: str) -> str:
        """Determina o contexto profissional baseado no conteúdo"""
        text_lower = text.lower()

        context_keywords = {
            "development": ["function", "method", "class", "variable", "import"],
            "debugging": ["error", "debug", "fix", "issue", "problem"],
            "deployment": ["deploy", "server", "production", "environment", "config"],
            "collaboration": ["team", "collaborate", "review", "merge", "branch"],
            "architecture": ["architecture", "design", "pattern", "structure", "model"]
        }

        scores = {context: 0 for context in context_keywords}

        for context, keywords in context_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[context] += 1

        return max(scores.items(), key=lambda x: x[1])[0]

    def _estimate_english_level(self, text: str) -> str:
        """Estima o nível de inglês do conteúdo"""
        words = text.lower().split()
        total_words = len(words)

        if total_words == 0:
            return "B1"

        # Listas de palavras por complexidade (simplificado)
        basic_words = {"the", "is", "and", "or", "but", "in", "on", "at", "to", "for"}
        advanced_words = {"nevertheless", "consequently", "furthermore", "notwithstanding"}

        basic_count = sum(1 for word in words if word in basic_words)
        advanced_count = sum(1 for word in words if word in advanced_words)

        advanced_ratio = advanced_count / total_words

        if advanced_ratio > 0.05:
            return "C1"
        elif advanced_ratio > 0.02:
            return "B2"
        else:
            return "B1"

    def _extract_key_terms(self, text: str) -> List[str]:
        """Extrai termos técnicos importantes"""
        # Termos comuns em documentação técnica
        technical_terms = {
            "function", "method", "class", "object", "variable", "parameter",
            "return", "import", "export", "interface", "implementation",
            "configuration", "deployment", "database", "api", "endpoint",
            "authentication", "authorization", "middleware", "framework"
        }

        words = set(text.lower().split())
        found_terms = list(words.intersection(technical_terms))

        return found_terms[:10]  # Retorna no máximo 10 termos

    def _is_valid_technical_url(self, url: str, base_url: str) -> bool:
        """Valida se a URL é apropriada para coleta técnica"""
        parsed_url = urlparse(url)
        parsed_base = urlparse(base_url)

        # Verifica se está no mesmo domínio
        if parsed_url.netloc != parsed_base.netloc:
            return False

        # Verifica extensões de arquivo não desejadas
        invalid_extensions = {'.pdf', '.zip', '.jpg', '.png', '.gif', '.exe'}
        path = parsed_url.path.lower()
        if any(path.endswith(ext) for ext in invalid_extensions):
            return False

        return True

    def save_documents(self, documents: List[Dict], output_dir: str = "technical_docs"):
        """Salva os documentos coletados"""
        BASE_PATH = Path(__file__).resolve().parents[2]
        OUTPUT_PATH = os.path.join(BASE_PATH,'output',output_dir)
        Path(OUTPUT_PATH).mkdir(exist_ok=True)

        for i, doc in enumerate(documents):
            filename = f"{doc['metadata'].technology}_{i}.json"
            filepath = Path(OUTPUT_PATH) / filename

            # Converte para dict serializável
            doc_dict = {
                "metadata": {
                    "title": doc["metadata"].title,
                    "url": doc["metadata"].url,
                    "technology": doc["metadata"].technology,
                    "category": doc["metadata"].category,
                    "english_level": doc["metadata"].english_level,
                    "professional_context": doc["metadata"].professional_context,
                    "content_type": doc["metadata"].content_type,
                    "last_updated": doc["metadata"].last_updated
                },
                "content": doc["content"],
                "word_count": doc["word_count"],
                "key_terms": doc["key_terms"]
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(doc_dict, f, indent=2, ensure_ascii=False)
