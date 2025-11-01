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

app = typer.Typer(name="AI CLI", help="A CLI tool for managing multiple AI models")


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

@app.command()
def tools():
    """Interactive selection interface to choose and launch available AI CLI tools"""
    import subprocess
    
    manager = AIModelManager()
    resources = manager.get_available_resources()
    
    options = []
    
    # Add models
    for model in resources["models"]:
        if model.startswith("ollama:"):
            display = f"{model[7:]} (Ollama)"
        else:
            display = f"{model} (Cloud)"
        options.append((display, f"model:{model}"))
    
    # Add CLI tools
    for tool in resources["cli_tools"]:
        options.append((f"{tool} (CLI)", f"tool:{tool}"))
    
    if not options:
        typer.echo("No AI models or CLI tools available.")
        typer.echo("  - Cloud: Set API keys (ai-cli config)")
        typer.echo("  - Local: Install Ollama with models")
        raise typer.Exit(code=1)
    
    try:
        result = select_option(options, "Select AI Tool:")
        if not result:
            typer.echo("\nCancelled.")
            return
        
        _, resource_info = result
    except KeyboardInterrupt:
        typer.echo("\nCancelled.")
        return
    
    if resource_info.startswith("model:"):
        model_name = resource_info[6:]
        typer.echo(f"\nStarting {model_name} session (type 'exit' or 'quit' to end)\n")
        
        while True:
            try:
                user_input = typer.prompt("You", prompt_suffix=": ")
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                
                response = manager.chat(model_name, user_input)
                typer.echo(f"{model_name}: {response}\n")
                
            except KeyboardInterrupt:
                typer.echo("\nSession ended.")
                break
            except Exception as e:
                typer.echo(f"Error: {str(e)}")
                break
        
    elif resource_info.startswith("tool:"):
        tool_name = resource_info[5:]
        try:
            subprocess.run([tool_name], check=True)
        except subprocess.CalledProcessError as e:
            typer.echo(f"Error: {e}")
        except FileNotFoundError:
            typer.echo(f"'{tool_name}' not found in PATH.")
        except Exception as e:
            typer.echo(f"Error: {e}")

@app.command()
def config(
    set_key: Optional[str] = typer.Option(None, "--set", "-s", help="Set API key: provider=key"),
    list_status: bool = typer.Option(False, "--list", "-l", help="List config status"),
    reset: bool = typer.Option(False, "--reset", help="Reset config"),
    add_tool: Optional[str] = typer.Option(None, "--add-tool", help="Add custom CLI tool"),
    list_tools: bool = typer.Option(False, "--list-tools", help="List custom CLI tools")
):
    """Manage API keys and CLI tools configuration"""
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
            typer.echo(f"Added '{add_tool}' to custom CLI tools")
        else:
            typer.echo(f"Failed to add '{add_tool}'")
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
    
    if list_status or not (set_key or add_tool):
        status = config_manager.get_providers_status()
        typer.echo("Configuration:")
        
        for provider, info in status.items():
            if provider == 'openai':
                continue
            status_text = "SET" if info['configured'] else "NOT SET"
            typer.echo(f"  {provider.upper()}: {status_text}")
            if info['configured']:
                typer.echo(f"    Preview: {info['key_preview']}")

if __name__ == "__main__":
    app()