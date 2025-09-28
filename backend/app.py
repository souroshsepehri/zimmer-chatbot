from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.db import engine, Base
from routers import chat, faqs, logs
from core.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Persian Chatbot API",
    description="A Persian chatbot with FAQ management and semantic search",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://persian-chatbot-frontend.onrender.com",  # Render frontend
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


@app.get("/")
async def root():
    return {"message": "Persian Chatbot API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
