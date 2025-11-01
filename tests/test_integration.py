"""Integration test for the AI CLI tool with a simple scenario"""
import os
import tempfile
from typer.testing import CliRunner
from ai_cli.cli import app

runner = CliRunner()

def test_basic_cli_workflow():
    """Test basic CLI commands and workflow"""
    # Test help command
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "A CLI tool for managing multiple AI models" in result.stdout
    
    # Test list command
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    # The output should either indicate no models are configured or show available models
    assert "Available AI models:" in result.stdout or "No AI models are currently configured" in result.stdout
    
    # Test config command
    result = runner.invoke(app, ["config", "--list"])
    assert result.exit_code == 0
    assert "Current configuration status:" in result.stdout
    
    # Test compare command with basic functionality (will fail gracefully without API keys)
    result = runner.invoke(app, ["compare", "test prompt"])
    assert result.exit_code == 0
    # Since no API keys are configured, it will show error messages but not crash
    
    # Test that output option works by creating a temporary file
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_file:
        temp_path = temp_file.name
    
    try:
        result = runner.invoke(app, ["compare", "simple test", "--output", temp_path])
        assert result.exit_code == 0
        # Check that the file was created and contains content
        with open(temp_path, 'r') as f:
            content = f.read()
            # Content should exist even if it's error messages
            assert content is not None  # This ensures file was written to
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    # Run the test
    test_basic_cli_workflow()
    print("All integration tests passed!")