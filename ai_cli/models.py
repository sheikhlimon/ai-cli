"""AI model management module"""
import os
from typing import Dict, Optional
import openai
from openai import OpenAI
import anthropic
import google.generativeai as genai
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
    
    def get_available_models(self) -> list:
        """Get list of available models based on configured API keys"""
        available = []
        if self.qwen_enabled:
            available.append("qwen")
        if self.claude_client:
            available.append("claude")
        if self.gemini_model:
            available.append("gemini")
        # Add OpenAI models if available (for other OpenAI-compatible models)
        if self.openai_client:
            available.append("openai")  # Generic name for OpenAI models
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
    
    def compare_models(self, prompt: str) -> Dict[str, str]:
        """Get responses from all available models"""
        responses = {}
        
        if self.qwen_enabled:
            responses['qwen'] = self.qwen(prompt)
        
        if self.claude_client:
            responses['claude'] = self.claude(prompt)
        
        if self.gemini_model:
            responses['gemini'] = self.gemini(prompt)
            
        # Include OpenAI models if available (but not duplicating Qwen)
        if self.openai_client and not self.qwen_enabled:
            # For now, just note that OpenAI models are available
            responses['openai'] = "OpenAI models available (specific model not called in compare)"
            
        return responses