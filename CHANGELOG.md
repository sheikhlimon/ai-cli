# Changelog

## [Unreleased] - 2024-11-01

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
- Simplified error messages across the codebase
- Updated installation instructions for cross-platform compatibility

### Removed
- `pick` library dependency (eliminated ~300 lines of fallback code)
- Verbose numbered menu fallbacks
- Redundant comments and documentation
- Old QWEN.md documentation
- Temporary test directories (.qwen, test_ai_cli)

### Fixed
- TUI alignment issues in raw terminal mode
- Line wrapping problems in interactive selector
- Terminal cursor visibility during selection
- Cross-platform installation instructions (was Arch-specific)

### Technical Details
- Total code reduction: ~300 lines removed, ~217 lines added (net -83 lines)
- Files modified: cli.py, models.py, pyproject.toml, README.md, .gitignore
- New ANSI escape sequences used:
  - `\033[?25l` - Hide cursor
  - `\033[?25h` - Show cursor
  - `\033[1m` - Bold text
  - `\033[2m` - Dim text
  - `\033[1;36m` - Cyan color
  - `\033[0m` - Reset formatting
