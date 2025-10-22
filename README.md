# English Pro Tech API

Backend service for English Pro Tech — a FastAPI-based API that helps users practice and improve technical English through role-play challenges and AI-generated feedback.

This README documents the stack, setup, environment, how to run the server, basic endpoints, tests, and project structure. Unknown or unverified items are marked as TODO.


## Overview
- Framework: FastAPI (ASGI)
- Language: Python 3.11+ (recommended)
- Package manager: pip (requirements.txt)
- Web server for local dev: uvicorn
- Database: MongoDB (async client via pymongo)
- Auth: JWT Bearer tokens
- Config: pydantic-settings + python-dotenv (.env)
- Gen AI integration: external HTTP API configurable via env (model + base URL)

The application mounts all routes under the /api prefix and provides a root health/info endpoint at /.


## Requirements
- Python 3.11 or newer
- pip
- A running MongoDB instance
- Network access to the configured Gen AI API (defaults to a local service)

Optional but useful:
- An HTTP client (VS Code/JetBrains HTTP Client, curl, or Postman) for testing


## Quickstart (Local Development)
1) Clone the repo and change into the project directory
   - cd english-pro-tech-api

2) Create and activate a virtual environment (recommended)
   - python -m venv .venv
   - On macOS/Linux: source .venv/bin/activate
   - On Windows (PowerShell): .venv\Scripts\Activate.ps1

3) Install dependencies
   - pip install -r requirements.txt

4) Configure environment variables (see .env template below)
   - Create a .env file in the project root

5) Ensure MongoDB is running and DB_URI points to it

6) Start the API
   - uvicorn main:app --reload
   - The app will be available at http://127.0.0.1:8000
   - Interactive docs: http://127.0.0.1:8000/docs


## Environment Variables
Configuration is managed via pydantic-settings (app/util/config.py) and python-dotenv. The following variables are supported. Values shown are defaults from code where present; adjust as needed.

- SECRET_KEY: Secret key for signing JWTs. Default: "your_secret_key" (CHANGE IN PROD)
- ENCODE_ALGORITHM: JWT algorithm. Default: "HS256"
- TOKEN_TTL: Access token TTL in minutes. Default: 30
- DB_URI: MongoDB connection string. Example: "mongodb://localhost:27017" (see NOTE below)
- DB_NAME: Database name. Default: "ept_db"
- ADMIN_PASSWORD: Admin password seed. Default: "admin123" (currently not used in seeding; see NOTE)
- FILE_UPLOAD_DIR: Directory for file uploads. Default: "./files" (not currently used in routes)
- GEN_AI_MODEL: Model identifier for Gen AI API. Default: "llama3"
- GEN_AI_URL: Base URL for Gen AI API. Default: "http://localhost:11434/api"

Notes:
- IMPORTANT: Although the default DB_URI in code shows a PostgreSQL-looking example, this application uses MongoDB via an async pymongo client. Ensure DB_URI is a valid MongoDB URI (e.g., mongodb://host:port). TODO: Update the default in code to reflect MongoDB to avoid confusion.
- Seeding: On startup, the app ensures role_play and user collections exist and will seed role_play data from database/role_play.json. If the user collection is empty, it seeds an "admin" user with password derived from DB_NAME (not ADMIN_PASSWORD). TODO: Align seeding logic to use ADMIN_PASSWORD or document intended behavior.
- OPEN_ROUTES (non-env): A static allowlist in settings includes /api/v1/auth/token, /api/v1/auth/reset-password, /api/v1/user/register.

Example .env
SECRET_KEY=change_me
ENCODE_ALGORITHM=HS256
TOKEN_TTL=30
DB_URI=mongodb://localhost:27017
DB_NAME=ept_db
ADMIN_PASSWORD=admin123
FILE_UPLOAD_DIR=./files
GEN_AI_MODEL=llama3
GEN_AI_URL=http://localhost:11434/api


## Running & Scripts
There is no dedicated scripts folder; use uvicorn directly.
- Development: uvicorn main:app --reload
- Production (example): uvicorn main:app --host 0.0.0.0 --port 8000

Package installation:
- pip install -r requirements.txt

TODO:
- Provide a Makefile or scripts for common tasks (run, test, lint).
- Add a Dockerfile and docker-compose.yml (MongoDB + API) for easy local setup.


## API Overview
Base path: /api

- Root: GET /
  - Returns {"message": "Welcome to English Pro Tech"}

- Auth (prefix: /v1/auth)
  - POST /api/v1/auth/token — Login with form fields username and password (OAuth2PasswordRequestForm). Returns JWT.
  - DELETE /api/v1/auth — Logout (Bearer token required)
  - POST /api/v1/auth/reset-password — Initiate password reset (TODO: email sending is not implemented)
  - PUT /api/v1/auth/reset-password?token=... — Complete password reset with new_password and confirm_password

- User (prefix: /v1/user)
  - POST /api/v1/user/register — Create a new user (public)
  - PUT /api/v1/user/ — Update current user (Bearer token required)
  - GET /api/v1/user/me — Retrieve current user (Bearer token required)

- Admin (prefix: /v1/admin)
  - Users (prefix: /user)
    - GET /api/v1/admin/user/{key}
    - POST /api/v1/admin/user/
    - PUT /api/v1/admin/user/
    - DELETE /api/v1/admin/user/{key}
  - Role Play (prefix: /role-play)
    - GET /api/v1/admin/role-play/{key}
    - POST /api/v1/admin/role-play/
    - PUT /api/v1/admin/role-play/
    - DELETE /api/v1/admin/role-play/{key}

- Role Play (prefix: /v1/role-play)
  - GET /api/v1/role-play/ — Get role-plays available for the current user
  - POST /api/v1/role-play/ — Submit a play task and receive AI feedback and XP (Bearer token required)

Authentication
- Add header: Authorization: Bearer <token>
- Obtain token via POST /api/v1/auth/token (form fields username, password)


## Tests
A basic HTTP client test file is provided at tests/test_main.http. You can run these requests using the JetBrains IDE HTTP Client or VS Code REST Client.

Example using curl:
- Health check: curl -s http://127.0.0.1:8000/
- Docs:               http://127.0.0.1:8000/docs

TODO:
- Add unit/integration tests (pytest) and CI configuration.


## Project Structure
- main.py — FastAPI app entrypoint; sets lifespan hooks to connect/disconnect DB and mounts routers under /api.
- app/
  - controller/ — Route handlers (auth, user, admin, role_play)
  - service/ — Business logic (auth, user, role play, Gen AI client wrapper)
  - model/ — Pydantic DTOs and types
  - util/ — Settings, security helpers (JWT, password hashing), utilities
  - repository/ — Base repository abstraction
  - router/routes.py — Aggregates per-feature routers into a single APIRouter
- database/
  - conn.py — Async MongoDB connection and collection initialization + seed
  - role_play.json — Initial seed data for role-play
  - collections.py — Enum of collection names
- resource/
  - gen_ai_api.py — Thin HTTP client for the configurable Gen AI service
- tests/
  - test_main.http — Sample HTTP requests for manual testing
- requirements.txt — Python dependencies
- README.md — This documentation


## Licensing
TODO: Add a LICENSE file and state the chosen license here (e.g., MIT, Apache-2.0).


## Notes & Caveats
- Async MongoDB client: The code imports AsyncMongoClient from pymongo. Ensure the installed version supports this usage in your environment; otherwise consider switching to motor (Motor client) for async MongoDB access. TODO: Verify and, if needed, adjust the driver usage.
- Defaults in settings: Some defaults (e.g., DB_URI) appear to be placeholders not aligned with MongoDB; override via .env for correct operation.
- Password reset flow: Email sending is marked as TODO; current endpoints accept/return data but do not dispatch emails.
