from fastapi import FastAPI
from app.api.routes import router
from contextlib import asynccontextmanager

from app.database.init_db import create_tables


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="F1 Race Intelligence Automation",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "f1-race-intelligence",
    }