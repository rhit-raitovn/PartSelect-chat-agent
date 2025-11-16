"""Services package"""
import os
import sys

# Try to import from the current deepseek module
try:
    from .deepseek import get_deepseek_service
    # Try to get the service class name dynamically
    try:
        from .deepseek import DeepSeekService
    except ImportError:
        from .deepseek import DemoDeepSeekService as DeepSeekService
except ImportError:
    from .deepseek import get_deepseek_service
    DeepSeekService = None

from .vector_db import VectorDBService, get_vector_db_service
from .cache import CacheService, get_cache_service

__all__ = [
    "DeepSeekService",
    "get_deepseek_service",
    "VectorDBService",
    "get_vector_db_service",
    "CacheService",
    "get_cache_service"
]