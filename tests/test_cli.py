"""Basic tests for the AI CLI tool"""
import pytest
from typer.testing import CliRunner
from ai_cli.cli import app

runner = CliRunner()

def test_list_command():
    """Test the list command"""
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0

def test_compare_command():
    """Test the compare command with a basic prompt"""
    result = runner.invoke(app, ["compare", "test prompt"])
    assert result.exit_code == 0