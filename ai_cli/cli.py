"""Main CLI module for the AI model manager"""
import typer
import os
import sys
import tty
import termios
from dotenv import load_dotenv
from typing import Optional, List, Tuple
from .models import AIModelManager
from .config import ConfigManager

load_dotenv()

app = typer.Typer(
    name="ai-cli",
    help="Unified interface for AI models and CLI tools",
    add_completion=False,  # Disable shell completion options
    no_args_is_help=False  # Allow running without args
)


def select_option(options: List[Tuple[str, str]], title: str = "Select an option:") -> Optional[Tuple[str, str]]:
    """Interactive selection with arrow keys and vim motions (j/k)"""
    if not options:
        return None
    
    current = 0
    
    def clear_screen():
        """Clear screen properly"""
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()
    
    def hide_cursor():
        """Hide terminal cursor"""
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
    
    def show_cursor():
        """Show terminal cursor"""
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
    
    def render():
        """Render the selection menu"""
        clear_screen()
        sys.stdout.write(f"\r\n{title}\r\n")
        sys.stdout.write("  ↑/↓ or j/k to navigate • Enter to select • q/ESC to quit\r\n\r\n")
        
        for idx, (display, _) in enumerate(options):
            if idx == current:
                # Selected item with colored indicator and bold text
                sys.stdout.write(f"  \033[1;36m>\033[0m \033[1m{display}\033[0m\r\n")
            else:
                # Unselected item with dimmed text
                sys.stdout.write(f"    \033[2m{display}\033[0m\r\n")
        sys.stdout.flush()
    
    # Check if stdin is a terminal
    if not sys.stdin.isatty():
        typer.echo("Error: Interactive mode requires a terminal")
        return None
    
    # Save terminal settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    try:
        tty.setraw(fd)
        hide_cursor()
        render()
        
        while True:
            ch = sys.stdin.read(1)
            
            # Handle escape sequences (arrow keys)
            if ch == '\x1b':
                next1 = sys.stdin.read(1)
                if next1 == '[':
                    next2 = sys.stdin.read(1)
                    if next2 == 'A':  # Up arrow
                        current = (current - 1) % len(options)
                        render()
                    elif next2 == 'B':  # Down arrow
                        current = (current + 1) % len(options)
                        render()
                else:
                    # ESC pressed (quit)
                    clear_screen()
                    show_cursor()
                    return None
            elif ch in ('j', 'J'):  # Vim down
                current = (current + 1) % len(options)
                render()
            elif ch in ('k', 'K'):  # Vim up
                current = (current - 1) % len(options)
                render()
            elif ch in ('q', 'Q'):  # Quit
                clear_screen()
                show_cursor()
                return None
            elif ch in ('\r', '\n'):  # Enter
                clear_screen()
                show_cursor()
                return options[current]
            elif ch == '\x03':  # Ctrl+C
                clear_screen()
                show_cursor()
                raise KeyboardInterrupt
    
    finally:
        show_cursor()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def tools():
    """Launch interactive AI tool selector (internal function)"""
    import subprocess
    
    manager = AIModelManager()
    resources = manager.get_available_resources()
    
    # Build options list
    options = []
    for model in resources["models"]:
        label = f"{model[7:]} (Ollama)" if model.startswith("ollama:") else f"{model} (Cloud)"
        options.append((label, f"model:{model}"))
    
    for tool in resources["cli_tools"]:
        options.append((f"{tool} (CLI)", f"tool:{tool}"))
    
    # Check if any tools available
    if not options:
        typer.echo("No AI tools found!\n")
        typer.echo("Setup:")
        typer.echo("  • Cloud models: ai-cli config -s provider=key")
        typer.echo("  • Local models: Install Ollama (https://ollama.ai)")
        typer.echo("  • CLI tools: Will be auto-detected from PATH")
        
        # Show which providers are configured vs not configured
        status = manager.get_available_models()
        if status:
            typer.echo(f"\nAvailable models: {', '.join(status)}")
        else:
            typer.echo("\nNo models currently available.")
            typer.echo("Configure at least one of: claude, gemini, qwen, or install Ollama")
        
        raise typer.Exit(code=1)
    
    # Display available models before selection
    cloud_models = [model for model in resources["models"] if not model.startswith("ollama:")]
    ollama_models = [model[7:] for model in resources["models"] if model.startswith("ollama:")]
    cli_tools = resources["cli_tools"]
    
    if cloud_models or ollama_models or cli_tools:
        typer.echo("Available resources:")
        if cloud_models:
            typer.echo(f"  Cloud models: {', '.join(cloud_models)}")
        if ollama_models:
            typer.echo(f"  Ollama models: {', '.join(ollama_models)}")
        if cli_tools:
            typer.echo(f"  CLI tools: {', '.join(cli_tools)}")
        typer.echo()
    
    # Get user selection
    try:
        result = select_option(options, "Select AI Tool:")
        if not result:
            typer.echo("\nCancelled.")
            return
        _, resource_info = result
    except KeyboardInterrupt:
        typer.echo("\nCancelled.")
        return
    
    # Handle selection
    resource_type, resource_name = resource_info.split(":", 1)
    
    if resource_type == "model":
        _run_chat_session(manager, resource_name)
    elif resource_type == "tool":
        _run_cli_tool(resource_name)

def _run_chat_session(manager: AIModelManager, model_name: str):
    """Run interactive chat session with a model"""
    typer.echo(f"\n💬 Chat session: {model_name}")
    typer.echo("Type 'exit', 'quit', or 'q' to end\n")
    
    while True:
        try:
            user_input = typer.prompt("You", prompt_suffix=": ")
            if user_input.lower() in ['exit', 'quit', 'q']:
                typer.echo("Goodbye! 👋")
                break
            
            response = manager.chat(model_name, user_input)
            typer.echo(f"{model_name}: {response}\n")
            
        except KeyboardInterrupt:
            typer.echo("\n\nSession ended.")
            break
        except Exception as e:
            typer.echo(f"❌ Error: {str(e)}")
            break

def _run_cli_tool(tool_name: str):
    """Launch external CLI tool"""
    import subprocess
    
    try:
        subprocess.run([tool_name])
    except FileNotFoundError:
        typer.echo(f"❌ '{tool_name}' not found in PATH")
        typer.echo(f"Try: ai-cli config -a {tool_name}")
    except KeyboardInterrupt:
        typer.echo("\n")
    except Exception as e:
        typer.echo(f"❌ Error running {tool_name}: {str(e)}")

def config(
    ctx: typer.Context,
    set_key: Optional[str] = typer.Option(None, "--set", "-s", help="Set API key (provider=key)"),
    add_tool: Optional[str] = typer.Option(None, "--add", "-a", help="Add custom tool"),
    remove_tool: Optional[str] = typer.Option(None, "--remove", "-r", help="Remove custom tool"),
    list_status: bool = typer.Option(False, "--list", "-l", help="Show configuration"),
    list_tools: bool = typer.Option(False, "--tools", "-t", help="Show custom tools"),
    show_models: bool = typer.Option(None, "--models", "-m", help="Show available models"),
    reset: bool = typer.Option(False, "--reset", help="Reset all")
):
    """Configuration options"""
    config_manager = ConfigManager()
    
    if reset:
        typer.confirm("Reset all configuration?", abort=True)
        config_file = config_manager.config_dir / "config.json"
        if config_file.exists():
            config_file.unlink()
            typer.echo("Configuration reset.")
        else:
            typer.echo("No configuration file found.")
        return
    
    if set_key:
        if '=' not in set_key:
            typer.echo("Format: provider=key")
            raise typer.Exit(code=1)
        
        provider, key = set_key.split('=', 1)
        provider = provider.strip().lower()
        key = key.strip()
        
        if provider not in ['claude', 'gemini', 'qwen']:
            typer.echo(f"Unsupported: {provider}. Use: claude, gemini, qwen")
            raise typer.Exit(code=1)
        
        if config_manager.set_api_key(provider, key):
            typer.echo(f"{provider.upper()} key set.")
        else:
            typer.echo(f"Failed to set {provider.upper()} key.")
        return
    
    if add_tool:
        import shutil
        if not shutil.which(add_tool):
            typer.echo(f"Warning: '{add_tool}' not found in PATH")
        
        if config_manager.add_custom_cli_tool(add_tool):
            typer.echo(f"✓ Added '{add_tool}' to custom CLI tools")
        else:
            typer.echo(f"✗ Failed to add '{add_tool}'")
        return
    
    if remove_tool:
        if config_manager.remove_custom_cli_tool(remove_tool):
            typer.echo(f"✓ Removed '{remove_tool}' from custom CLI tools")
        else:
            typer.echo(f"✗ Tool '{remove_tool}' not found in custom list")
        return
    
    if list_tools:
        custom = config_manager.get_custom_cli_tools()
        excluded = config_manager.get_excluded_cli_tools()
        
        typer.echo("Custom CLI Tools:")
        if custom:
            for tool in custom:
                typer.echo(f"  + {tool}")
        else:
            typer.echo("  (none)")
        
        typer.echo("\nExcluded CLI Tools:")
        if excluded:
            for tool in excluded:
                typer.echo(f"  - {tool}")
        else:
            typer.echo("  (none)")
        return
    
    # Show available models if requested
    if show_models:
        manager = AIModelManager()
        available_models = manager.get_available_models()
        
        typer.echo("Available AI Models:")
        if available_models:
            cloud_models = [model for model in available_models if not model.startswith("ollama:")]
            ollama_models = [model[7:] for model in available_models if model.startswith("ollama:")]
            
            if cloud_models:
                typer.echo(f"  Cloud models: {', '.join(cloud_models)}")
            if ollama_models:
                typer.echo(f"  Ollama models: {', '.join(ollama_models)}")
            if not cloud_models and not ollama_models:
                typer.echo("  (none)")
        else:
            typer.echo("  No models available")
            typer.echo("\nTo configure cloud models:")
            typer.echo("  • ai-cli -s claude=your_api_key")
            typer.echo("  • ai-cli -s gemini=your_api_key") 
            typer.echo("  • ai-cli -s qwen=your_api_key")
            typer.echo("\nTo use local models: Install Ollama (https://ollama.ai)")
        return
    
    if list_status or not (set_key or add_tool):
        status = config_manager.get_providers_status()
        typer.echo("Configuration:")
        
        for provider, info in status.items():
            status_text = "SET" if info['configured'] else "NOT SET"
            typer.echo(f"  {provider.upper()}: {status_text}")
            if info['configured']:
                typer.echo(f"    Preview: {info['key_preview']}")

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    set_key: Optional[str] = typer.Option(None, "--set", "-s", help="Set API key (provider=key)"),
    add_tool: Optional[str] = typer.Option(None, "--add", "-a", help="Add custom tool"),
    remove_tool: Optional[str] = typer.Option(None, "--remove", "-r", help="Remove custom tool"),
    list_status: bool = typer.Option(False, "--list", "-l", help="Show configuration"),
    list_tools: bool = typer.Option(False, "--tools", "-t", help="Show custom tools"),
    show_models: bool = typer.Option(None, "--models", "-m", help="Show available models"),
    reset: bool = typer.Option(False, "--reset", help="Reset all")
):
    """
    Unified interface for AI models and CLI tools.
    
    Run without options to launch interactive tool selector.
    """
    # Handle config options if provided
    if any([set_key, add_tool, remove_tool, list_status, list_tools, show_models, reset]):
        config(ctx, set_key, add_tool, remove_tool, list_status, list_tools, show_models, reset)
    elif ctx.invoked_subcommand is None:
        # Launch tool selector by default
        tools()

if __name__ == "__main__":
    app()