import sys
from ollama import Client as OllamaClient
from mistralai import Mistral

from walter.config import Config
from walter.prompt import Prompt

class Asker:
    def __init__(self, config: Config):
        self.providers = {
            "ollama": self.ollama,
            "mistral": self.mistral
        }
        self.config = config.get_config()
        self.provider = self.config["provider"]
        self.provider_function = self.providers[self.provider]

    def ollama(self, prompt: Prompt):
        print("Asking to ollama")
        ollama_config = self.config["ollama"]
        try:
            client = OllamaClient(host=ollama_config.get("url", "http://localhost:11434"))
            # The ollama Python package expects messages as a list of dicts with 'role' and 'content'
            messages = prompt.get_history()
            # Remove /api/chat from url if present for base host
            base_url = ollama_config["url"].replace("/api/chat", "")
            client = OllamaClient(host=base_url)
            response = client.chat(
                model=ollama_config["model"],
                messages=messages,
                options={"temperature": ollama_config["temperature"]}
            )
            return response['message']['content']
        except Exception as e:
            print(f"[Walter] API error (Ollama): {e}")
            sys.exit(1)

    def mistral(self, prompt: Prompt):
        print("Asking to Mistral AI")
        mistral_config = self.config["mistral"]
        try:
            client = Mistral(api_key=mistral_config["api_key"])
            response = client.chat.complete(
                model = mistral_config["model"],
                messages = prompt.get_history()
            )
            return(response.choices[0].message.content)
        except Exception as e:
            print(f"[Walter] API error (Mistral): {e}")
            sys.exit(1)


