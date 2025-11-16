"""
Intent Classification Module
"""
import re
from typing import Dict, Any
from app.models.schemas import Intent, IntentType
from app.services.deepseek import get_deepseek_service


class IntentClassifier:
    """Classify user intents from messages"""
    
    def __init__(self):
        self.deepseek = get_deepseek_service()
        
        # Keywords for quick pattern matching
        self.intent_patterns = {
            IntentType.INSTALLATION: [
                r'\b(install|installation|how to install|setup|mount|attach)\b',
                r'\b(step by step|instructions|guide)\b'
            ],
            IntentType.COMPATIBILITY: [
                r'\b(compatible|compatibility|work with|fit|match)\b',
                r'\b(model|appliance) (number|#)?\s*[A-Z0-9]+\b'
            ],
            IntentType.TROUBLESHOOTING: [
                r'\b(fix|repair|not working|broken|problem|issue|trouble)\b',
                r'\b(won\'t|doesn\'t|can\'t|stopped)\b'
            ],
            IntentType.PRODUCT_INFO: [
                r'\b(price|cost|how much|specifications|specs|details)\b',
                r'\b(part number|part #|PS\d+)\b'
            ],
            IntentType.ORDER_SUPPORT: [
                r'\b(order|purchase|buy|shipping|delivery|return|refund)\b',
                r'\b(track|status|when will)\b'
            ]
        }
    
    async def classify(self, message: str) -> Intent:
        """
        Classify user intent from message
        
        Args:
            message: User message text
            
        Returns:
            Intent object with type, confidence, and extracted entities
        """
        message_lower = message.lower()
        
        # First try pattern matching for quick classification
        pattern_scores = {}
        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    score += 1
            if score > 0:
                pattern_scores[intent_type] = score
        
        # If clear pattern match, use it
        if pattern_scores:
            best_intent = max(pattern_scores, key=pattern_scores.get)
            confidence = min(0.7 + (pattern_scores[best_intent] * 0.1), 0.95)
            
            # Extract entities based on intent
            entities = self._extract_entities(message, best_intent)
            
            return Intent(
                intent_type=best_intent,
                confidence=confidence,
                entities=entities
            )
        
        # If no clear pattern, use LLM for classification
        return await self._llm_classify(message)
    
    async def _llm_classify(self, message: str) -> Intent:
        """Use LLM to classify intent when patterns don't match"""
        system_prompt = """You are an intent classifier for a refrigerator and dishwasher parts e-commerce site.
Classify the user's message into one of these intents:
- installation: User wants installation instructions
- compatibility: User wants to check if a part works with their appliance
- troubleshooting: User has a problem and needs help fixing it
- product_info: User wants information about a product
- order_support: User has questions about ordering, shipping, or returns
- general: General questions about parts or appliances
- out_of_scope: Question is not related to refrigerator/dishwasher parts

Also extract any entities like:
- part_number: Part numbers (e.g., PS11752778)
- model_number: Appliance model numbers (e.g., WDT780SAEM1)
- brand: Brand name (e.g., Whirlpool, GE)
- issue: Description of the problem

Respond ONLY with valid JSON in this format:
{
    "intent": "intent_type",
    "confidence": 0.85,
    "entities": {
        "part_number": "PS11752778",
        "model_number": "WDT780SAEM1"
    }
}"""
        
        try:
            response = await self.deepseek.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            # Parse JSON response
            import json
            result = json.loads(response['content'])
            
            return Intent(
                intent_type=IntentType(result.get('intent', 'general')),
                confidence=result.get('confidence', 0.5),
                entities=result.get('entities', {})
            )
        except Exception as e:
            # Fallback to general intent on error
            return Intent(
                intent_type=IntentType.GENERAL,
                confidence=0.5,
                entities={}
            )
    
    def _extract_entities(
        self,
        message: str,
        intent_type: IntentType
    ) -> Dict[str, Any]:
        """Extract entities from message based on intent type"""
        entities = {}
        
        # Extract part numbers (PS followed by digits)
        part_match = re.search(r'\b(PS\d{8,})\b', message, re.IGNORECASE)
        if part_match:
            entities['part_number'] = part_match.group(1).upper()
        
        # Extract model numbers (alphanumeric with specific pattern)
        model_match = re.search(r'\b([A-Z]{2,}\d{3,}[A-Z0-9]*)\b', message)
        if model_match:
            entities['model_number'] = model_match.group(1).upper()
        
        # Extract brand names
        brands = ['whirlpool', 'ge', 'samsung', 'lg', 'frigidaire', 'kenmore', 'bosch', 'kitchenaid']
        for brand in brands:
            if brand in message.lower():
                entities['brand'] = brand.capitalize()
                break
        
        # For troubleshooting, extract the issue description
        if intent_type == IntentType.TROUBLESHOOTING:
            # Simple heuristic: look for "not working", "broken", etc.
            issue_patterns = [
                r'(ice maker|water dispenser|compressor|door|seal).*(not working|broken|stopped|won\'t)',
                r'(not working|broken|stopped|won\'t).*(ice maker|water dispenser|compressor|door|seal)'
            ]
            for pattern in issue_patterns:
                match = re.search(pattern, message.lower())
                if match:
                    entities['issue'] = match.group(0)
                    break
        
        return entities


def get_intent_classifier() -> IntentClassifier:
    """Get intent classifier instance"""
    return IntentClassifier()