"""Mistral AI provider with lazy loading."""
from typing import Generator
from .base import BaseProvider


class MistralProvider(BaseProvider):
    """Mistral AI provider."""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self._client = None
        self.model = config.get("model", "codestral-latest")
        self.api_key = config.get("api_key", "")
    
    @property
    def client(self):
        """Lazy load Mistral client."""
        if self._client is None:
            from mistralai import Mistral
            self._client = Mistral(api_key=self.api_key)
        return self._client
    
    @property
    def name(self) -> str:
        return "Mistral"
    
    def ask(self, messages: list[dict]) -> str:
        """Send messages and get complete response."""
        response = self.client.chat.complete(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content
    
    def stream(self, messages: list[dict]) -> Generator[str, None, None]:
        """Stream response tokens."""
        response = self.client.chat.stream(
            model=self.model,
            messages=messages
        )
        for event in response:
            if event.data.choices[0].delta.content:
                yield event.data.choices[0].delta.content
