"""Configuration management for the AI CLI tool"""
import os
import typer
from pathlib import Path
from typing import Optional

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".ai-cli"
        self.config_file = self.config_dir / "config.json"
        self.env_file = Path.cwd() / ".env"
        if not self.env_file.exists():
            self.env_file = Path.home() / ".env"
        
        self.ensure_config_dir()
    
    def ensure_config_dir(self):
        """Ensure the config directory exists"""
        self.config_dir.mkdir(exist_ok=True)
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider"""
        # Try to get from environment variables first
        env_key = os.getenv(f"{provider.upper()}_API_KEY")
        if env_key:
            return env_key
        
        # Try to get from config file
        if self.config_file.exists():
            import json
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return config.get("api_keys", {}).get(provider.lower())
            except:
                pass
        
        return None
    
    def set_api_key(self, provider: str, key: str) -> bool:
        """Set API key for a specific provider"""
        # Update in environment (runtime only)
        os.environ[f"{provider.upper()}_API_KEY"] = key
        
        # Store in config file
        config = {}
        if self.config_file.exists():
            import json
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            except:
                config = {}
        
        if "api_keys" not in config:
            config["api_keys"] = {}
        
        config["api_keys"][provider.lower()] = key
        
        try:
            import json
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except:
            return False
    
    def get_providers_status(self) -> dict:
        """Get status of all configured providers"""
        providers = ["openai", "claude", "gemini", "qwen"]
        status = {}
        
        for provider in providers:
            key = self.get_api_key(provider)
            status[provider] = {
                "configured": key is not None and key.strip() != "",
                "key_preview": f"{key[:4]}..." if key and len(key) > 4 else "Not set"
            }
        
        return status
    
    def create_env_file(self, openai_key: str = "", claude_key: str = "", 
                        gemini_key: str = "", qwen_key: str = "") -> bool:
        """Create a .env file with API keys"""
        try:
            with open(self.env_file, 'w') as f:
                f.write(f"OPENAI_API_KEY={openai_key}\n")
                f.write(f"CLAUDE_API_KEY={claude_key}\n")
                f.write(f"GEMINI_API_KEY={gemini_key}\n")
                f.write(f"QWEN_API_KEY={qwen_key}\n")
            return True
        except:
            return False