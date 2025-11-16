"""
PartSelect AI Agent - Main Application Entry Point
"""
import os
from dotenv import load_dotenv
import uvicorn
from app.api.routes import app

# Load environment variables from .env file
load_dotenv()
KEY = 'OPENROUTER_API_KEY'

# Verify API key is loaded
if not os.getenv(KEY):
    print("=" * 60)
    print(f"ERROR: {KEY} not found!")
    print("=" * 60)
    exit(1)

print("=" * 60)
print("✓ Environment variables loaded successfully")
print("✓ DeepSeek API key found")
print("=" * 60)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )