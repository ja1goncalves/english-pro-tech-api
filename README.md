# English Pro Tech API

Backend service for English Pro Tech — a FastAPI-based API that helps users practice and improve technical English through role‑play challenges and AI‑generated feedback enhanced by a lightweight RAG (Retrieval Augmented Generation) pipeline.

This README documents: stack, tools, setup, configuration, how to run locally, architecture (API/services/RAG), responsibilities of folders and key classes, and how NLP, agents, and RAG are used.


## Overview
- Framework: FastAPI (ASGI)
- Language: Python 3.11+
- Package manager: pip (requirements.txt)
- Web server: uvicorn
- Database: MongoDB (async client via pymongo AsyncMongoClient)
- Auth: JWT Bearer tokens
- Config: pydantic-settings + python-dotenv (.env)
- Gen AI integration: external HTTP API (model + base URL) via a thin agent wrapper
- RAG: TF‑IDF vectorization (scikit‑learn) + cosine similarity over document chunks; optional ChromaDB persistence example

All API routes are mounted under /api. Interactive docs at /docs when running locally.


## What’s inside: tools and resources used
- FastAPI/starlette: web API framework and ASGI underpinnings
- pydantic 2 + pydantic-settings: DTOs and configuration
- PyJWT + bcrypt: authentication and password hashing
- pymongo (AsyncMongoClient): database access to MongoDB
- requests: HTTP calls to the external Gen AI provider
- scikit-learn: NLP TF‑IDF embeddings and cosine similarity search
- beautifulsoup4: HTML parsing for technical docs scraping
- chromadb: example persistent vector store setup (not required at runtime)
- python-dotenv: load .env environment variables
- uvicorn: development server

Optional/external services
- MongoDB server (local or remote)
- Gen AI model server (e.g., Ollama) accessible via GEN_AI_URL
- GitHub API (optional token for higher rate limits)


## Prerequisites
- Python 3.11+
- pip
- MongoDB running and reachable
- Internet access for initial RAG ingestion (technical docs and GitHub; optional but enabled by default at startup)
- Optional: a local LLM service (e.g., Ollama) if you want on‑device generation


## Local installation and first run
1) Clone and enter the project directory
   - cd english-pro-tech-api

2) Create and activate a virtual environment
   - python -m venv .venv
   - macOS/Linux: source .venv/bin/activate
   - Windows (PowerShell): .venv\Scripts\Activate.ps1

3) Install dependencies
   - pip install -r requirements.txt

4) Start MongoDB
   - Ensure you have a MongoDB instance running. If local: mongodb://localhost:27017

5) Configure your .env (see template below)
   - touch .env and fill in values

6) (Optional) Start a local Gen AI model server
   - Example with Ollama:
     - Install: https://ollama.com
     - Pull model: ollama pull llama3
     - Set GEN_AI_URL to your chat/completions endpoint (e.g., http://localhost:11434/api/chat) and GEN_AI_MODEL=llama3
     - Note: default in code is http://localhost:11434/api — adjust if your provider uses a different path.

7) Run the API
   - uvicorn main:app --reload
   - http://127.0.0.1:8000/docs for Swagger UI

On first startup the app will:
- Create required collections
- Seed role plays (from database/role_play.json)
- Ensure an admin user exists (username: admin, password from ADMIN_PASSWORD)
- Trigger an initial RAG data population (fetch technical docs and GitHub content), which may take several minutes and requires internet. Provide GITHUB_TOKEN to avoid API rate limits.


## Environment variables
Managed via app/util/config.py and python-dotenv. Defaults come from code; override via .env.

- SECRET_KEY: secret used to sign JWTs. Default: your_secret_key
- ENCODE_ALGORITHM: JWT algorithm. Default: HS256
- TOKEN_TTL: access token lifetime in minutes. Default: 30
- DB_URI: MongoDB connection string (e.g., mongodb://localhost:27017)
- DB_NAME: database name. Default: ept_db
- ADMIN_PASSWORD: initial admin password. Default: admin123
- FILE_UPLOAD_DIR: uploads directory. Default: ./files
- GEN_AI_MODEL: model identifier (e.g., llama3)
- GEN_AI_URL: base URL or chat endpoint for your Gen AI server. Default: http://localhost:11434/api (you may need /api/chat depending on your provider)
- GITHUB_TOKEN: optional personal access token to increase GitHub rate limits

Notes and caveats
- The code imports AsyncMongoClient from pymongo; in many environments the recommended async driver is motor. This project assumes a compatible environment for AsyncMongoClient. If you face issues, consider switching to motor.
- The default DB_URI in code was initially set to a PostgreSQL‑looking example; ensure you set a proper MongoDB URI in .env.
- The password reset endpoints don’t send email; they expose API flows only.
- The Gen AI client expects a chat‑style endpoint that returns streamed or chunked JSON lines; adjust GEN_AI_URL to your provider.


## How the system works (architecture)
High‑level layers
- Entry point (main.py): configures FastAPI, DB lifecycle, and middleware; includes /api routers.
- Controllers (app/controller): HTTP endpoints for auth, user, admin, and role‑play.
- Services (app/service): business logic for authentication, users, role‑plays, Gen AI integration, and RAG refresh/storage.
- Models/DTOs (app/model): request/response contracts and types.
- Utilities (app/util): configuration, JWT/password helpers, text utilities.
- Database (database/*): connection management and initial seeding.
- RAG system (resource/rag_system): ingestion, processing, vectorization, and lightweight retrieval.
- Agent client (resource/agent_ai): thin HTTP client for external LLMs.

RAG/NLP pipeline overview
1) Data ingestion (resource/rag_system/data_ingestion.py)
   - TechnicalDocsFetcher scrapes technical documentation defined in resource/rag_system/technical_sources.json using requests + BeautifulSoup.
   - GitHubDataFetcher pulls content from selected public repositories via the GitHub API (optional GITHUB_TOKEN to raise rate limits).
2) Processing and chunking (resource/rag_system/rag_data_processor.py)
   - Cleans text, tokenizes, and produces task‑aware chunks with metadata (technology, professional_context, english_level, etc.).
   - Specialized chunkers for markdown, code, forums, and generic content.
   - Output: ProcessedChunk dataclass instances with content, metadata, chunk_id, and optional embedding field.
3) Vectorization and storage
   - In‑memory SimpleVectorStore builds TF‑IDF vectors via scikit‑learn and uses cosine_similarity for search.
   - An example persistent store using ChromaDB exists (RAGVectorStore), but the live query path uses the in‑memory TF‑IDF store by default.
4) Retrieval and query (resource/rag_system/tech_english_rag_system.py)
   - TechEnglishRAGSystem orchestrates setup and query_rag(), applying optional context filters (e.g., professional context = "development").
5) Use in generation (app/service/gen_ia_service.py)
   - GenIAService.get_context_rag() fetches top‑N relevant chunks and formats them into a concise context string used to prime the generator.
   - Prompts (init_play and answer_play) combine user/task metadata, prior chat story, and retrieved context to produce targeted feedback and XP scoring.

AI agent integration
- resource/agent_ai/gen_ai_api.py is a minimal agent wrapper around an external chat completion provider (e.g., Ollama). It:
  - Reads model and URL from GEN_AI_MODEL/GEN_AI_URL
  - Sends a system message and the user prompt
  - Streams/aggregates response content into a single string
  - Returns text to the service layer

NLP details
- Embeddings: TF‑IDF vectors built with scikit‑learn’s TfidfVectorizer (max_features=1000, English stop‑words)
- Similarity: cosine_similarity between query vector and chunk vectors
- Filtering: optional filtering by professional_context during search
- This provides fast, local, dependency‑light retrieval without requiring external embedding services


## Project structure and responsibilities
- main.py — FastAPI app, lifecycle (connect/disconnect DB), middleware, router mounting
- app/
  - controller/
    - auth_controller.py — token, logout, password reset flows
    - user_controller.py — registration, profile update, me
    - admin_controller.py — user/role‑play management and RAG refresh endpoint
    - role_play_controller.py — list available role‑plays and submit answers for feedback/XP
  - service/
    - auth_service.py — login/logout/token logic and middleware (AuthMiddleware)
    - user_service.py — CRUD and password changes
    - role_play_service.py — role/level/play CRUD and selection
    - gen_ia_service.py — RAG retrieval + Gen AI prompts for initial/feedback conversations
    - rag_doc_service.py — runs ingestion + processing and persists docs/chunks into MongoDB
    - rag_chuck_service.py — persistence access to stored chunks
    - service.py — base service abstraction
  - model/
    - dto.py, entity.py, type.py — DTOs, entities, and enums used across controllers/services
  - util/
    - config.py — Settings (env), OPEN_ROUTES allow‑list
    - security.py — JWT/password hashing helpers
    - chunk.py — helpers to pretty‑print retrieved context chunks
    - role_play.py — helpers to format play codes and histories
- database/
  - conn.py — Async MongoDB connection, collection init, and initial seeding (roles, admin, RAG)
  - role_play.json — seed roles/levels/plays
  - collections.py — collection names (Table enum)
- resource/
  - agent_ai/gen_ai_api.py — external LLM client wrapper
  - rag_system/
    - data_ingestion.py — orchestrates fetching and processing; example RAG pipeline
    - technical_docs_fetcher.py — scraping technical docs from curated sources
    - github_data_fetcher.py — GitHub API collector for selected repos
    - rag_data_processor.py — text cleaning and intelligent chunking
    - simple_vector_store.py — TF‑IDF + cosine retrieval in memory
    - rag_vectors_store.py — example persistent vector DB (ChromaDB)
    - tech_english_rag_system.py — orchestrator to setup/search
    - data_class/ — dataclasses like ProcessedChunk and metadata types
- tests/
  - test_main.http — sample HTTP requests for manual testing


## Runbook: useful commands
- Development server: uvicorn main:app --reload
- Production example: uvicorn main:app --host 0.0.0.0 --port 8000
- Trigger RAG refresh manually (admin only): PUT /api/v1/admin/rag/refresh


## API overview (selected)
Base path: /api

- Auth (/v1/auth)
  - POST /api/v1/auth/token — username/password login (OAuth2PasswordRequestForm)
  - DELETE /api/v1/auth — logout
  - POST /api/v1/auth/reset-password — request reset
  - PUT /api/v1/auth/reset-password?token=... — complete reset
- User (/v1/user)
  - POST /api/v1/user/register — create user (public)
  - PUT /api/v1/user/ — update current user
  - GET /api/v1/user/me — current user
- Admin (/v1/admin)
  - /user — manage users
  - /role-play — manage role‑plays
  - /rag/refresh — refresh RAG data
- Role Play (/v1/role-play)
  - GET /api/v1/role-play/ — available role‑plays
  - POST /api/v1/role-play/ — submit and get AI feedback + XP

Authentication
- Authorization: Bearer <token>
- Obtain token via POST /api/v1/auth/token


## Tests
Use tests/test_main.http with JetBrains HTTP Client or VS Code REST Client.

Examples
- Health: curl -s http://127.0.0.1:8000/
- Docs:   open http://127.0.0.1:8000/docs


## Notes & caveats
- Async MongoDB: if AsyncMongoClient is unsupported in your environment, consider motor (Motor client) and adjust imports accordingly.
- Defaults: set DB_URI to a real MongoDB URI. The code default is a placeholder.
- RAG ingestion: initial population can take time and network; provide GITHUB_TOKEN to reduce rate limiting.
- Gen AI server: GEN_AI_URL may need to point to your provider’s chat endpoint (e.g., Ollama /api/chat). Adjust as needed.


## Licensing
TODO: Add a LICENSE file and state the chosen license (e.g., MIT, Apache‑2.0).
