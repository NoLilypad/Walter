import os
import sys

from walter.config import Config

class Prompt:
    def __init__(self, user_prompt: str, config: Config):
        self.history = []
        self.user_prompt = user_prompt
        self.config = config
        self.general_prompt = self.config.get_prompt()
        try:
            self.os_name = os.uname().sysname
            self.cwd = os.getcwd()
            self.files = ', '.join(os.listdir(self.cwd))
        except Exception as e:
            print(f"[Walter] Error accessing file system: {e}")
            sys.exit(1)

        self.final_prompt = self.general_prompt.format(user_prompt = user_prompt,
                                                       os_name = self.os_name,
                                                       cwd = self.cwd,
                                                       files = self.files)
        self.add_user_message(self.get_prompt())
    
    def get_prompt(self):
        return self.final_prompt
    
    def add_to_history(self, message: dict):
        self.history.append(message)

    def add_user_message(self, content: str):
        self.history.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        self.history.append({"role": "assistant", "content": content})

    def get_history(self):
        return self.history



