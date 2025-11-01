"""Main CLI module for the AI model manager"""
import typer
import os
from dotenv import load_dotenv
from typing import Optional
from .models import AIModelManager
from .config import ConfigManager

load_dotenv()

app = typer.Typer(name="AI CLI", help="A CLI tool for managing multiple AI models")

@app.command()
def list():
    """List all available AI models"""
    manager = AIModelManager()
    models = manager.get_available_models()
    if models:
        typer.echo("Available AI models:")
        for model in models:
            typer.echo(f"  - {model}")
    else:
        typer.echo("No AI models are currently configured. Please check your API keys.")

@app.command()
def qwen(prompt: str = typer.Argument(..., help="The prompt to send to Qwen model"), 
         output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file to save the response")):
    """Use Qwen model with the given prompt"""
    manager = AIModelManager()
    response = manager.qwen(prompt)
    
    if output:
        with open(output, 'w') as f:
            f.write(response)
        typer.echo(f"Response saved to {output}")
    else:
        typer.echo(response)

@app.command()
def claude(prompt: str = typer.Argument(..., help="The prompt to send to Claude model"), 
           output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file to save the response")):
    """Use Claude model with the given prompt"""
    manager = AIModelManager()
    response = manager.claude(prompt)
    
    if output:
        with open(output, 'w') as f:
            f.write(response)
        typer.echo(f"Response saved to {output}")
    else:
        typer.echo(response)

@app.command()
def gemini(prompt: str = typer.Argument(..., help="The prompt to send to Gemini model"), 
           output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file to save the response")):
    """Use Gemini model with the given prompt"""
    manager = AIModelManager()
    response = manager.gemini(prompt)
    
    if output:
        with open(output, 'w') as f:
            f.write(response)
        typer.echo(f"Response saved to {output}")
    else:
        typer.echo(response)

@app.command()
def compare(prompt: str = typer.Argument(..., help="The prompt to send to all models for comparison"), 
            output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file to save the comparison")):
    """Compare responses from all available models"""
    manager = AIModelManager()
    responses = manager.compare_models(prompt)
    
    full_output = ""
    for model, response in responses.items():
        section = f"\n--- {model.upper()} ---\n{response}\n"
        full_output += section
        typer.echo(section)
    
    if output:
        with open(output, 'w') as f:
            f.write(full_output)
        typer.echo(f"Comparison saved to {output}")

@app.command()
def config(
    set_key: Optional[str] = typer.Option(None, "--set", "-s", help="Set an API key in the format 'provider=key'"),
    list_status: bool = typer.Option(False, "--list", "-l", help="List configuration status"),
    reset: bool = typer.Option(False, "--reset", help="Reset all configuration")
):
    """Manage configuration"""
    config_manager = ConfigManager()
    
    if reset:
        typer.confirm("Are you sure you want to reset all configuration?", abort=True)
        config_file = config_manager.config_dir / "config.json"
        if config_file.exists():
            config_file.unlink()
            typer.echo("Configuration reset successfully.")
        else:
            typer.echo("No configuration file found to reset.")
        return
    
    if set_key:
        if '=' not in set_key:
            typer.echo("Please provide the key in the format 'provider=key'")
            raise typer.Exit(code=1)
        
        provider, key = set_key.split('=', 1)
        provider = provider.strip().lower()
        key = key.strip()
        
        if provider not in ['openai', 'claude', 'gemini', 'qwen']:
            typer.echo(f"Unsupported provider: {provider}. Supported: openai, claude, gemini, qwen")
            raise typer.Exit(code=1)
        
        if config_manager.set_api_key(provider, key):
            typer.echo(f"{provider.upper()} API key set successfully!")
        else:
            typer.echo(f"Failed to set {provider.upper()} API key.")
        return
    
    if list_status or not set_key:
        # Show current configuration status
        status = config_manager.get_providers_status()
        typer.echo("Current configuration status:")
        
        for provider, info in status.items():
            status_text = "SET" if info['configured'] else "NOT SET"
            typer.echo(f"  {provider.upper()}: {status_text}")
            if info['configured']:
                typer.echo(f"    Key preview: {info['key_preview']}")

if __name__ == "__main__":
    app()