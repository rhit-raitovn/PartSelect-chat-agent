"""
Agent Tools - Function definitions for tool calling
"""
from typing import List, Dict, Any
from app.services.vector_db import get_vector_db_service
from app.models.schemas import Product


class AgentTools:
    """Tools available to the agent for answering user queries"""
    
    def __init__(self):
        self.vector_db = get_vector_db_service()
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions for function calling"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_products",
                    "description": "Search for refrigerator or dishwasher parts by description, part number, or category",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (e.g., 'ice maker', 'door seal', 'PS11752778')"
                            },
                            "category": {
                                "type": "string",
                                "enum": ["refrigerator", "dishwasher", "all"],
                                "description": "Filter by category"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 5)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_product_by_part_number",
                    "description": "Get detailed information about a specific part by its part number",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "part_number": {
                                "type": "string",
                                "description": "The part number (e.g., PS11752778)"
                            }
                        },
                        "required": ["part_number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_compatibility",
                    "description": "Check if a part is compatible with a specific appliance model",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "part_number": {
                                "type": "string",
                                "description": "The part number to check"
                            },
                            "model_number": {
                                "type": "string",
                                "description": "The appliance model number"
                            }
                        },
                        "required": ["part_number", "model_number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_installation_instructions",
                    "description": "Get installation instructions for a specific part",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "part_number": {
                                "type": "string",
                                "description": "The part number"
                            }
                        },
                        "required": ["part_number"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_troubleshooting",
                    "description": "Search for troubleshooting guides for common appliance problems",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "problem": {
                                "type": "string",
                                "description": "Description of the problem (e.g., 'ice maker not working')"
                            },
                            "brand": {
                                "type": "string",
                                "description": "Appliance brand (optional)"
                            }
                        },
                        "required": ["problem"]
                    }
                }
            }
        ]
    
    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool and return results"""
        
        if tool_name == "search_products":
            return await self._search_products(**arguments)
        elif tool_name == "get_product_by_part_number":
            return await self._get_product_by_part_number(**arguments)
        elif tool_name == "check_compatibility":
            return await self._check_compatibility(**arguments)
        elif tool_name == "get_installation_instructions":
            return await self._get_installation_instructions(**arguments)
        elif tool_name == "search_troubleshooting":
            return await self._search_troubleshooting(**arguments)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    async def _search_products(
        self,
        query: str,
        category: str = "all",
        limit: int = 5
    ) -> Dict[str, Any]:
        """Search for products"""
        filter_dict = None
        if category != "all":
            filter_dict = {"category": category}
        
        products = self.vector_db.search_products(
            query=query,
            n_results=limit,
            filter_dict=filter_dict
        )
        
        return {
            "products": products,
            "count": len(products)
        }
    
    async def _get_product_by_part_number(
        self,
        part_number: str
    ) -> Dict[str, Any]:
        """Get product by part number"""
        product = self.vector_db.get_product_by_part_number(part_number)
        
        if product:
            return {"product": product}
        else:
            return {"error": f"Product with part number {part_number} not found"}
    
    async def _check_compatibility(
        self,
        part_number: str,
        model_number: str
    ) -> Dict[str, Any]:
        """Check part compatibility"""
        is_compatible = self.vector_db.check_compatibility(
            part_number=part_number,
            model_number=model_number
        )
        
        product = self.vector_db.get_product_by_part_number(part_number)
        
        return {
            "compatible": is_compatible,
            "part_number": part_number,
            "model_number": model_number,
            "compatible_models": product.get('compatibility', []) if product else []
        }
    
    async def _get_installation_instructions(
        self,
        part_number: str
    ) -> Dict[str, Any]:
        """Get installation instructions"""
        product = self.vector_db.get_product_by_part_number(part_number)
        
        if product and product.get('installation_guide_url'):
            return {
                "part_number": part_number,
                "installation_url": product['installation_guide_url'],
                "instructions": product.get('installation_steps', 'Visit the installation guide URL for detailed instructions.')
            }
        else:
            return {
                "error": f"Installation instructions not available for {part_number}",
                "suggestion": "Please visit PartSelect.com for video installation guides."
            }
    
    async def _search_troubleshooting(
        self,
        problem: str,
        brand: str = None
    ) -> Dict[str, Any]:
        """Search troubleshooting guides"""
        guides = self.vector_db.search_troubleshooting(
            problem_description=problem,
            n_results=3
        )
        
        # Filter by brand if specified
        if brand:
            guides = [g for g in guides if g.get('brand', '').lower() == brand.lower()]
        
        return {
            "guides": guides,
            "count": len(guides)
        }


def get_agent_tools() -> AgentTools:
    """Get agent tools instance"""
    return AgentTools()