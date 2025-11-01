# Agent Context & Development Notes

## Project Overview

AI CLI is a unified interface for AI models and CLI tools with interactive selection. **Just run `ai-cli`** to launch the tool selector. Features dynamic tool discovery, simple configuration with short flags, and a custom TUI built from scratch.

## Architecture

### Core Modules

1. **cli.py** - Main CLI interface (306 lines)
   - `main()` - Main callback handling all options and default behavior
   - `select_option()` - Custom TUI selector using raw terminal mode
   - `tools()` - Interactive model/tool selector (internal function)
   - `_run_chat_session()` - Helper for model chat sessions
   - `_run_cli_tool()` - Helper for launching external CLI tools
   - `config()` - Configuration logic (internal function)

2. **models.py** - AI model management (259 lines)
   - `AIModelManager` - Main class for model interactions
   - `chat()` - Unified interface for all models
   - `_check_cli_availability()` - Dynamic PATH scanning for AI tools
   - `_check_ollama_availability()` - Detect local Ollama
   - `_get_ollama_models()` - List available Ollama models
   - Support for Claude, Gemini, Qwen APIs

3. **config.py** - Configuration persistence (116 lines, reduced from 165)
   - `_load_config()` - Helper to load JSON config
   - `_save_config()` - Helper to save JSON config
   - `get_api_key()`, `set_api_key()` - API key management
   - `get_custom_cli_tools()`, `add_custom_cli_tool()`, `remove_custom_cli_tool()` - Custom tool management
   - Stores in `~/.ai-cli/config.json`
   - Environment variable fallback

## Key Design Decisions

### Flat Command Structure (No Subcommands)

**All options at top level - no nested commands**

- Main callback accepts all config options directly
- `main()` checks if any config option is provided, otherwise launches tool selector
- All flags visible in main `--help` output
- Simpler UX: `ai-cli -l` instead of `ai-cli config --list`
- Removed `@app.command()` decorators from `tools()` and `config()` - now internal functions

### Dynamic CLI Tool Discovery

**No hardcoded tool lists - scans PATH automatically**

- Scans all directories in `PATH` environment variable
- Pattern matching: exact names (ollama, droid, gemini, claude, amp, qwen)
- Prefix matching: `ai-`, `gpt-`, `chatgpt-`, `llm-`, `gemini-`, `claude-`
- Suffix matching: `-cli`, `-ai`, `-gpt`, `-llm`
- Exclusion list to filter system tools (node, npm, python, etc.)
- Custom tools can be added via `ai-cli config -a <tool>`

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

### \_run_chat_session()

```python
def _run_chat_session(manager: AIModelManager, model_name: str)
```

- Runs interactive chat loop with AI model
- Shows 💬 emoji and exit instructions
- Handles 'exit', 'quit', 'q' commands
- Graceful KeyboardInterrupt handling

### \_run_cli_tool()

```python
def _run_cli_tool(tool_name: str)
```

- Launches external CLI tool via subprocess
- Better error messages with ❌ emoji
- Suggests `ai-cli config -a` for missing tools
- Handles FileNotFoundError, KeyboardInterrupt gracefully

### \_load_config() / \_save_config()

```python
def _load_config() -> Dict  # Returns empty dict if file doesn't exist
def _save_config(config: Dict) -> bool  # Returns success status
```

- Eliminates duplicate JSON loading/saving code
- Specific exception handling (json.JSONDecodeError, IOError)
- Used by all config methods for consistency

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
- **Error messages**: Short, actionable, with emojis (❌ for errors, ✓ for success, 💬 for chat, 👋 for goodbye)
- **Helper functions**: Extract logic into `_private_helpers()` for better organization
- **Short flags**: Always provide single-letter aliases (-s, -a, -r, -l, -t)
- **Default behavior**: Make common actions the default (e.g., `ai-cli` runs tool selector)

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
