from fastapi import FastAPI

from app.service.auth_service import AuthMiddleware
from database.conn import Connection
from resource.rag_system.data_ingestion import DataIngestion
from app.router.routes import api
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = Connection(app)
    data_ingestion = DataIngestion()
    # Start the database connection
    await conn.startup_db_client()
    yield
    # Close the database connection
    await conn.shutdown_db_client()

app = FastAPI(
    title="EnglishProTech API",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}}
)
app.add_middleware(AuthMiddleware)

app.include_router(api, prefix="/api")



