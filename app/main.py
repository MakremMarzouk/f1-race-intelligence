from fastapi import FastAPI

app = FastAPI(
    title="F1 Race Intelligence Automation",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "f1-race-intelligence",
    }