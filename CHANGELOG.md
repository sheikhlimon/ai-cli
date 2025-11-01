# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2025-11-01

### Major Features
- **Dynamic CLI tool discovery** - Auto-detects AI tools from PATH (droid, gemini, claude, amp, ollama, etc.)
- **Default command** - Just run `ai-cli` without subcommands to launch tool selector
- **Custom tool management** - Add/remove custom tools via config
- **Short flags** - Simple flags: `-s` (set), `-a` (add), `-r` (remove), `-l` (list), `-t` (tools)

### Added
- Dynamic PATH scanning for AI CLI tools with pattern matching
- Configuration methods for custom CLI tools (add/remove/list)
- Helper functions `_run_chat_session()` and `_run_cli_tool()` for better code organization
- Emojis for better UX (💬 chat, ❌ errors, 👋 goodbye)
- `@app.callback(invoke_without_command=True)` for default command behavior
- Short flag aliases for all config options

### Added
- Custom TUI selector with arrow key and vim motion (j/k) navigation
- Hidden cursor during selection for cleaner UI
- Bold text for selected items, dimmed text for unselected items
- Unified `chat()` method in AIModelManager for consistent model interface
- MIT License

### Changed
- **Streamlined interface** - Removed shell completion clutter from help
- **Simplified config** - Short flags for all operations
- **Better error messages** - Actionable suggestions with emojis
- **Code organization** - Extracted helper functions for maintainability
- **Documentation** - Simplified README and DEVELOPMENT.md examples
- Refactored `_check_cli_availability()` to scan entire PATH dynamically
- Improved `tools` command with cleaner resource type handling
- Config methods now use `_load_config()` and `_save_config()` helpers
- All examples updated to use short flags and simpler commands

### Removed
- Hardcoded CLI tools list (replaced with dynamic detection)
- Shell completion options from help output (add_completion=False)
- Redundant `openai` provider references
- Unused `create_env_file()` method in ConfigManager
- Duplicate JSON imports and file I/O code
- Verbose long-form option names from examples

### Fixed
- Subprocess handling in CLI tool launcher (removed problematic check=True)
- Exception handling specificity (json.JSONDecodeError, IOError instead of bare except)
- KeyboardInterrupt handling for graceful exits

### Technical Details
- **Code reduction**: config.py reduced by ~30% (165 to 116 lines)
- **Commits**: 7 major improvements (dynamic discovery, config UX, streamlined interface, refactoring, default command, docs, tools improvements)
- **Files modified**: cli.py, models.py, config.py, README.md, DEVELOPMENT.md
- **New architecture**:
  - ConfigManager: `_load_config()`, `_save_config()` helper methods
  - CLI: `_run_chat_session()`, `_run_cli_tool()` helper functions
  - Models: Dynamic PATH scanning with exclusion list
- **Pattern matching**: Detects AI tools by name, prefix (ai-, gpt-), and suffix (-cli, -ai, -gpt)

## [Previous] - 2025-11-01

### Added
- Custom TUI selector with arrow key and vim motion (j/k) navigation
- Hidden cursor during selection for cleaner UI
- Bold text for selected items, dimmed text for unselected items
- Unified `chat()` method in AIModelManager for consistent model interface
- MIT License

### Changed
- Replaced `pick` library dependency with custom raw terminal implementation
- Fixed newline rendering in raw terminal mode (using `\r\n` instead of `\n`)
- Streamlined README from 103 to 65 lines
- Updated installation instructions for cross-platform compatibility

### Removed
- `pick` library dependency (eliminated ~300 lines of fallback code)
- Verbose numbered menu fallbacks
- Old QWEN.md documentation
- Temporary test directories (.qwen, test_ai_cli)

### Fixed
- TUI alignment issues in raw terminal mode
- Line wrapping problems in interactive selector
- Terminal cursor visibility during selection
