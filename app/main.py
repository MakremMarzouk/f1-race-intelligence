from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="F1 Race Intelligence Automation",
    version="0.1.0",
)

app.include_router(router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "f1-race-intelligence",
    }