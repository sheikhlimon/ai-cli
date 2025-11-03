"""Configuration management for the AI CLI tool"""
import os
import json
from pathlib import Path
from typing import Optional, List, Dict

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
    
    def _load_config(self) -> Dict:
        """Load config from file, return empty dict if not exists or invalid"""
        if not self.config_file.exists():
            return {}
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_config(self, config: Dict) -> bool:
        """Save config to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except IOError:
            return False
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider (env var takes precedence)"""
        env_key = os.getenv(f"{provider.upper()}_API_KEY")
        if env_key:
            return env_key
        
        config = self._load_config()
        return config.get("api_keys", {}).get(provider.lower())
    
    def set_api_key(self, provider: str, key: str) -> bool:
        """Set API key for a specific provider"""
        os.environ[f"{provider.upper()}_API_KEY"] = key
        
        config = self._load_config()
        if "api_keys" not in config:
            config["api_keys"] = {}
        config["api_keys"][provider.lower()] = key
        
        return self._save_config(config)
    
    def get_providers_status(self) -> dict:
        """Get status of all configured providers"""
        providers = ["claude", "gemini", "qwen"]
        status = {}
        
        for provider in providers:
            key = self.get_api_key(provider)
            status[provider] = {
                "configured": bool(key and key.strip()),
                "key_preview": f"{key[:4]}..." if key and len(key) > 4 else "Not set"
            }
        
        return status
    
    def get_custom_cli_tools(self) -> List[str]:
        """Get list of custom CLI tools from config"""
        return self._load_config().get("custom_cli_tools", [])
    
    def get_excluded_cli_tools(self) -> List[str]:
        """Get list of excluded CLI tools from config"""
        return self._load_config().get("excluded_cli_tools", [])
    
    def add_custom_cli_tool(self, tool: str) -> bool:
        """Add a custom CLI tool to config"""
        config = self._load_config()
        
        if "custom_cli_tools" not in config:
            config["custom_cli_tools"] = []
        
        if tool not in config["custom_cli_tools"]:
            config["custom_cli_tools"].append(tool)
            return self._save_config(config)
        
        return True  # Already exists
    
    def remove_custom_cli_tool(self, tool: str) -> bool:
        """Remove a custom CLI tool from config"""
        config = self._load_config()
        
        if "custom_cli_tools" in config and tool in config["custom_cli_tools"]:
            config["custom_cli_tools"].remove(tool)
            return self._save_config(config)
        
        return False
    
    def get_known_node_tools(self) -> List[str]:
        """Get list of known Node.js-based CLI tools that might disappear across versions"""
        return self._load_config().get("known_node_tools", [])
    
    def set_known_node_tools(self, tools: List[str]) -> bool:
        """Store known Node.js-based CLI tools for reference"""
        config = self._load_config()
        config["known_node_tools"] = list(set(tools))  # Remove duplicates
        return self._save_config(config)