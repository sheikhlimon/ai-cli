"""AI model management module"""
import os
from typing import Dict, Optional
import openai
from openai import OpenAI
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
        
        # OpenAI (for models that use OpenAI API format)
        openai_api_key = os.getenv("OPENAI_API_KEY") or config_manager.get_api_key("openai")
        if openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
        else:
            self.openai_client = None
        
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
    
    def get_available_models(self) -> list:
        """Get list of available models based on configured API keys"""
        available = []
        if self.qwen_enabled:
            available.append("qwen")
        if self.claude_client:
            available.append("claude")
        if self.gemini_model:
            available.append("gemini")
        # Add OpenAI models if available
        if self.openai_client:
            available.append("gpt-3.5-turbo")  # More specific naming
            available.append("gpt-4")  # Could support multiple models
        return available
    
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
    
    def openai_model(self, prompt: str, model: str = "gpt-3.5-turbo") -> str:
        """Get response from OpenAI model (e.g., GPT)"""
        if not self.openai_client:
            return "OpenAI API key not configured. Please set OPENAI_API_KEY environment variable."
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling OpenAI model {model}: {str(e)}"
    
    def get_available_models(self) -> list:
        """Get list of available models based on configured API keys and local models"""
        available = []
        if self.qwen_enabled:
            available.append("qwen")
        if self.claude_client:
            available.append("claude")
        if self.gemini_model:
            available.append("gemini")
        # Add OpenAI models if available
        if self.openai_client:
            available.append("gpt-3.5-turbo")  # More specific naming
            available.append("gpt-4")  # Could support multiple models
        # Add Ollama models if available
        if self.ollama_available and self.ollama_models:
            available.extend([f"ollama:{model}" for model in self.ollama_models])
        return available
    
    def compare_models(self, prompt: str) -> Dict[str, str]:
        """Get responses from all available models"""
        responses = {}
        
        # Collect responses from all available models, handling errors gracefully
        if self.qwen_enabled:
            try:
                responses['qwen'] = self.qwen(prompt)
            except Exception as e:
                responses['qwen'] = f"Error getting response from Qwen: {str(e)}"
        
        if self.claude_client:
            try:
                responses['claude'] = self.claude(prompt)
            except Exception as e:
                responses['claude'] = f"Error getting response from Claude: {str(e)}"
        
        if self.gemini_model:
            try:
                responses['gemini'] = self.gemini(prompt)
            except Exception as e:
                responses['gemini'] = f"Error getting response from Gemini: {str(e)}"
            
        # Include a default OpenAI model response if available
        if self.openai_client:
            try:
                responses['gpt-3.5-turbo'] = self.openai_model(prompt, "gpt-3.5-turbo")
            except Exception as e:
                responses['gpt-3.5-turbo'] = f"Error getting response from GPT-3.5-Turbo: {str(e)}"
        
        # Include Ollama models if available
        if self.ollama_available and self.ollama_models:
            # Use the first available Ollama model for comparison
            default_ollama_model = self.ollama_models[0]  # Use first model as default for comparison
            try:
                responses[f'ollama:{default_ollama_model}'] = self.ollama_model(prompt, default_ollama_model)
            except Exception as e:
                responses[f'ollama:{default_ollama_model}'] = f"Error getting response from Ollama {default_ollama_model}: {str(e)}"
            
        return responses