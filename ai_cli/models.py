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
        """Auto-detect AI CLI tools on the system"""
        import shutil
        from pathlib import Path
        from .config import ConfigManager
        
        config_manager = ConfigManager()
        available_clis = []
        seen = set()
        
        # Exclude common system tools
        excluded = set(config_manager.get_excluded_cli_tools())
        excluded.update(['ai-cli', 'node', 'npm', 'npx', 'python', 'python3', 'pip', 'bash', 'sh', 'corepack', 'yarn', 'pnpm'])
        
        # Scan all PATH directories
        path_dirs = os.environ.get('PATH', '').split(os.pathsep)
        
        for path_dir in path_dirs:
            try:
                path_obj = Path(path_dir)
                if not path_obj.exists() or not path_obj.is_dir():
                    continue
                
                for item in path_obj.iterdir():
                    if not item.is_file() or item.name in excluded or item.name in seen:
                        continue
                    
                    # Check if executable
                    if not os.access(str(item), os.X_OK):
                        continue
                    
                    name = item.name
                    name_lower = name.lower()
                    
                    # Match AI tool patterns
                    # 1. Exact matches for specific AI tools
                    if name_lower in ['ollama', 'aider', 'droid', 'gemini', 'claude', 'qwen', 'anthropic', 
                                      'copilot', 'cody', 'cursor', 'fabric', 'ai', 'llm', 'gpt', 
                                      'chat', 'aichat', 'sgpt', 'chatgpt', 'amp']:
                        available_clis.append(name)
                        seen.add(name)
                    # 2. Has AI-related prefixes
                    elif any(name_lower.startswith(x) for x in ['ai-', 'chatgpt-', 'gpt-', 'llm-', 'gemini-', 'claude-', 'qwen-', 'openai-']):
                        available_clis.append(name)
                        seen.add(name)
                    # 3. Has AI-related suffixes (but not system tools)
                    elif any(name_lower.endswith(x) for x in ['-ai', '-gpt', '-llm']) and not any(y in name_lower for y in ['android', 'deploy', 'hypr', 'gnu', 'omarchy']):
                        available_clis.append(name)
                        seen.add(name)
                        
            except (PermissionError, OSError):
                continue
        
        # Add custom CLI tools from config
        custom_tools = config_manager.get_custom_cli_tools()
        for tool in custom_tools:
            if tool not in excluded and tool not in seen and shutil.which(tool):
                available_clis.append(tool)
                seen.add(tool)
        
        # Track Node.js-based tools that are currently available
        node_tool_indicators = ['node_modules', 'package.json', 'npm', 'yarn', 'pnpm']
        current_node_tools = [tool for tool in available_clis 
                             if any(indicator in tool.lower() for indicator in ['claude', 'gemini', 'chatgpt', 'gpt', 'ai', 'ollama'] + node_tool_indicators)
                             and shutil.which(tool)]  # Confirm they're executable
        config_manager.set_known_node_tools(current_node_tools)
        
        return sorted(available_clis)
    
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