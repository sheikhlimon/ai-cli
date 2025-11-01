"""Test the models module directly"""
import os
import pytest
from unittest.mock import patch
from ai_cli.models import AIModelManager


@pytest.mark.unit
def test_model_manager_initialization():
    """Test that the AIModelManager initializes correctly"""
    manager = AIModelManager()
    # Check that manager has expected attributes
    assert hasattr(manager, 'claude_client')
    assert hasattr(manager, 'gemini_model')
    assert hasattr(manager, 'qwen_enabled')
    assert hasattr(manager, 'ollama_available')
    assert hasattr(manager, 'ollama_models')
    assert hasattr(manager, 'available_cli_tools')


@pytest.mark.unit
def test_qwen_method_without_dashscope():
    """Test Qwen method when dashscope is not available"""
    manager = AIModelManager()
    # This should gracefully handle the absence of API key
    assert isinstance(manager.qwen_enabled, bool)


@pytest.mark.unit
def test_available_models_without_keys():
    """Test that available models list is returned"""
    manager = AIModelManager()
    models = manager.get_available_models()
    # Should be a list of available models
    assert isinstance(models, list)


@pytest.mark.unit
def test_get_available_resources():
    """Test get_available_resources returns proper structure"""
    manager = AIModelManager()
    resources = manager.get_available_resources()
    assert isinstance(resources, dict)
    assert "models" in resources
    assert "cli_tools" in resources
    assert isinstance(resources["models"], list)
    assert isinstance(resources["cli_tools"], list)


@pytest.mark.unit
def test_ollama_method_without_ollama():
    """Test Ollama method when Ollama is not available"""
    manager = AIModelManager()
    # Check that ollama_available is a boolean
    assert isinstance(manager.ollama_available, bool)
    assert isinstance(manager.ollama_models, list)


@pytest.mark.unit
def test_get_available_models_includes_ollama():
    """Test that get_available_models includes Ollama models when available"""
    manager = AIModelManager()
    models = manager.get_available_models()
    
    assert isinstance(models, list)
    # If Ollama is available, it should include ollama models with 'ollama:' prefix
    ollama_models = [m for m in models if m.startswith('ollama:')]
    if manager.ollama_available and manager.ollama_models:
        assert len(ollama_models) > 0


@pytest.mark.unit
def test_chat_method_exists():
    """Test that chat method exists"""
    manager = AIModelManager()
    assert hasattr(manager, 'chat')
    assert callable(manager.chat)


if __name__ == "__main__":
    pytest.main([__file__])