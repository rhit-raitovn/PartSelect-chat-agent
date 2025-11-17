# backend/app/agent/core.py

import re
import json
from typing import Dict, List, Optional, Any
from enum import Enum


class Intent(Enum):
    """User intent categories"""
    INSTALLATION_HELP = "installation_help"
    COMPATIBILITY_CHECK = "compatibility_check"
    PRODUCT_SEARCH = "product_search"
    TROUBLESHOOTING = "troubleshooting"
    GENERAL_INQUIRY = "general_inquiry"


class PartSelectAgent:
    """Main agent that processes user queries"""
    
    def __init__(self, products_data: List[Dict]):
        """Initialize with products from JSON"""
        self.products = {p['part_number']: p for p in products_data}
        print(f"Agent initialized with {len(self.products)} products")
    
    def classify_intent(self, message: str) -> Intent:
        """
        Classify user intent - THIS IS CRITICAL
        """
        msg = message.lower()
        
        # Check for installation keywords FIRST
        installation_keywords = [
            'install', 'installation', 'how to install', 
            'how do i install', 'how can i install',
            'steps', 'replace', 'replacement', 'installing'
        ]
        
        if any(keyword in msg for keyword in installation_keywords):
            print(f"Detected INSTALLATION intent from: {message}")
            return Intent.INSTALLATION_HELP
        
        # Compatibility check
        compatibility_keywords = [
            'compatible', 'compatibility', 'fit', 'work with',
            'will this work', 'does this fit', 'match my'
        ]
        
        if any(word in msg for word in compatibility_keywords):
            print(f"Detected COMPATIBILITY intent from: {message}")
            return Intent.COMPATIBILITY_CHECK
        
        # Product search
        if any(word in msg for word in ['find', 'search', 'need', 'looking for']):
            print(f"Detected PRODUCT SEARCH intent from: {message}")
            return Intent.PRODUCT_SEARCH
        
        # Troubleshooting
        if any(word in msg for word in ['not working', 'broken', 'problem', 'fix', 'troubleshoot']):
            print(f"Detected TROUBLESHOOTING intent from: {message}")
            return Intent.TROUBLESHOOTING
        
        print(f"Detected GENERAL INQUIRY intent from: {message}")
        return Intent.GENERAL_INQUIRY
    
    def extract_part_number(self, message: str) -> Optional[str]:
        """
        Extract part number like PS11752778
        """
        # Look for PS followed by digits
        match = re.search(r'PS\d+', message.upper())
        if match:
            part_num = match.group(0)
            print(f"🔍 Extracted part number: {part_num}")
            return part_num
        return None
    
    def extract_model_number(self, message: str) -> Optional[str]:
        """
        Extract appliance model number from message
        Examples: WDT780SAEM1, WRS325SDHZ, 106.51133110
        """
        # Pattern 1: Standard format like WDT780SAEM1
        match = re.search(r'\b[A-Z]{3}\d{3}[A-Z0-9]{4,}\b', message.upper())
        if match:
            model = match.group(0)
            print(f"Extracted model number: {model}")
            return model
        
        # Pattern 2: Kenmore format like 106.51133110
        match = re.search(r'\b\d{3}\.\d{8}\b', message)
        if match:
            model = match.group(0)
            print(f"Extracted model number: {model}")
            return model
        
        # Pattern 3: General alphanumeric model
        match = re.search(r'\b[A-Z]{2,}\d{4}[A-Z0-9]+\b', message.upper())
        if match:
            model = match.group(0)
            print(f"Extracted model number: {model}")
            return model
        
        print(f"No model number found in: {message}")
        return None
    
    def get_installation_guide(self, part_number: str) -> Dict[str, Any]:
        """
        Get installation steps from product data
        """
        print(f"📖 Looking up installation guide for {part_number}")
        
        # Check if part exists
        if part_number not in self.products:
            print(f"Part {part_number} not found")
            return {
                "found": False,
                "message": f"Part number {part_number} not found in our catalog."
            }
        
        product = self.products[part_number]
        print(f"Found product: {product['name']}")
        
        # Check if installation steps exist
        if 'installation_steps' in product and product['installation_steps']:
            steps = product['installation_steps'].split('\n')
            print(f"Found {len(steps)} installation steps")
            
            return {
                "found": True,
                "has_steps": True,
                "part_number": part_number,
                "part_name": product['name'],
                "description": product['description'],
                "steps": steps,
                "guide_url": product.get('installation_guide_url', ''),
                "price": product['price'],
                "category": product['category']
            }
        else:
            print(f"No installation steps in data for {part_number}")
            return {
                "found": True,
                "has_steps": False,
                "part_number": part_number,
                "part_name": product['name'],
                "description": product['description'],
                "guide_url": product.get('installation_guide_url', ''),
                "message": "Installation steps not available in text format."
            }
    
    def check_compatibility(self, part_number: str, model_number: str) -> Dict[str, Any]:
        """
        Check if a part is compatible with a specific model
        """
        print(f"Checking compatibility: {part_number} with {model_number}")
        
        if part_number not in self.products:
            return {
                "found": False,
                "message": f"Part {part_number} not found."
            }
        
        product = self.products[part_number]
        compatible_models = product.get('compatibility', [])
        
        is_compatible = model_number.upper() in [m.upper() for m in compatible_models]
                
        return {
            "found": True,
            "part_number": part_number,
            "part_name": product['name'],
            "model_number": model_number,
            "is_compatible": is_compatible,
            "compatible_models": compatible_models,
            "price": product['price'],
            "category": product['category']
        }
    
    def find_parts_for_model(self, model_number: str) -> Dict[str, Any]:
        """
        Find all parts compatible with a model
        """
        print(f"Finding parts for model: {model_number}")
        
        compatible_parts = []
        
        for part_num, product in self.products.items():
            compatible_models = product.get('compatibility', [])
            if model_number.upper() in [m.upper() for m in compatible_models]:
                compatible_parts.append({
                    "part_number": part_num,
                    "name": product['name'],
                    "price": product['price'],
                    "category": product['category'],
                    "description": product['description']
                })
        
        print(f"Found {len(compatible_parts)} compatible parts")
        
        return {
            "model_number": model_number,
            "compatible_parts": compatible_parts,
            "count": len(compatible_parts)
        }
    
    def search_parts(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """
        Search for parts based on query string
        """
        print(f"Searching for: {query}")
        
        results = []
        query_lower = query.lower()
        
        for part_number, product in self.products.items():
            # Check if query matches name, description, or part number
            if (query_lower in product['name'].lower() or 
                query_lower in product['description'].lower() or
                query_lower in part_number.lower()):
                
                # Filter by category if specified
                if category and product['category'] != category.lower():
                    continue
                    
                results.append({
                    "part_number": part_number,
                    "name": product['name'],
                    "description": product['description'],
                    "price": product['price'],
                    "category": product['category'],
                    "image_url": product.get('image_url', '')
                })
        
        print(f"Found {len(results)} results")
        return results
    
    def troubleshoot_issue(self, message: str, model_number: Optional[str] = None) -> Dict[str, Any]:
        """
        Troubleshoot appliance issues and suggest parts
        """
        print(f"Troubleshooting: {message}")
        
        msg_lower = message.lower()
        
        # Common issue patterns and related parts
        issue_patterns = {
            'ice maker': {
                'keywords': ['ice maker', 'ice', 'not making ice', 'no ice'],
                'category': 'refrigerator',
                'common_parts': ['ice maker assembly', 'water inlet valve', 'water filter'],
                'diagnosis': "Ice maker issues are commonly caused by:",
                'steps': [
                    "Check if the ice maker is turned on",
                    "Verify water supply is connected and valve is open",
                    "Check for frozen water line",
                    "Inspect the water inlet valve",
                    "Replace water filter if it's been 6+ months",
                    "Test the ice maker assembly"
                ]
            },
            'not cooling': {
                'keywords': ['not cooling', 'not cold', 'warm', 'temperature'],
                'category': 'refrigerator',
                'common_parts': ['evaporator fan motor', 'temperature control', 'door gasket'],
                'diagnosis': "Cooling issues can be caused by:",
                'steps': [
                    "Check if the temperature is set correctly",
                    "Ensure the vents are not blocked",
                    "Check door seals for gaps",
                    "Listen for the evaporator fan running",
                    "Clean the condenser coils",
                    "Check the temperature control thermostat"
                ]
            },
            'leaking': {
                'keywords': ['leak', 'leaking', 'water on floor', 'dripping'],
                'category': 'refrigerator',
                'common_parts': ['water inlet valve', 'door gasket', 'drain pump'],
                'diagnosis': "Water leaks can come from:",
                'steps': [
                    "Check the water line connections",
                    "Inspect the water inlet valve",
                    "Check the defrost drain for clogs",
                    "Inspect door gaskets for damage",
                    "Check the drain pan"
                ]
            },
            'not washing': {
                'keywords': ['not washing', 'not cleaning', 'dishes dirty'],
                'category': 'dishwasher',
                'common_parts': ['spray arm', 'heating element', 'drain pump'],
                'diagnosis': "Poor washing performance can be due to:",
                'steps': [
                    "Check spray arms for clogs",
                    "Ensure water temperature is adequate (120°F)",
                    "Clean the filter",
                    "Check water inlet valve",
                    "Inspect spray arm for damage"
                ]
            },
            'not draining': {
                'keywords': ['not draining', 'water standing', 'won\'t drain'],
                'category': 'dishwasher',
                'common_parts': ['drain pump', 'door latch'],
                'diagnosis': "Drainage issues are often caused by:",
                'steps': [
                    "Check for clogs in the drain hose",
                    "Clean the filter and drain area",
                    "Inspect the drain pump",
                    "Check the garbage disposal knockout plug",
                    "Verify drain hose is not kinked"
                ]
            }
        }
        
        # Detect which issue pattern matches
        detected_issue = None
        for issue_name, issue_data in issue_patterns.items():
            if any(keyword in msg_lower for keyword in issue_data['keywords']):
                detected_issue = issue_name
                issue_info = issue_data
                break
        
        if not detected_issue:
            # Generic troubleshooting response
            return {
                "issue_detected": False,
                "message": "I can help troubleshoot your appliance! To provide specific guidance, please tell me:\n\n• What appliance is having issues? (refrigerator/dishwasher)\n• What's the problem? (not cooling, leaking, not draining, etc.)\n• What's your model number?\n\nFor example: 'My WDT780SAEM1 dishwasher is not draining'"
            }
        
        print(f"Detected issue: {detected_issue}")
        
        # Find related parts
        related_parts = []
        for part_num, product in self.products.items():
            # Match by category and common part names
            if product['category'] == issue_info['category']:
                for common_part in issue_info['common_parts']:
                    if common_part.lower() in product['name'].lower():
                        # Filter by model if provided
                        if model_number:
                            compatible_models = product.get('compatibility', [])
                            if model_number.upper() in [m.upper() for m in compatible_models]:
                                related_parts.append(product)
                                break
                        else:
                            related_parts.append(product)
                            break
        
        print(f"Found {len(related_parts)} related parts")
        
        return {
            "issue_detected": True,
            "issue_type": detected_issue,
            "diagnosis": issue_info['diagnosis'],
            "troubleshooting_steps": issue_info['steps'],
            "related_parts": related_parts[:5],  # Limit to 5 parts
            "model_number": model_number,
            "category": issue_info['category']
        }
    
    def process_message(self, user_message: str) -> Dict[str, Any]:
        """
        Main processing method - THIS GETS CALLED FROM YOUR API
        """
        print(f"\n{'='*60}")
        print(f"Processing: {user_message}")
        print(f"{'='*60}")
        
        # Step 1: Classify intent
        intent = self.classify_intent(user_message)
        print(f"Intent: {intent.value}")
        
        # Step 2: Extract entities
        part_number = self.extract_part_number(user_message)
        model_number = self.extract_model_number(user_message)
        
        # Step 3: Handle based on intent
        if intent == Intent.INSTALLATION_HELP:
            if part_number:
                guide_data = self.get_installation_guide(part_number)
                
                # Add suggested actions
                suggested_actions = [
                    "Watch installation video",
                    f"Is {part_number} compatible with my model?",
                    "Contact support"
                ]
                
                return {
                    "intent": intent.value,
                    "response_type": "installation_guide",
                    "data": guide_data,
                    "suggested_actions": suggested_actions
                }
            else:
                return {
                    "intent": intent.value,
                    "response_type": "need_part_number",
                    "data": {
                        "message": "Please provide a part number (starts with PS) to get installation instructions."
                    },
                    "suggested_actions": [
                        "How can I install part number PS11752778?",
                        "Find ice maker parts",
                        "Check compatibility"
                    ]
                }
        
        elif intent == Intent.COMPATIBILITY_CHECK:
            if part_number and model_number:
                # Check if specific part is compatible with model
                compatibility = self.check_compatibility(part_number, model_number)
                
                suggested_actions = [
                    f"How do I install {part_number}?",
                    "Watch installation video",
                    "Contact support"
                ]
                
                return {
                    "intent": intent.value,
                    "response_type": "compatibility_check",
                    "data": compatibility,
                    "suggested_actions": suggested_actions
                }
            elif model_number:
                # Show all compatible parts for this model
                compatible_parts = self.find_parts_for_model(model_number)
                
                suggested_actions = [
                    f"Troubleshoot issues with {model_number}",
                    "Find ice maker parts",
                    "Find dishwasher parts"
                ]
                
                return {
                    "intent": intent.value,
                    "response_type": "compatible_parts_list",
                    "data": compatible_parts,
                    "suggested_actions": suggested_actions
                }
            elif part_number:
                # Show what models this part fits
                if part_number in self.products:
                    product = self.products[part_number]
                    
                    suggested_actions = [
                        f"How do I install {part_number}?",
                        f"Find similar parts to {part_number}",
                        "Check with my model number"
                    ]
                    
                    return {
                        "intent": intent.value,
                        "response_type": "part_compatibility_list",
                        "data": {
                            "part_number": part_number,
                            "part_name": product['name'],
                            "compatible_models": product.get('compatibility', [])
                        },
                        "suggested_actions": suggested_actions
                    }
            else:
                return {
                    "intent": intent.value,
                    "response_type": "need_more_info",
                    "data": {
                        "message": "Please provide a part number or model number to check compatibility."
                    },
                    "suggested_actions": [
                        "Is PS11752778 compatible with WDT780SAEM1?",
                        "Find parts for my model",
                        "Installation help"
                    ]
                }
        
        elif intent == Intent.PRODUCT_SEARCH:
            # Extract search terms (remove common words)
            search_terms = user_message.lower()
            for word in ['find', 'search', 'need', 'looking for', 'part']:
                search_terms = search_terms.replace(word, '')
            search_terms = search_terms.strip()
            
            if search_terms:
                results = self.search_parts(search_terms)
                
                suggested_actions = [
                    "Check compatibility with my model",
                    "Installation help",
                    "Troubleshooting"
                ]
                
                return {
                    "intent": intent.value,
                    "response_type": "search_results",
                    "data": {
                        "results": results,
                        "count": len(results),
                        "query": search_terms
                    },
                    "suggested_actions": suggested_actions
                }
        
        elif intent == Intent.TROUBLESHOOTING:
            # Troubleshooting logic
            troubleshooting_data = self.troubleshoot_issue(user_message, model_number)
            
            # Generate dynamic suggested actions based on detected issue
            if troubleshooting_data.get("issue_detected"):
                suggested_actions = []
                
                # Add part-specific actions if parts were found
                related_parts = troubleshooting_data.get("related_parts", [])
                if related_parts:
                    first_part = related_parts[0]
                    suggested_actions.append(f"How do I install {first_part['part_number']}?")
                    suggested_actions.append("Watch installation video")
                
                # Always add contact support
                suggested_actions.append("Contact support")
                
                # Limit to 3 actions
                suggested_actions = suggested_actions[:3]
            else:
                suggested_actions = [
                    "My ice maker is not working",
                    "My dishwasher won't drain",
                    "Contact support"
                ]
            
            return {
                "intent": intent.value,
                "response_type": "troubleshooting",
                "data": troubleshooting_data,
                "suggested_actions": suggested_actions
            }
        
        # Default response for general inquiries or unhandled cases
        return {
            "intent": intent.value,
            "response_type": "general",
            "data": {
                "message": "I can help you with:\n• Installation guides for parts\n• Checking part compatibility with your appliance model\n• Finding parts by name or description\n• Troubleshooting appliance issues\n\nWhat would you like help with?"
            },
            "suggested_actions": [
                "How can I install part number PS11752778?",
                "Is this part compatible with my WDT780SAEM1 model?",
                "My Whirlpool ice maker is not working"
            ]
        }


def format_agent_response(agent_response: Dict[str, Any]) -> str:
    """
    Convert agent response to user-friendly text
    THIS CREATES THE FINAL MESSAGE THE USER SEES
    """
    response_type = agent_response.get("response_type")
    data = agent_response.get("data", {})
    
    if response_type == "installation_guide":
        if not data.get("found"):
            return f"{data.get('message', 'Part not found.')}"
        
        if not data.get("has_steps"):
            return f"""**{data['part_name']}** (Part #{data['part_number']})

{data['description']}

Installation steps are not available in text format, but you can find video guides here:
{data.get('guide_url', 'Visit PartSelect.com')}"""
        
        # BUILD THE CORRECT RESPONSE
        message = f"**{data['part_name']}** (Part #{data['part_number']})\n\n"
        message += f"{data['description']}\n\n"
        message += "**Installation Steps:**\n\n"
        
        for step in data['steps']:
            message += f"{step}\n"
        
        message += f"\n**Video Guide:** {data.get('guide_url', 'N/A')}"
        message += f"\n**Price:** ${data['price']}"
        message += "\n\n**Safety Note:** Always disconnect power and water supply before beginning installation."
        
        return message
    
    elif response_type == "compatibility_check":
        if not data.get("found"):
            return f"{data.get('message', 'Part not found.')}"
        
        part_name = data.get("part_name")
        part_number = data.get("part_number")
        model_number = data.get("model_number")
        is_compatible = data.get("is_compatible")
        
        if is_compatible:
            message = f"**Yes! {part_name} (Part #{part_number}) is compatible with model {model_number}!**\n\n"
            message += f"**Price:** ${data.get('price', 'N/A')}\n\n"
            message += "**This part also fits these models:**\n"
            for model in data.get("compatible_models", [])[:8]:
                message += f"• {model}\n"
            if len(data.get("compatible_models", [])) > 8:
                message += f"...and {len(data.get('compatible_models', [])) - 8} more models\n"
        else:
            message = f"**No, {part_name} (Part #{part_number}) is NOT compatible with model {model_number}.**\n\n"
            message += "**This part is designed for:**\n"
            for model in data.get("compatible_models", [])[:8]:
                message += f"• {model}\n"
            if len(data.get("compatible_models", [])) > 8:
                message += f"...and {len(data.get('compatible_models', [])) - 8} more models\n"
            message += f"\nWould you like me to find parts that are compatible with your {model_number}?"
        
        return message
    
    elif response_type == "compatible_parts_list":
        model_number = data.get("model_number")
        parts = data.get("compatible_parts", [])
        count = data.get("count", 0)
        
        if count == 0:
            return f"I couldn't find any parts for model **{model_number}** in our database. Please verify the model number."
        
        message = f"**Found {count} compatible part(s) for model {model_number}:**\n\n"
        
        # Group by category
        categories = {}
        for part in parts:
            cat = part['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(part)
        
        for category, cat_parts in categories.items():
            message += f"\n**{category.capitalize()} Parts:**\n"
            for part in cat_parts[:5]:
                message += f"• **{part['name']}** (Part #{part['part_number']}) - ${part['price']}\n"
            if len(cat_parts) > 5:
                message += f"  ...and {len(cat_parts) - 5} more {category} parts\n"
        
        return message
    
    elif response_type == "part_compatibility_list":
        part_name = data.get("part_name")
        part_number = data.get("part_number")
        models = data.get("compatible_models", [])
        
        message = f"**{part_name}** (Part #{part_number})\n\n"
        message += f"**Compatible with {len(models)} models:**\n\n"
        for model in models[:10]:
            message += f"• {model}\n"
        if len(models) > 10:
            message += f"...and {len(models) - 10} more models\n"
        
        message += "\nWant to check if this fits your specific model? Just ask!"
        
        return message
    
    elif response_type == "search_results":
        results = data.get("results", [])
        count = data.get("count", 0)
        query = data.get("query", "")
        
        if count == 0:
            return f"No parts found matching '{query}'. Try different keywords or ask me to find specific parts!"
        
        message = f"**Found {count} part(s) matching '{query}':**\n\n"
        for result in results[:5]:
            message += f"**{result['name']}** (Part #{result['part_number']})\n"
            message += f"${result['price']} | {result['category']}\n"
            message += f"{result['description'][:100]}...\n\n"
        
        if count > 5:
            message += f"...and {count - 5} more results.\n"
        
        message += "\nAsk me for installation help or compatibility check for any part!"
        
        return message
    
    elif response_type == "troubleshooting":
        if not data.get("issue_detected"):
            return data.get("message", "Please provide more details about the issue.")
        
        issue_type = data.get("issue_type", "")
        diagnosis = data.get("diagnosis", "")
        steps = data.get("troubleshooting_steps", [])
        parts = data.get("related_parts", [])
        model_number = data.get("model_number")
        
        message = f"**Troubleshooting: {issue_type.replace('_', ' ').title()}**\n\n"
        
        if model_number:
            message += f"Model: {model_number}\n\n"
        
        message += f"{diagnosis}\n\n"
        message += "**Troubleshooting Steps:**\n\n"
        
        for i, step in enumerate(steps, 1):
            message += f"{i}. {step}\n"
        
        if parts:
            message += f"\n**Common Replacement Parts:**\n\n"
            for part in parts:
                message += f"• **{part['name']}** (Part #{part['part_number']}) - ${part['price']}\n"
            
            message += "\nAsk me about any part for installation instructions or compatibility!"
        else:
            message += "\nNeed a specific part? Tell me your model number and I'll find compatible parts!"
        
        return message
    
    elif response_type == "need_part_number":
        return data.get("message", "Please provide a part number.")
    
    elif response_type == "need_more_info":
        return data.get("message", "Please provide more information.")
    
    else:
        return data.get("message", "How can I help you today?")