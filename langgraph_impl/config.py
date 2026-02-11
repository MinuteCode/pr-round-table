"""
Model configuration for the LangGraph code review tool.

Supports three providers:
- Anthropic Claude (ANTHROPIC_API_KEY)
- OpenAI GPT (OPENAI_API_KEY)
- OpenRouter (OPENROUTER_API_KEY)
"""

import os
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
    "openrouter": "anthropic/claude-sonnet-4",
}

MAX_TOKENS = 16384


def get_model(provider: str = None, model_id: str = None):
    """
    Return a LangChain chat model based on provider or auto-detect from API keys.

    Args:
        provider: Force a specific provider ("anthropic", "openai", "openrouter")
        model_id: Override the default model ID for the provider

    Priority when auto-detecting: Anthropic > OpenAI > OpenRouter
    """
    if provider:
        return _get_model_for_provider(provider, model_id)

    if os.getenv("ANTHROPIC_API_KEY"):
        return ChatAnthropic(
            model=model_id or DEFAULT_MODELS["anthropic"],
            max_tokens=MAX_TOKENS,
        )
    elif os.getenv("OPENAI_API_KEY"):
        return ChatOpenAI(
            model=model_id or DEFAULT_MODELS["openai"],
            max_tokens=MAX_TOKENS,
        )
    elif os.getenv("OPENROUTER_API_KEY"):
        return ChatOpenAI(
            model=model_id or DEFAULT_MODELS["openrouter"],
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            max_tokens=MAX_TOKENS,
        )
    else:
        raise ValueError(
            "No API key found. Set one of:\n"
            "  - ANTHROPIC_API_KEY\n"
            "  - OPENAI_API_KEY\n"
            "  - OPENROUTER_API_KEY"
        )


def _get_model_for_provider(provider: str, model_id: str = None):
    """Get model for a specific provider."""
    provider = provider.lower()

    if provider == "anthropic":
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY not set")
        return ChatAnthropic(
            model=model_id or DEFAULT_MODELS["anthropic"],
            max_tokens=MAX_TOKENS,
        )

    elif provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not set")
        return ChatOpenAI(
            model=model_id or DEFAULT_MODELS["openai"],
            max_tokens=MAX_TOKENS,
        )

    elif provider == "openrouter":
        if not os.getenv("OPENROUTER_API_KEY"):
            raise ValueError("OPENROUTER_API_KEY not set")
        return ChatOpenAI(
            model=model_id or DEFAULT_MODELS["openrouter"],
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            max_tokens=MAX_TOKENS,
        )

    else:
        raise ValueError(
            f"Unknown provider: {provider}. Use 'anthropic', 'openai', or 'openrouter'"
        )
