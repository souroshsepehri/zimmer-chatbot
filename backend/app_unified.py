from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from core.db import engine, Base
from routers import chat, faqs, logs
from core.config import settings
import os
from pathlib import Path

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Persian Chatbot - Unified",
    description="A Persian chatbot with integrated frontend and backend",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://persian-chatbot-unified.onrender.com",  # Render unified
        "https://*.onrender.com",  # Any Render subdomain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(faqs.router, prefix="/api", tags=["faqs"])
app.include_router(logs.router, prefix="/api", tags=["logs"])

# Mount static files (frontend) if they exist
frontend_out = Path("../frontend/out")
if frontend_out.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_out)), name="static")
    print("✅ Frontend static files mounted")

@app.get("/")
async def root():
    """Serve the frontend or show API message"""
    index_file = frontend_out / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        return {
            "message": "Persian Chatbot API is running", 
            "frontend": "Not available - build frontend first",
            "api_docs": "/docs"
        }

@app.get("/{path:path}")
async def serve_frontend_routes(path: str):
    """Serve frontend routes for SPA"""
    # If it's an API route, let the backend handle it
    if path.startswith("api/"):
        return {"error": "API route not found"}
    
    # Try to serve frontend file
    frontend_file = frontend_out / path
    if frontend_file.exists() and frontend_file.is_file():
        return FileResponse(str(frontend_file))
    
    # For SPA routing, serve index.html
    index_file = frontend_out / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    
    return {"error": "Not found", "path": path}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "frontend": frontend_out.exists()}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
