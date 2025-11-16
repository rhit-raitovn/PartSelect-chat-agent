"""
DeepSeek LLM Integration Service
"""
import os
from typing import List, Dict, Any
from openai import OpenAI

KEY = "OPENROUTER_API_KEY"
URL = "https://openrouter.ai/api/v1"

# OpenRouter CORRECT model
my_model = "deepseek/deepseek-chat"


class DeepSeekService:
    """Service for interacting with DeepSeek LLM via OpenRouter"""

    def __init__(self):
        self.api_key = os.getenv(KEY, "")
        self.base_url = URL

        if not self.api_key:
            raise ValueError(f"{KEY} environment variable is required")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        self.model = my_model

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        tools: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }

            if tools:
                params["tools"] = tools
                params["tool_choice"] = "auto"

            response = self.client.chat.completions.create(**params)

            return {
                "content": response.choices[0].message.content,
                "tool_calls": getattr(response.choices[0].message, "tool_calls", None),
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
            }

        except Exception as e:
            error_msg = str(e)
            return {
                "content": f"DeepSeek API error: {error_msg}",
                "tool_calls": None,
                "finish_reason": "error",
                "usage": None,
            }


# Singleton
_deepseek_service = None


def get_deepseek_service() -> DeepSeekService:
    global _deepseek_service
    if _deepseek_service is None:
        _deepseek_service = DeepSeekService()
    return _deepseek_service
