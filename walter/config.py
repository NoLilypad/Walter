import os
import yaml
import platformdirs 
import importlib.resources
import sys

class Config:
    def __init__(self):
        self.app_name = "walter"
        self.config_dir = platformdirs.user_config_dir(self.app_name)
        self.config_path = os.path.join(self.config_dir, "config.yaml")
        self.prompt_path = os.path.join(self.config_dir, "prompt.md")
        self.config = {}
        self.prompt = ""
        # Loads config at init
        self.load_or_create_config()

    def load_or_create_config(self):
        try:
            if os.path.exists(self.config_path):
                self.load_config()
                self.load_prompt()
            else:
                self.create_default_config()
                self.load_config()
                self.load_prompt()
        except Exception as e:
            print(f"[Walter] Error loading or creating config: {e}")
            sys.exit(1)

    def create_default_config(self):
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with importlib.resources.files("walter").joinpath("default_config.yaml").open("r") as f:
                default_config = yaml.safe_load(f)
            with open(self.config_path, "w") as f:
                yaml.safe_dump(default_config, f, default_flow_style=False)
            with importlib.resources.files("walter").joinpath("default_prompt.md").open("r") as f:
                default_prompt = f.read()
            with open(self.prompt_path, "w", encoding="utf") as f:
                f.write(default_prompt)
        except Exception as e:
            print(f"[Walter] Error creating default config: {e}")
            sys.exit(1)

    def load_config(self):
        try:
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            print(f"[Walter] Error loading config: {e}")
            sys.exit(1)

    def load_prompt(self):
        try:
            with open(self.prompt_path, "r", encoding="utf8") as f:
                self.prompt = f.read()
        except Exception as e:
            print(f"[Walter] Error loading prompt: {e}")
            sys.exit(1)

    def get_config(self):
        return self.config
    
    def get_prompt(self):
        return self.prompt
