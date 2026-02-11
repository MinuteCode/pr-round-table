"""
Model configuration for the code review tool.

Supports three providers:
- Anthropic Claude (ANTHROPIC_API_KEY)
- OpenAI GPT (OPENAI_API_KEY)
- OpenRouter (OPENROUTER_API_KEY)
"""

import os
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.models.openrouter import OpenRouter

# Default models for each provider
DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-4-20250514",
    "openai": "gpt-4o",
    "openrouter": "anthropic/claude-sonnet-4",  # Can use any model on OpenRouter
}

MAX_TOKENS = 16384


def get_model(provider: str = None, model_id: str = None):
    """
    Return model based on provider or auto-detect from available API keys.

    Args:
        provider: Force a specific provider ("anthropic", "openai", "openrouter")
        model_id: Override the default model ID for the provider

    Priority when auto-detecting: Anthropic > OpenAI > OpenRouter
    """
    # If provider specified, use it directly
    if provider:
        return _get_model_for_provider(provider, model_id)

    # Auto-detect based on available API keys
    if os.getenv("ANTHROPIC_API_KEY"):
        return Claude(id=model_id or DEFAULT_MODELS["anthropic"], max_tokens=MAX_TOKENS)
    elif os.getenv("OPENAI_API_KEY"):
        return OpenAIChat(id=model_id or DEFAULT_MODELS["openai"], max_tokens=MAX_TOKENS)
    elif os.getenv("OPENROUTER_API_KEY"):
        return OpenRouter(id=model_id or DEFAULT_MODELS["openrouter"], max_tokens=MAX_TOKENS)
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
        return Claude(id=model_id or DEFAULT_MODELS["anthropic"], max_tokens=MAX_TOKENS)

    elif provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not set")
        return OpenAIChat(id=model_id or DEFAULT_MODELS["openai"], max_tokens=MAX_TOKENS)

    elif provider == "openrouter":
        if not os.getenv("OPENROUTER_API_KEY"):
            raise ValueError("OPENROUTER_API_KEY not set")
        return OpenRouter(id=model_id or DEFAULT_MODELS["openrouter"], max_tokens=MAX_TOKENS)

    else:
        raise ValueError(
            f"Unknown provider: {provider}. Use 'anthropic', 'openai', or 'openrouter'"
        )
