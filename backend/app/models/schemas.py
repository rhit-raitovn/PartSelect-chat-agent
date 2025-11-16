"""
Pydantic models for request/response validation
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None


class Product(BaseModel):
    part_number: str
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None
    compatibility: List[str] = []
    installation_guide_url: Optional[str] = None


class IntentType(str, Enum):
    INSTALLATION = "installation"
    COMPATIBILITY = "compatibility"
    TROUBLESHOOTING = "troubleshooting"
    PRODUCT_INFO = "product_info"
    ORDER_SUPPORT = "order_support"
    GENERAL = "general"
    OUT_OF_SCOPE = "out_of_scope"


class Intent(BaseModel):
    intent_type: IntentType
    confidence: float
    entities: Dict[str, Any] = {}


class AgentResponse(BaseModel):
    message: str
    products: List[Product] = []
    intent: Optional[Intent] = None
    suggested_actions: List[str] = []
    conversation_id: str


class ChatResponse(BaseModel):
    response: AgentResponse
    success: bool = True
    error: Optional[str] = None