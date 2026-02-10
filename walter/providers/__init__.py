"""Lazy-loaded LLM providers."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import BaseProvider
    from .ollama import OllamaProvider
    from .gemini import GeminiProvider
    from .mistral import MistralProvider

_providers = {}

def get_provider(name: str, config: dict) -> "BaseProvider":
    """Lazy load and return provider instance."""
    if name not in _providers:
        if name == "ollama":
            from .ollama import OllamaProvider
            _providers[name] = OllamaProvider(config.get("ollama", {}))
        elif name == "gemini":
            from .gemini import GeminiProvider
            _providers[name] = GeminiProvider(config.get("gemini", {}))
        elif name == "mistral":
            from .mistral import MistralProvider
            _providers[name] = MistralProvider(config.get("mistral", {}))
        else:
            raise ValueError(f"Unknown provider: {name}")
    return _providers[name]

def list_providers() -> list[str]:
    """List available provider names."""
    return ["ollama", "gemini", "mistral"]
