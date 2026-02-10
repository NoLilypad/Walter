"""Google Gemini provider with lazy loading."""
from typing import Generator
from .base import BaseProvider


class GeminiProvider(BaseProvider):
    """Google Gemini API provider."""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self._client = None
        self.model = config.get("model", "gemini-2.0-flash")
        self.api_key = config.get("api_key", "")
    
    @property
    def client(self):
        """Lazy load Gemini client."""
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        return self._client
    
    @property
    def name(self) -> str:
        return "Gemini"
    
    def _convert_messages(self, messages: list[dict]) -> list[dict]:
        """Convert standard messages format to Gemini format."""
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        return contents
    
    def ask(self, messages: list[dict]) -> str:
        """Send messages and get complete response."""
        contents = self._convert_messages(messages)
        response = self.client.models.generate_content(
            model=self.model,
            contents=contents
        )
        return response.text
    
    def stream(self, messages: list[dict]) -> Generator[str, None, None]:
        """Stream response tokens."""
        contents = self._convert_messages(messages)
        response = self.client.models.generate_content_stream(
            model=self.model,
            contents=contents
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
