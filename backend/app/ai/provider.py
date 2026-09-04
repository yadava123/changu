from typing import Any
import httpx
from app.core.config import settings

class AIProvider:
    async def generate(self, messages: list[dict[str, str]], context: dict[str, Any] | None = None) -> str:
        raise NotImplementedError

class UnavailableProvider(AIProvider):
    async def generate(self, messages, context=None) -> str:
        raise RuntimeError("AI provider is unavailable")


class RulesProvider(AIProvider):
    async def generate(self, messages, context=None) -> str:
        return str((context or {}).get("fallback", "I can help you use ChanGu services."))


class GeminiProvider(AIProvider):
    async def generate(self, messages, context=None) -> str:
        if not settings.gemini_api_key:
            raise RuntimeError("Gemini is not configured")
        contents = [{"role": "user" if message["role"] != "assistant" else "model", "parts": [{"text": message["content"]}]} for message in messages]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.ai_model}:generateContent"
        async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
            response = await client.post(url, params={"key": settings.gemini_api_key}, json={"contents": contents, "generationConfig": {"temperature": settings.ai_temperature, "maxOutputTokens": settings.ai_max_tokens}})
            response.raise_for_status()
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]


class GroqProvider(AIProvider):
    async def generate(self, messages, context=None) -> str:
        if not settings.groq_api_key:
            raise RuntimeError("Groq is not configured")
        async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
            response = await client.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {settings.groq_api_key}"}, json={"model": settings.ai_model, "messages": messages, "temperature": settings.ai_temperature, "max_tokens": settings.ai_max_tokens})
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]


def configured_provider() -> AIProvider:
    provider = settings.ai_provider.lower()
    if provider == "gemini":
        return GeminiProvider()
    if provider == "groq":
        return GroqProvider()
    return RulesProvider()
