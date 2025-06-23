import requests
from mistralai import Mistral
import sys

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
        data = {
            "model": ollama_config["model"],
            "messages": prompt.get_history(),
            "stream": False,
            "options": {
                "temperature": ollama_config["temperature"]
            }
        }
        try:
            response = requests.post(ollama_config["url"], json=data, timeout=10)
            response.raise_for_status()
            resp = response.json()
            return resp["message"].get("content", "")
        except requests.RequestException as e:
            print(f"[Walter] API error (Ollama): {e}")
            sys.exit(1)
        except Exception as e:
            print(f"[Walter] Unexpected error (Ollama): {e}")
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


