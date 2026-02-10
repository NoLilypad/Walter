"""Configuration management with backward compatibility for v1 configs."""
import os
import sys
from typing import Any, Optional
import importlib.resources

# Lazy imports
_yaml = None
_platformdirs = None


def get_yaml():
    """Lazy load PyYAML."""
    global _yaml
    if _yaml is None:
        import yaml
        _yaml = yaml
    return _yaml


def get_platformdirs():
    """Lazy load platformdirs."""
    global _platformdirs
    if _platformdirs is None:
        import platformdirs
        _platformdirs = platformdirs
    return _platformdirs


# Default configuration for v2.0
DEFAULT_CONFIG = {
    "provider": "ollama",
    "editor": "nano",
    "stream": True,
    "ollama": {
        "model": "llama3.2:3b",
        "temperature": 0.2,
        "url": "http://localhost:11434"
    },
    "gemini": {
        "model": "gemini-2.0-flash",
        "api_key": ""
    },
    "mistral": {
        "model": "codestral-latest",
        "api_key": ""
    }
}


class Config:
    """Configuration manager with v1 compatibility."""
    
    def __init__(self, app_name: str = "walter"):
        self.app_name = app_name
        platformdirs = get_platformdirs()
        self.config_dir = platformdirs.user_config_dir(app_name)
        self.config_path = os.path.join(self.config_dir, "config.yaml")
        self.prompt_path = os.path.join(self.config_dir, "prompt.md")
        self._config: dict = {}
        self._prompt: str = ""
        self._load()
    
    def _load(self):
        """Load or create configuration."""
        os.makedirs(self.config_dir, exist_ok=True)
        
        if os.path.exists(self.config_path):
            self._load_config()
            self._migrate_v1_config()
        else:
            self._create_default()
        
        self._load_prompt()
    
    def _load_config(self):
        """Load existing config file."""
        yaml = get_yaml()
        try:
            with open(self.config_path, "r") as f:
                self._config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[Walter] Error loading config: {e}")
            self._config = DEFAULT_CONFIG.copy()
    
    def _migrate_v1_config(self):
        """Migrate v1 config format to v2 while preserving user settings."""
        changed = False
        
        # Ensure all provider sections exist
        for provider in ["ollama", "gemini", "mistral"]:
            if provider not in self._config:
                self._config[provider] = DEFAULT_CONFIG[provider].copy()
                changed = True
        
        # Fix old ollama URL format (remove /api/chat if present)
        if "ollama" in self._config:
            url = self._config["ollama"].get("url", "")
            if "/api/chat" in url:
                self._config["ollama"]["url"] = url.replace("/api/chat", "")
                changed = True
        
        # Add stream option if missing
        if "stream" not in self._config:
            self._config["stream"] = True
            changed = True
        
        # Save migrated config
        if changed:
            self._save_config()
    
    def _create_default(self):
        """Create default configuration files."""
        yaml = get_yaml()
        
        # Save default config
        self._config = DEFAULT_CONFIG.copy()
        self._save_config()
        
        # Copy default prompt
        try:
            with importlib.resources.files("walter").joinpath("default_prompt.md").open("r") as f:
                default_prompt = f.read()
            with open(self.prompt_path, "w", encoding="utf-8") as f:
                f.write(default_prompt)
        except Exception as e:
            # Fallback prompt if resource not found
            default_prompt = self._get_fallback_prompt()
            with open(self.prompt_path, "w", encoding="utf-8") as f:
                f.write(default_prompt)
    
    def _save_config(self):
        """Save current config to file."""
        yaml = get_yaml()
        with open(self.config_path, "w") as f:
            yaml.safe_dump(self._config, f, default_flow_style=False, sort_keys=False)
    
    def _load_prompt(self):
        """Load system prompt from file."""
        if os.path.exists(self.prompt_path):
            try:
                with open(self.prompt_path, "r", encoding="utf-8") as f:
                    self._prompt = f.read()
            except Exception:
                self._prompt = self._get_fallback_prompt()
        else:
            self._prompt = self._get_fallback_prompt()
            with open(self.prompt_path, "w", encoding="utf-8") as f:
                f.write(self._prompt)
    
    def _get_fallback_prompt(self) -> str:
        """Return fallback prompt if default_prompt.md is not available."""
        return """# Role
You are an AI agent that generates CLI commands.

# Mission
Based on this user demand: {user_prompt}

Generate a working CLI command.

# Response format
- No formatting, no markdown, explanation or question, the command should run natively.
- If multiple commands are needed, make it a one-liner with &&
- The command should be the simplest possible.

# Data
User's OS: {os_name}
Current working directory: {cwd}
Files in working directory: {files}
"""
    
    @property
    def config(self) -> dict:
        """Get full config dict."""
        return self._config
    
    @property
    def provider(self) -> str:
        """Get current provider name."""
        return self._config.get("provider", "ollama")
    
    @property
    def editor(self) -> str:
        """Get editor command."""
        return self._config.get("editor") or os.environ.get("EDITOR", "nano")
    
    @property
    def stream(self) -> bool:
        """Whether to use streaming responses."""
        return self._config.get("stream", True)
    
    @property
    def prompt_template(self) -> str:
        """Get prompt template."""
        return self._prompt
    
    def get_config(self) -> dict:
        """Get config dict (v1 compatibility)."""
        return self._config
    
    def get_prompt(self) -> str:
        """Get prompt template (v1 compatibility)."""
        return self._prompt
    
    def build_prompt(self, user_prompt: str) -> str:
        """Build final prompt with context."""
        try:
            os_name = os.uname().sysname
        except AttributeError:
            os_name = sys.platform
        
        cwd = os.getcwd()
        
        try:
            files = ", ".join(os.listdir(cwd)[:50])  # Limit to 50 files
        except Exception:
            files = ""
        
        return self.prompt_template.format(
            user_prompt=user_prompt,
            os_name=os_name,
            cwd=cwd,
            files=files
        )

