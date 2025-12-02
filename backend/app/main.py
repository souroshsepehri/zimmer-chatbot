from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.routers import admin

app = FastAPI(title="Zimmer Chatbot Backend")

app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/health")
async def health():
    return JSONResponse(content={"status": "ok"})



















