"""Main CLI module for the AI model manager"""
import typer
import os
from dotenv import load_dotenv
from typing import Optional
from .models import AIModelManager

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
def config(set_key: Optional[str] = typer.Option(None, "--set", "-s", help="Set a configuration value (e.g., api-key)")):
    """Manage configuration"""
    if set_key:
        typer.echo(f"Setting {set_key}...")
        # Implementation for setting config values will go here
    else:
        # Show current configuration status
        manager = AIModelManager()
        models = manager.get_available_models()
        typer.echo("Current configuration status:")
        typer.echo(f"Available models: {models if models else 'None configured'}")
        
        # Check which API keys are set
        api_keys_status = {
            "OpenAI": "SET" if os.getenv("OPENAI_API_KEY") else "NOT SET",
            "Claude": "SET" if os.getenv("CLAUDE_API_KEY") else "NOT SET", 
            "Gemini": "SET" if os.getenv("GEMINI_API_KEY") else "NOT SET"
        }
        for service, status in api_keys_status.items():
            typer.echo(f"  {service} API key: {status}")

if __name__ == "__main__":
    app()