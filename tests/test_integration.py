"""Integration test for the AI CLI tool with a simple scenario"""
import pytest
from typer.testing import CliRunner
from ai_cli.cli import app

runner = CliRunner()

@pytest.mark.integration
def test_basic_cli_workflow():
    """Test basic CLI commands and workflow"""
    # Test help command
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Unified interface for AI models and CLI tools" in result.stdout
    
    # Test list command
    result = runner.invoke(app, ["--list"])
    assert result.exit_code == 0
    
    # Test that options are frontlined
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--set" in result.stdout
    assert "--add" in result.stdout


@pytest.mark.integration
def test_config_workflow():
    """Test configuration management workflow"""
    # Test listing configuration
    result = runner.invoke(app, ["--list"])
    assert result.exit_code == 0
    
    # Should show configuration keys
    assert "Configuration:" in result.stdout or "CLAUDE" in result.stdout or "GEMINI" in result.stdout or "QWEN" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__])