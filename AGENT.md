# Agent Context & Development Notes

## Project Overview

AI CLI is a unified interface for AI models and CLI tools with interactive selection. **Just run `ai-cli`** to launch the tool selector. Features dynamic tool discovery, simple configuration with short flags, and a custom TUI built from scratch.

## Architecture

### Core Modules

1. **cli.py** - Main CLI interface
   - `main()` - Main callback handling all options and default behavior
   - `select_option()` - Custom TUI selector using raw terminal mode
   - `tools()` - Interactive model/tool selector (internal function)
   - `_run_chat_session()` - Helper for model chat sessions
   - `_run_cli_tool()` - Helper for launching external CLI tools
   - `config()` - Configuration logic (internal function)

2. **models.py** - AI model management
   - `AIModelManager` - Main class for model interactions
   - `chat()` - Unified interface for all models
   - `_check_cli_availability()` - Dynamic PATH scanning for AI tools
   - `_check_ollama_availability()` - Detect local Ollama
   - `_get_ollama_models()` - List available Ollama models
   - Support for Claude, Gemini, Qwen APIs

3. **config.py** - Configuration persistence
   - `_load_config()` - Helper to load JSON config
   - `_save_config()` - Helper to save JSON config
   - `get_api_key()`, `set_api_key()` - API key management
   - `get_custom_cli_tools()`, `add_custom_cli_tool()`, `remove_custom_cli_tool()` - Custom tool management
   - Stores in `~/.ai-cli/config.json`

## Key Design Decisions

### Flat Command Structure (No Subcommands)

**All options at top level - no nested commands**

- Main callback accepts all config options directly
- All flags visible in main `--help` output
- Simpler UX: `ai-cli -l` instead of `ai-cli config --list`
- Removed `@app.command()` decorators - now internal functions

### Dynamic CLI Tool Discovery

**No hardcoded tool lists - scans PATH automatically with configurable patterns**

**Detection Strategy:**
1. Scans all directories in `PATH` environment variable
2. Matches against configurable patterns (stored in config.json)
3. Verifies tools are in current PATH (handles environment changes)
4. Adds custom user-configured tools
5. Tracks volatile Node.js-based tools

**Pattern Matching (configurable via ai_tool_patterns in config):**
- Exact matches: `ollama`, `aider`, `droid`, `gemini`, `claude`, `qwen`, `anthropic`, etc.
- Prefix matching: `ai-*`, `gpt-*`, `chatgpt-*`, `llm-*`, `gemini-*`, `claude-*`, etc.
- Suffix matching: `*-ai`, `*-gpt`, `*-llm`
- Suffix exclusions: Filters out false positives like `android-*`, `*-deploy`, etc.

**Exclusion System:**
- Default system tools: `node`, `npm`, `npx`, `python`, `pip`, `bash`, etc.
- User-configurable exclusions: Via `excluded_cli_tools` in config

**Multi-Version Node.js Support:**
- Scans all Node.js versions managed by nvm, fnm, and volta
- Tools from ANY Node version are available, not just current
- Stores absolute paths so tools work after version switches
- Automatically discovers global packages across all versions



### Custom TUI Implementation

**Raw Terminal Mode**

- Uses `tty.setraw()` for character-by-character input
- Critical: Must use `\r\n` instead of `\n` in raw mode
- Cursor management: Hide during selection, restore on exit
- Proper cleanup in finally block to prevent terminal corruption

## Key Functions Reference

### _check_cli_availability()

```python
def _check_cli_availability(self) -> list
```

- Scans PATH for AI tools using configurable patterns
- Verifies tools with `shutil.which()` (handles Node.js version switches)
- Returns sorted list of available tool names
- Handles permission errors, broken symlinks, duplicates gracefully

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

## Code Style

- **Concise**: No verbose comments, code should be self-documenting
- **Minimal**: Only necessary functionality, no feature creep
- **Clean**: Consistent formatting, clear variable names
- **Error messages**: Short, actionable, with emojis (❌ for errors, ✓ for success, 💬 for chat, 👋 for goodbye)
- **Helper functions**: Extract logic into `_private_helpers()` for better organization
- **Short flags**: Always provide single-letter aliases (-s, -a, -r, -l, -t, -m)
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

## Development Notes

### Adding New Models

1. Add API client setup in `AIModelManager._setup_apis()`
2. Add model method (e.g., `def new_model(self, prompt: str)`)
3. Add case in `chat()` method
4. Update `get_available_models()` to include when configured

### Adding New Commands

1. Add typer.Option to main and config functions in cli.py
2. Use typer.Option for flags/arguments
3. Keep error messages concise

### Customizing Tool Detection

Edit `~/.ai-cli/config.json` to customize patterns:

```json
{
  "ai_tool_patterns": {
    "exact_matches": ["ollama", "custom-tool"],
    "prefixes": ["ai-", "gpt-"],
    "suffixes": ["-ai", "-llm"],
    "suffix_exclusions": ["android", "deploy"]
  },
  "excluded_cli_tools": ["unwanted-tool"],
  "custom_cli_tools": ["my-ai"]
}
```

### Common Pitfalls

- **Text wrapping/misalignment in TUI**: Always use `\r\n` (carriage return + newline) in raw mode
- **Terminal left in broken state**: Always use try/finally block to restore settings and show cursor
- **ANSI codes visible as text**: Check `sys.stdin.isatty()` before entering TUI mode
- **Stale tool detection**: Always verify tools with `shutil.which()` after PATH scanning
- **Hardcoding patterns**: Use configurable patterns from config
