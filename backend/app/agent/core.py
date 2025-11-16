"""
Core Agent Logic - Main orchestration for handling user queries
"""
import json
import uuid
from typing import List, Dict, Any
from app.models.schemas import (
    ChatMessage,
    AgentResponse,
    Product,
    Intent,
    IntentType,
    MessageRole
)
from app.services.deepseek import get_deepseek_service
from app.agent.intent import get_intent_classifier
from app.agent.tools import get_agent_tools


class PartSelectAgent:
    """Main agent for handling user queries about refrigerator and dishwasher parts"""
    
    def __init__(self):
        self.deepseek = get_deepseek_service()
        self.intent_classifier = get_intent_classifier()
        self.tools = get_agent_tools()
        self.conversations = {}  # In-memory conversation storage
        
        self.system_prompt = """You are a helpful customer service agent for PartSelect, an e-commerce website specializing in refrigerator and dishwasher parts.

Your responsibilities:
1. Help customers find the right parts for their appliances
2. Provide installation instructions and troubleshooting guidance
3. Check part compatibility with specific appliance models
4. Answer questions about products, pricing, and ordering

Important guidelines:
- ONLY discuss refrigerator and dishwasher parts. Politely decline questions about other appliances or unrelated topics.
- Be concise but informative. Use numbered lists (1., 2., 3.) for sequential steps.
- Use bullet points (starting with -) for non-sequential items.
- Always verify part numbers and model numbers when provided.
- If you need to use tools, use them to provide accurate information.
- When showing products, mention the part number, name, and price.
- For installation questions, provide step-by-step guidance or link to video guides.
- For compatibility questions, always verify using the check_compatibility tool.
- Be friendly and professional. If you don't have information, be honest and suggest contacting customer service.

Formatting guidelines for clean, readable responses:
- Use numbered lists (1., 2., 3.) for steps or sequential instructions
- Use bullet points (- item) for features, checks, or non-sequential items
- Use **bold** sparingly for key terms only (e.g., **part numbers**, **important warnings**)
- Keep paragraphs short (2-3 sentences max)
- Add blank lines between different sections for readability
- Don't overuse bold - only for truly important items

Format your responses with:
- Direct answers first
- Clear step-by-step instructions when needed
- Product recommendations when relevant
- Next steps or action items at the end"""
    
    async def process_message(
        self,
        message: str,
        conversation_id: str = None,
        user_context: Dict[str, Any] = None
    ) -> AgentResponse:
        """
        Process a user message and generate a response
        
        Args:
            message: User's message
            conversation_id: Optional conversation ID for context
            user_context: Optional user context (preferences, history, etc.)
            
        Returns:
            AgentResponse with message, products, and metadata
        """
        # Create or retrieve conversation
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        conversation_history = self.conversations[conversation_id]
        
        # Classify intent
        intent = await self.intent_classifier.classify(message)
        
        # Check if query is out of scope
        if intent.intent_type == IntentType.OUT_OF_SCOPE:
            return AgentResponse(
                message="I apologize, but I can only help with questions about refrigerator and dishwasher parts. Is there anything related to these appliances I can help you with?",
                products=[],
                intent=intent,
                suggested_actions=["Browse refrigerator parts", "Browse dishwasher parts"],
                conversation_id=conversation_id
            )
        
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # Prepare messages for LLM
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + conversation_history[-10:]  # Keep last 10 messages for context
        
        # Get tool definitions
        tools = self.tools.get_tool_definitions()
        
        # First LLM call - may request tool use
        response = await self.deepseek.chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            tools=tools
        )
        
        products = []
        tool_results = []
        
        # Handle tool calls if any
        if response['tool_calls']:
            for tool_call in response['tool_calls']:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Execute tool
                tool_result = await self.tools.execute_tool(
                    tool_name=function_name,
                    arguments=function_args
                )
                
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(tool_result)
                })
                
                # Extract products from tool results
                if 'product' in tool_result:
                    products.append(Product(**tool_result['product']))
                elif 'products' in tool_result:
                    for p in tool_result['products']:
                        products.append(Product(**p))
            
            # Second LLM call with tool results
            messages.append({
                "role": "assistant",
                "content": response['content'],
                "tool_calls": response['tool_calls']
            })
            messages.extend(tool_results)
            
            final_response = await self.deepseek.chat_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_message = final_response['content']
        else:
            assistant_message = response['content']
        
        # Add assistant response to history
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Update conversation storage
        self.conversations[conversation_id] = conversation_history
        
        # Generate suggested actions based on intent
        suggested_actions = self._generate_suggested_actions(intent, products)
        
        return AgentResponse(
            message=assistant_message,
            products=products[:5],  # Limit to top 5 products
            intent=intent,
            suggested_actions=suggested_actions,
            conversation_id=conversation_id
        )
    
    def _generate_suggested_actions(
        self,
        intent: Intent,
        products: List[Product]
    ) -> List[str]:
        """Generate contextual suggested actions"""
        actions = []
        
        if intent.intent_type == IntentType.PRODUCT_INFO and products:
            actions.append("View product details")
            actions.append("Check compatibility")
            actions.append("Add to cart")
        
        elif intent.intent_type == IntentType.COMPATIBILITY:
            actions.append("View compatible models")
            actions.append("Find alternative parts")
        
        elif intent.intent_type == IntentType.INSTALLATION:
            actions.append("Watch installation video")
            actions.append("Download PDF guide")
            actions.append("View required tools")
        
        elif intent.intent_type == IntentType.TROUBLESHOOTING:
            actions.append("See common solutions")
            actions.append("Order replacement part")
            actions.append("Contact support")
        
        elif intent.intent_type == IntentType.ORDER_SUPPORT:
            actions.append("Track order")
            actions.append("Contact customer service")
        
        else:
            actions.append("Browse parts catalog")
            actions.append("Talk to support")
        
        return actions
    
    def clear_conversation(self, conversation_id: str):
        """Clear a conversation history"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def get_conversation_history(
        self,
        conversation_id: str
    ) -> List[ChatMessage]:
        """Get conversation history"""
        if conversation_id in self.conversations:
            return [
                ChatMessage(
                    role=MessageRole(msg['role']),
                    content=msg['content']
                )
                for msg in self.conversations[conversation_id]
            ]
        return []


# Singleton instance
_agent = None


def get_agent() -> PartSelectAgent:
    """Get or create agent instance"""
    global _agent
    if _agent is None:
        _agent = PartSelectAgent()
    return _agent