from fastapi import FastAPI
from app.database import init_db

app = FastAPI(title="MASTER X API", version="0.1.0")

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "MASTER X"}
