# Agent Context & Development Notes

## Project Overview

AI CLI is a terminal-based multi-model AI manager that provides a unified interface for interacting with various AI models (cloud and local). The key feature is an intuitive TUI selector built from scratch.

## Architecture

### Core Modules

1. **cli.py** - Main CLI interface
   - `select_option()` - Custom TUI selector using raw terminal mode
   - `tools()` - Interactive model/tool selector command
   - `config()` - Configuration management command

2. **models.py** - AI model management
   - `AIModelManager` - Main class for model interactions
   - `chat()` - Unified interface for all models
   - Auto-detection of Ollama models and CLI tools
   - Support for Claude, Gemini, Qwen APIs

3. **config.py** - Configuration persistence
   - Stores API keys in `~/.config/ai-cli/config.json`
   - Environment variable fallback

## Key Design Decisions

### Custom TUI Implementation

**Why not use `pick` or other libraries?**
- Wanted full control over rendering and behavior
- Eliminated 300+ lines of fallback code
- Direct control over ANSI escape sequences
- Better performance with minimal dependencies

**Raw Terminal Mode**
- Uses `tty.setraw()` for character-by-character input
- Critical: Must use `\r\n` instead of `\n` in raw mode
- Cursor management: Hide during selection, restore on exit
- Proper cleanup in finally block to prevent terminal corruption

### Visual Design
- Selected: Bold text with cyan `>` indicator
- Unselected: Dimmed (gray) text
- Alignment: 2 spaces + indicator + 1 space + text
- Clean screen clearing with ANSI `\033[2J\033[H`

## Common Pitfalls & Solutions

### Issue: Text wrapping/misalignment in TUI
**Cause:** Using `\n` in raw terminal mode only moves cursor down, not to line start
**Solution:** Always use `\r\n` (carriage return + newline) in raw mode

### Issue: Terminal left in broken state
**Cause:** Not restoring terminal settings or showing cursor
**Solution:** Always use try/finally block to restore settings and show cursor

### Issue: ANSI codes visible as text
**Cause:** Terminal doesn't support ANSI or output is redirected
**Solution:** Check `sys.stdin.isatty()` before entering TUI mode

## Key Functions Reference

### select_option()
```python
def select_option(options: List[Tuple[str, str]], title: str) -> Optional[Tuple[str, str]]
```
- Returns: (display_name, resource_info) or None if cancelled
- Navigation: Arrow keys (↑/↓), vim keys (j/k), Enter to select, q/ESC to quit
- Handles: Ctrl+C gracefully

### ANSI Escape Sequences Used
```python
"\033[2J\033[H"      # Clear screen and move to home
"\033[?25l"          # Hide cursor
"\033[?25h"          # Show cursor
"\033[1m"            # Bold
"\033[2m"            # Dim
"\033[1;36m"         # Cyan color
"\033[0m"            # Reset all attributes
```

## Development Workflow

### Testing TUI
```bash
# Must run in actual terminal (not piped/redirected)
venv/bin/ai-cli tools
```

### Adding New Models
1. Add API client setup in `AIModelManager._setup_apis()`
2. Add model method (e.g., `def new_model(self, prompt: str)`)
3. Add case in `chat()` method
4. Update `get_available_models()` to include when configured

### Adding New Commands
1. Add `@app.command()` decorated function in cli.py
2. Use typer.Option for flags/arguments
3. Keep error messages concise

## Code Style

- **Concise**: No verbose comments, code should be self-documenting
- **Minimal**: Only necessary functionality, no feature creep
- **Clean**: Consistent formatting, clear variable names
- **Error messages**: Short and actionable (e.g., "Error: message" not "An error occurred: message")

## Dependencies

**Core:**
- typer - CLI framework
- anthropic - Claude API
- google-generativeai - Gemini API
- dashscope - Qwen API
- python-dotenv - Environment variables

**System:**
- termios, tty - Raw terminal control (Unix only)
- subprocess - For Ollama and CLI tool detection

## Future Considerations

### Potential Improvements
- Async model calls for faster responses
- Conversation history/context management
- Model-specific parameter tuning
- Streaming responses
- Windows native support (currently requires WSL for raw mode)

### Known Limitations
- TUI requires TTY (won't work with piped input/output)
- Raw terminal mode is Unix-specific (termios/tty)
- No streaming support (all responses are complete)
- Single-turn conversations only (no context persistence)

## Testing Notes

**Manual Testing Required:**
- TUI must be tested in actual terminal
- Test arrow keys, vim keys, and all exit methods
- Verify cursor restoration on all exit paths
- Check alignment with different option text lengths

**Automated Testing:**
- Model detection logic
- Config file read/write
- API key validation
- Command argument parsing

## Maintenance Tips

1. **Never** use `print()` or `sys.stdout.write("\n")` in raw mode without `\r`
2. **Always** restore terminal in finally blocks
3. **Always** show cursor before exiting
4. **Test** TUI changes in actual terminal, not via subprocess
5. **Keep** error messages under 80 characters
6. **Avoid** adding new dependencies unless absolutely necessary

## Contact Points for Issues

- TUI rendering issues → Check `\r\n` usage and cursor hide/show
- Terminal corruption → Check finally blocks and cursor restoration  
- Alignment issues → Verify spacing before/after indicator
- Model not detected → Check `_setup_apis()` and API key configuration
- Command not working → Check typer decorators and parameter types
