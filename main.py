from fastapi import FastAPI
from database.conn import Connection
from app.router.routes import api
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = Connection(app)
    # Start the database connection
    await conn.startup_db_client()
    yield
    # Close the database connection
    await conn.shutdown_db_client()

app = FastAPI(lifespan=lifespan, swagger_ui_parameters={"syntaxHighlight": {"theme": "obsidian"}})

@app.get("/")
async def root():
    return {"message": "Welcome to English Pro Tech"}

app.include_router(api, prefix="/api")



