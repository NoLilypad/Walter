"""Ollama provider with lazy loading."""
from typing import Generator
from .base import BaseProvider


class OllamaProvider(BaseProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self._client = None
        self.model = config.get("model", "llama3.2:3b")
        self.temperature = config.get("temperature", 0.2)
        self.url = config.get("url", "http://localhost:11434").replace("/api/chat", "")
    
    @property
    def client(self):
        """Lazy load ollama client."""
        if self._client is None:
            from ollama import Client
            self._client = Client(host=self.url)
        return self._client
    
    @property
    def name(self) -> str:
        return "Ollama"
    
    def ask(self, messages: list[dict]) -> str:
        """Send messages and get complete response."""
        response = self.client.chat(
            model=self.model,
            messages=messages,
            options={"temperature": self.temperature}
        )
        return response["message"]["content"]
    
    def stream(self, messages: list[dict]) -> Generator[str, None, None]:
        """Stream response tokens."""
        response = self.client.chat(
            model=self.model,
            messages=messages,
            options={"temperature": self.temperature},
            stream=True
        )
        for chunk in response:
            if chunk.get("message", {}).get("content"):
                yield chunk["message"]["content"]
