"""Comprehensive tests for the AI CLI tool"""
import pytest
from typer.testing import CliRunner
from ai_cli.cli import app

runner = CliRunner()

@pytest.mark.unit
def test_help_command():
    """Test the help command"""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "A CLI tool for managing multiple AI models" in result.stdout
    assert "tools" in result.stdout
    assert "config" in result.stdout

@pytest.mark.unit
def test_config_list_command():
    """Test the config --list command"""
    result = runner.invoke(app, ["config", "--list"])
    assert result.exit_code == 0
    # Should show configuration status (even if keys are not set)
    assert "Configuration:" in result.stdout or "CLAUDE" in result.stdout

@pytest.mark.unit
def test_config_command_no_args():
    """Test the config command without arguments"""
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0

@pytest.mark.unit
def test_tools_command_help():
    """Test the tools command help"""
    result = runner.invoke(app, ["tools", "--help"])
    assert result.exit_code == 0
    assert "Interactive selection interface" in result.stdout

@pytest.mark.unit
def test_invalid_command():
    """Test that invalid commands are handled properly"""
    result = runner.invoke(app, ["nonexistent-command"])
    assert result.exit_code != 0

if __name__ == "__main__":
    pytest.main([__file__])