"""
PartSelect AI Agent - Main Application Entry Point
"""
import os
from dotenv import load_dotenv
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

# Load environment variables from .env file
load_dotenv()
KEY = 'OPENROUTER_API_KEY'

# Create FastAPI application
app = FastAPI(
    title="PartSelect AI Agent API",
    description="AI-powered assistant for appliance parts",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes with /api prefix
app.include_router(router, prefix="/api", tags=["chat"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "PartSelect AI Agent API",
        "status": "running",
        "docs_url": "/docs",
        "chat_endpoint": "/api/chat"
    }

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)