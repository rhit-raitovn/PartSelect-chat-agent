"""
API Routes
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.models.schemas import ChatRequest, ChatResponse
from app.agent.core import get_agent
from datetime import datetime
import traceback

# Create FastAPI app
app = FastAPI(
    title="PartSelect AI Agent API",
    description="AI-powered customer service agent for refrigerator and dishwasher parts",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "PartSelect AI Agent",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "operational",
            "agent": "operational",
            "vector_db": "operational"
        }
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    
    Process user message and return agent response
    """
    try:
        agent = get_agent()
        
        # Process message
        response = await agent.process_message(
            message=request.message,
            conversation_id=request.conversation_id,
            user_context=request.user_context
        )
        
        return ChatResponse(
            response=response,
            success=True
        )
    
    except Exception as e:
        # Log error
        print(f"Error processing chat: {str(e)}")
        print(traceback.format_exc())
        
        return ChatResponse(
            response=None,
            success=False,
            error=f"An error occurred processing your request: {str(e)}"
        )


@app.post("/api/conversation/clear")
async def clear_conversation(conversation_id: str):
    """Clear conversation history"""
    try:
        agent = get_agent()
        agent.clear_conversation(conversation_id)
        return {"success": True, "message": "Conversation cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history"""
    try:
        agent = get_agent()
        history = agent.get_conversation_history(conversation_id)
        return {
            "conversation_id": conversation_id,
            "messages": [msg.dict() for msg in history]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)