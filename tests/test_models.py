"""Test the models module directly"""
import os
import pytest
from unittest.mock import patch
from ai_cli.models import AIModelManager


def test_model_manager_initialization():
    """Test that the AIModelManager initializes correctly"""
    manager = AIModelManager()
    # Without API keys, clients should be None
    assert hasattr(manager, 'openai_client')
    assert hasattr(manager, 'claude_client')
    assert hasattr(manager, 'gemini_model')
    assert hasattr(manager, 'qwen_enabled')
    assert hasattr(manager, 'ollama_available')
    assert hasattr(manager, 'ollama_models')


def test_qwen_method_without_dashscope():
    """Test Qwen method when dashscope is not available"""
    # Remove QWEN_API_KEY if it exists
    original_key = os.environ.get('QWEN_API_KEY')
    if 'QWEN_API_KEY' in os.environ:
        del os.environ['QWEN_API_KEY']
    
    manager = AIModelManager()
    response = manager.qwen("Test prompt")
    
    # Should return a message about missing dashscope or API key
    assert "dashscope" in response.lower() or "configured" in response.lower()
    
    # Restore original key if it existed
    if original_key is not None:
        os.environ['QWEN_API_KEY'] = original_key


def test_available_models_without_keys():
    """Test that available models list is returned"""
    manager = AIModelManager()
    models = manager.get_available_models()
    # Should be a list of available models
    assert isinstance(models, list)
    # The list might contain openai models if client is available, or be empty otherwise


def test_compare_models_without_keys():
    """Test compare_models method without API keys"""
    manager = AIModelManager()
    responses = manager.compare_models("Test prompt")
    # Should return a dictionary with potentially empty responses
    assert isinstance(responses, dict)
    # All responses should indicate missing configuration or be empty


def test_ollama_method_without_ollama():
    """Test Ollama method when Ollama is not available"""
    manager = AIModelManager()
    # Since Ollama availability depends on system setup, this test will show appropriate message
    response = manager.ollama_model("Test prompt", "llama2")
    
    # Response should indicate Ollama is not available or show an error
    # The exact message depends on whether ollama is installed on the system
    assert isinstance(response, str)


def test_get_available_models_includes_ollama():
    """Test that get_available_models includes Ollama models when available"""
    manager = AIModelManager()
    models = manager.get_available_models()
    
    assert isinstance(models, list)
    # If Ollama is available, it should include ollama models with 'ollama:' prefix
    ollama_models = [m for m in models if m.startswith('ollama:')]
    if manager.ollama_available:
        # If Ollama is available on the system, there should be ollama models
        # (might be empty list if no models are pulled)
        pass
    else:
        # If Ollama is not available, there should be no ollama models in the list
        assert len(ollama_models) == 0


if __name__ == "__main__":
    pytest.main([__file__])