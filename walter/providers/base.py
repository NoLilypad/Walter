"""Base provider interface."""
from abc import ABC, abstractmethod
from typing import Generator


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: dict):
        self.config = config
    
    @abstractmethod
    def ask(self, messages: list[dict]) -> str:
        """Send messages and get response."""
        pass
    
    @abstractmethod
    def stream(self, messages: list[dict]) -> Generator[str, None, None]:
        """Stream response tokens."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider display name."""
        pass
