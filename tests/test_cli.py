"""Comprehensive tests for the AI CLI tool"""
import pytest
from typer.testing import CliRunner
from ai_cli.cli import app

runner = CliRunner()

def test_list_command():
    """Test the list command"""
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    # The output should either indicate no models are configured or show available models
    # This is acceptable in both cases
    assert "Available AI models:" in result.stdout or "No AI models are currently configured" in result.stdout

def test_config_command():
    """Test the config command"""
    result = runner.invoke(app, ["config", "--list"])
    assert result.exit_code == 0
    assert "Current configuration status:" in result.stdout

def test_compare_command():
    """Test the compare command with a basic prompt"""
    result = runner.invoke(app, ["compare", "test prompt"])
    assert result.exit_code == 0
    # The response should contain some output even without API keys
    # as the models should return error messages that are handled gracefully

def test_help_command():
    """Test the help command"""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "A CLI tool for managing multiple AI models" in result.stdout
    assert "list" in result.stdout
    assert "qwen" in result.stdout
    assert "claude" in result.stdout
    assert "gemini" in result.stdout
    assert "compare" in result.stdout
    assert "config" in result.stdout
    # Check for new commands
    assert "ollama" in result.stdout
    assert "interactive" in result.stdout

def test_ollama_command():
    """Test the ollama command"""
    result = runner.invoke(app, ["ollama", "test prompt"])
    # This might fail if ollama is not installed, but should not crash
    assert result.exit_code in [0, 1]  # Could return 1 if ollama is not available

def test_openai_model_command():
    """Test the openai-model command"""
    result = runner.invoke(app, ["openai-model", "test prompt"])
    assert result.exit_code == 0
    # Should return an error message about missing API key
    assert "not configured" in result.stdout or "Error" in result.stdout

if __name__ == "__main__":
    pytest.main([__file__])