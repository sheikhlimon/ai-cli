"""AI model management module"""
import os
from typing import Dict, Optional
import anthropic
import google.generativeai as genai
import subprocess
import json
# Import for Qwen if available
try:
    import dashscope
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False

class AIModelManager:
    def __init__(self):
        # Initialize API clients
        self._setup_apis()
    
    def _setup_apis(self):
        """Set up API clients for different AI models"""
        # Get API keys from environment or config
        from .config import ConfigManager
        config_manager = ConfigManager()
        
        # Anthropic (for Claude)
        claude_api_key = os.getenv("CLAUDE_API_KEY") or config_manager.get_api_key("claude")
        if claude_api_key:
            self.claude_client = anthropic.Anthropic(api_key=claude_api_key)
        else:
            self.claude_client = None
            
        # Google (for Gemini)
        gemini_api_key = os.getenv("GEMINI_API_KEY") or config_manager.get_api_key("gemini")
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        else:
            self.gemini_model = None
            
        # Qwen/Tongyi (using dashscope)
        qwen_api_key = os.getenv("QWEN_API_KEY") or config_manager.get_api_key("qwen")
        if qwen_api_key and DASHSCOPE_AVAILABLE:
            dashscope.api_key = qwen_api_key
            self.qwen_enabled = True
        else:
            self.qwen_enabled = False
            
        # Ollama local models
        self.ollama_available = self._check_ollama_availability()
        if self.ollama_available:
            self.ollama_models = self._get_ollama_models()
        else:
            self.ollama_models = []
            
        # Available AI CLI tools
        self.available_cli_tools = self._check_cli_availability()

    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is available on the system"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
            # Ollama is not installed or not running
            return False

    def _get_ollama_models(self) -> list:
        """Get list of locally available Ollama models"""
        if not self.ollama_available:
            return []
        
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                # Skip header line and parse model names
                models = []
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        # Extract model name from ollama list output format
                        model_name = line.split()[0]  # First column is model name
                        if model_name:
                            models.append(model_name)
                return models
            return []
        except Exception:
            return []

    def _check_cli_availability(self) -> list:
        """
        Auto-detect AI CLI tools on the system by scanning PATH directories.
        
        Detection strategy:
        1. Scans all PATH directories for executable files
        2. Matches tools against configurable patterns (exact names, prefixes, suffixes)
        3. Verifies tools are actually in current PATH (handles Node.js version switches)
        4. Adds custom tools from config
        5. Tracks Node.js-based tools for environment change detection
        
        Returns:
            Sorted list of available AI CLI tool names
            
        Edge cases handled:
        - Node.js version changes: Uses shutil.which() to verify PATH accessibility
        - Permission errors: Silently skips inaccessible directories
        - Symlinks and broken links: Checked via os.access() and shutil.which()
        - Duplicate tool names: Tracked via 'seen' set
        - Custom vs auto-detected conflicts: Custom tools added after auto-detection
        """
        import shutil
        from pathlib import Path
        from .config import ConfigManager
        
        config_manager = ConfigManager()
        candidates = []
        seen = set()
        
        excluded = set(config_manager.get_default_excluded_tools())
        excluded.update(config_manager.get_excluded_cli_tools())
        
        patterns = config_manager.get_ai_tool_patterns()
        exact_matches = set(patterns.get("exact_matches", []))
        prefixes = patterns.get("prefixes", [])
        suffixes = patterns.get("suffixes", [])
        suffix_exclusions = patterns.get("suffix_exclusions", [])
        
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        
        for path_dir in path_dirs:
            try:
                path_obj = Path(path_dir)
                if not path_obj.exists() or not path_obj.is_dir():
                    continue
                
                for item in path_obj.iterdir():
                    if not item.is_file() or item.name in seen or item.name in excluded:
                        continue
                    
                    if not os.access(str(item), os.X_OK):
                        continue
                    
                    name = item.name
                    name_lower = name.lower()
                    
                    if name_lower in exact_matches:
                        candidates.append(name)
                        seen.add(name)
                    elif any(name_lower.startswith(prefix) for prefix in prefixes):
                        candidates.append(name)
                        seen.add(name)
                    elif (any(name_lower.endswith(suffix) for suffix in suffixes) and 
                          not any(exclusion in name_lower for exclusion in suffix_exclusions)):
                        candidates.append(name)
                        seen.add(name)
                        
            except (PermissionError, OSError):
                continue
        
        custom_tools = config_manager.get_custom_cli_tools()
        for tool in custom_tools:
            if tool not in excluded and tool not in seen:
                candidates.append(tool)
                seen.add(tool)
        
        # Verify tools are in current PATH (handles Node.js version switches)
        available_tools = [tool for tool in candidates if shutil.which(tool)]
        
        self._track_node_tools(available_tools, config_manager)
        
        return sorted(available_tools)
    
    def _track_node_tools(self, tools: list, config_manager) -> None:
        """Track Node.js-based tools that may change across version switches"""
        node_indicators = ['node_modules', 'npm', 'yarn', 'pnpm']
        npm_ai_tools = ['claude', 'gemini', 'chatgpt', 'gpt', 'ai', 'llm']
        
        node_tools = [
            tool for tool in tools
            if any(indicator in tool.lower() for indicator in node_indicators + npm_ai_tools)
        ]
        
        if node_tools:
            config_manager.set_known_node_tools(node_tools)
    
    def get_available_models(self) -> list:
        """Get list of available models based on configured API keys and local models"""
        available = []
        
        if self.qwen_enabled:
            available.append("qwen")
        if self.claude_client:
            available.append("claude")
        if self.gemini_model:
            available.append("gemini")
        if self.ollama_available and self.ollama_models:
            available.extend([f"ollama:{model}" for model in self.ollama_models])
            
        return available
    
    def chat(self, model_name: str, prompt: str) -> str:
        """Unified chat interface for all models"""
        if model_name.startswith("ollama:"):
            return self.ollama_model(prompt, model_name[7:])
        elif model_name == "qwen":
            return self.qwen(prompt)
        elif model_name == "claude":
            return self.claude(prompt)
        elif model_name == "gemini":
            return self.gemini(prompt)
        else:
            return f"Unknown model: {model_name}"
    
    def qwen(self, prompt: str) -> str:
        """Get response from Qwen model"""
        if not self.qwen_enabled:
            if not DASHSCOPE_AVAILABLE:
                return "Qwen integration requires the dashscope package. Install it with: pip install dashscope"
            else:
                return "Qwen API key not configured. Please set QWEN_API_KEY environment variable."
        
        try:
            import dashscope
            response = dashscope.ChatCompletion.call(
                model='qwen-max',
                messages=[
                    {'role': 'user', 'content': prompt}
                ]
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content if response.output.choices else "No response from Qwen"
            else:
                return f"Error calling Qwen: {response.code} - {response.message}"
        except Exception as e:
            return f"Error calling Qwen: {str(e)}"
    
    def claude(self, prompt: str) -> str:
        """Get response from Claude model"""
        if not self.claude_client:
            return "Claude API key not configured. Please set CLAUDE_API_KEY environment variable."
        
        try:
            message = self.claude_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error calling Claude: {str(e)}"
    
    def gemini(self, prompt: str) -> str:
        """Get response from Gemini model"""
        if not self.gemini_model:
            return "Gemini API key not configured. Please set GEMINI_API_KEY environment variable."
        
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error calling Gemini: {str(e)}"
    
    def ollama_model(self, prompt: str, model: str = "llama2") -> str:
        """Get response from a local Ollama model"""
        if not self.ollama_available:
            return "Ollama is not available. Please install and start Ollama server."
        
        if model not in self.ollama_models:
            return f"Model '{model}' not available. Available models: {', '.join(self.ollama_models) if self.ollama_models else 'None'}"
        
        try:
            result = subprocess.run([
                'ollama', 'run', model
            ], input=prompt, text=True, capture_output=True, timeout=60)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error calling Ollama model {model}: {result.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return f"Timeout calling Ollama model {model}: Request took too long"
        except Exception as e:
            return f"Error calling Ollama model {model}: {str(e)}"
    
    def get_available_resources(self) -> dict:
        """Get both AI models and CLI tools available on the system"""
        return {
            "models": self.get_available_models(),
            "cli_tools": self.available_cli_tools
        }