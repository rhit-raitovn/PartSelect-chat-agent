"""
Demo Mode for DeepSeek Service - Full simulation including tool responses
"""
import os
from typing import List, Dict, Any
import random


class DemoDeepSeekService:
    """Demo service that simulates DeepSeek responses without API calls"""
    
    def __init__(self):
        self.api_key = "demo-mode"
        self.base_url = "demo-mode"
        self.model = "demo-deepseek-chat"
        self.demo_mode = True
        print("\n" + "="*60)
        print("⚠️  RUNNING IN DEMO MODE")
        print("   No API calls will be made")
        print("   All responses are simulated")
        print("="*60 + "\n")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        tools: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a simulated chat completion
        """
        # Simulate API delay
        await self._simulate_delay()
        
        # Check if this is the second call (with tool results)
        has_tool_results = any(msg.get("role") == "tool" for msg in messages)
        
        # Get the user's message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "").lower()
                break
        
        # If we have tool results, generate final response
        if has_tool_results:
            return {
                "content": self._generate_tool_response(user_message, messages),
                "tool_calls": None,
                "finish_reason": "stop",
                "usage": {
                    "prompt_tokens": 150,
                    "completion_tokens": 80,
                    "total_tokens": 230
                }
            }
        
        # First call - determine if tools should be used
        tool_calls = None
        response_content = ""
        
        if tools and self._should_use_tools(user_message):
            tool_calls = self._generate_tool_calls(user_message, tools)
            response_content = None  # No content when calling tools
        else:
            response_content = self._generate_direct_response(user_message)
        
        return {
            "content": response_content,
            "tool_calls": tool_calls,
            "finish_reason": "tool_calls" if tool_calls else "stop",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }
    
    async def _simulate_delay(self):
        """Simulate API latency"""
        import asyncio
        await asyncio.sleep(0.3 + random.random() * 0.3)
    
    def _should_use_tools(self, user_message: str) -> bool:
        """Determine if tools should be used based on message"""
        tool_keywords = [
            'install', 'part', 'ps11752778', 'compatible', 'compatibility',
            'model', 'wdt780saem1', 'fix', 'not working', 'problem', 'issue',
            'search', 'find', 'looking for', 'need', 'door', 'seal', 'ice maker',
            'whirlpool', 'refrigerator', 'dishwasher', 'broken'
        ]
        return any(keyword in user_message for keyword in tool_keywords)
    
    def _generate_tool_calls(self, user_message: str, tools: List[Dict]) -> List:
        """Generate simulated tool calls"""
        from types import SimpleNamespace
        
        tool_calls = []
        
        # Installation query
        if 'install' in user_message or 'ps11752778' in user_message:
            tool_calls.append(SimpleNamespace(
                id="call_1",
                function=SimpleNamespace(
                    name="get_product_by_part_number",
                    arguments='{"part_number": "PS11752778"}'
                )
            ))
            tool_calls.append(SimpleNamespace(
                id="call_2",
                function=SimpleNamespace(
                    name="get_installation_instructions",
                    arguments='{"part_number": "PS11752778"}'
                )
            ))
        
        # Compatibility query
        elif 'compatible' in user_message or 'wdt780saem1' in user_message:
            tool_calls.append(SimpleNamespace(
                id="call_1",
                function=SimpleNamespace(
                    name="check_compatibility",
                    arguments='{"part_number": "PS11752778", "model_number": "WDT780SAEM1"}'
                )
            ))
            tool_calls.append(SimpleNamespace(
                id="call_2",
                function=SimpleNamespace(
                    name="get_product_by_part_number",
                    arguments='{"part_number": "PS11752778"}'
                )
            ))
        
        # Ice maker troubleshooting
        elif 'ice maker' in user_message or ('not working' in user_message and 'whirlpool' in user_message):
            tool_calls.append(SimpleNamespace(
                id="call_1",
                function=SimpleNamespace(
                    name="search_troubleshooting",
                    arguments='{"problem": "ice maker not working", "brand": "Whirlpool"}'
                )
            ))
            tool_calls.append(SimpleNamespace(
                id="call_2",
                function=SimpleNamespace(
                    name="search_products",
                    arguments='{"query": "ice maker", "category": "refrigerator", "limit": 3}'
                )
            ))
        
        # Door seal search
        elif 'door' in user_message and ('seal' in user_message or 'gasket' in user_message):
            tool_calls.append(SimpleNamespace(
                id="call_1",
                function=SimpleNamespace(
                    name="search_products",
                    arguments='{"query": "door seal", "category": "refrigerator", "limit": 5}'
                )
            ))
        
        # General product search
        elif any(word in user_message for word in ['search', 'find', 'need', 'looking']):
            search_query = "refrigerator parts"
            if "door" in user_message or "seal" in user_message:
                search_query = "door seal"
            elif "ice" in user_message:
                search_query = "ice maker"
                
            tool_calls.append(SimpleNamespace(
                id="call_1",
                function=SimpleNamespace(
                    name="search_products",
                    arguments=f'{{"query": "{search_query}", "limit": 5}}'
                )
            ))
        
        return tool_calls if tool_calls else None
    
    def _generate_tool_response(self, user_message: str, messages: List) -> str:
        """Generate response after tools have been called"""
        
        # Ice maker troubleshooting
        if 'ice maker' in user_message:
            return """I found some solutions for your ice maker issue. Here are the recommended parts and troubleshooting steps:

**Common Causes:**
1. Check if the water supply line is connected and valve is open
2. Verify the ice maker is turned on (arm should be down)
3. Ensure freezer temperature is 0-5°F

**Recommended Replacement Parts:**
The products shown below are commonly needed for ice maker repairs. The Ice Maker Assembly (PS11752778) is the most common replacement part."""
        
        # Door seal search
        elif 'door' in user_message and 'seal' in user_message:
            return """I've found several door seal options for your refrigerator. A proper door gasket is essential for:

• Maintaining temperature
• Energy efficiency
• Preventing frost buildup

The door seals shown below are compatible with various refrigerator models. Check the part details for your specific model compatibility."""
        
        # Installation
        elif 'install' in user_message:
            return """Here are the installation instructions for the Ice Maker Assembly (PS11752778):

**Installation Steps:**
1. Turn off refrigerator and water supply
2. Remove ice bin and mounting screws
3. Disconnect wiring harness
4. Remove old ice maker
5. Install new unit and reconnect wiring
6. Secure with mounting screws
7. Turn on water and power

For detailed video instructions, visit the product page shown below."""
        
        # Compatibility
        elif 'compatible' in user_message:
            return """Yes, this part is compatible with your WDT780SAEM1 model!

**Compatible Models:**
• WDT780SAEM1
• WRS325SDHZ
• WRF535SWHZ
• MFI2570FEZ

You can view the complete product details below."""
        
        # Default tool response
        else:
            return """I've found some relevant parts for you. Please check the products shown below for details including pricing, compatibility, and installation information."""
    
    def _generate_direct_response(self, user_message: str) -> str:
        """Generate a direct response without tools"""
        responses = {
            "hello": "Hello! I'm your PartSelect assistant. I can help you with refrigerator and dishwasher parts. What can I help you with today?",
            "hi": "Hi there! I'm here to help with refrigerator and dishwasher parts. How can I assist you?",
            "help": "I can help you with:\n• Finding parts for your appliances\n• Checking compatibility\n• Installation instructions\n• Troubleshooting issues\n\nWhat would you like help with?",
            "thanks": "You're welcome! Feel free to ask if you need anything else!",
            "thank": "You're welcome! Let me know if there's anything else I can help with.",
            "bye": "Goodbye! Feel free to come back if you need help with any refrigerator or dishwasher parts!",
        }
        
        for keyword, response in responses.items():
            if keyword in user_message:
                return response
        
        # Default response
        return "I'd be happy to help! Could you please provide more details about what you're looking for? For example:\n• Part installation help\n• Compatibility checking\n• Troubleshooting an issue\n• Finding a specific part"


# Create alias for compatibility with existing imports
DeepSeekService = DemoDeepSeekService

# Singleton instance
_demo_deepseek_service = None


def get_deepseek_service():
    """Get or create DeepSeek service instance - Demo Mode"""
    global _demo_deepseek_service
    if _demo_deepseek_service is None:
        _demo_deepseek_service = DemoDeepSeekService()
    return _demo_deepseek_service