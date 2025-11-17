# backend/app/api/routes.py
# Updated chat endpoint to return suggested actions

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os

from app.agent.core import PartSelectAgent, format_agent_response

router = APIRouter()

# Load products and initialize agent
def load_products():
    products_file = os.path.join(os.path.dirname(__file__), '../../data/products.json')
    with open(products_file, 'r') as f:
        return json.load(f)

products_data = load_products()
agent = PartSelectAgent(products_data)

class ChatRequest(BaseModel):
    message: str
    user_id: str = "anonymous"

class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    response_type: Optional[str] = None
    suggested_actions: Optional[List[str]] = []  # ← Add this field

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint that processes user messages
    """
    try:
        # Process message through agent
        agent_response = agent.process_message(request.message)
        
        # Format response
        formatted_response = format_agent_response(agent_response)
        
        # Return with suggested actions
        return ChatResponse(
            response=formatted_response,
            intent=agent_response.get("intent"),
            response_type=agent_response.get("response_type"),
            suggested_actions=agent_response.get("suggested_actions", [])  # ← Include suggested actions
        )
    
    except Exception as e:
        print(f"❌ Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    return {"status": "healthy", "products": len(agent.products)}