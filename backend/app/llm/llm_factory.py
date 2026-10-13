from app.core.config import settings
from app.llm.base_llm_provider import BaseLLMProvider


def create_llm_provider() -> BaseLLMProvider:
    if settings.llm_provider == "gemini":
        from app.llm.gemini_provider import GeminiProvider

        return GeminiProvider()
    raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")
