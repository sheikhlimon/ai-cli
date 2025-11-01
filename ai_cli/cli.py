"""Main CLI module for the AI model manager"""
import typer
import os
from dotenv import load_dotenv
from .models import AIModelManager

load_dotenv()

app = typer.Typer(name="AI CLI", help="A CLI tool for managing multiple AI models")

@app.command()
def list():
    """List all available AI models"""
    manager = AIModelManager()
    models = manager.get_available_models()
    for model in models:
        print(model)

@app.command()
def qwen(prompt: str):
    """Use Qwen model with the given prompt"""
    manager = AIModelManager()
    response = manager.qwen(prompt)
    print(response)

@app.command()
def claude(prompt: str):
    """Use Claude model with the given prompt"""
    manager = AIModelManager()
    response = manager.claude(prompt)
    print(response)

@app.command()
def gemini(prompt: str):
    """Use Gemini model with the given prompt"""
    manager = AIModelManager()
    response = manager.gemini(prompt)
    print(response)

@app.command()
def compare(prompt: str):
    """Compare responses from all available models"""
    manager = AIModelManager()
    responses = manager.compare_models(prompt)
    for model, response in responses.items():
        print(f"\n--- {model.upper()} ---")
        print(response)

@app.command()
def config():
    """Manage configuration"""
    typer.echo("Configuration management coming soon...")

if __name__ == "__main__":
    app()