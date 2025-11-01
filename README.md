# AI CLI

Unified interface for AI models and CLI tools with interactive selection.

## Features

- **Just run `ai-cli`** - Interactive tool selector launches automatically
- Auto-detects AI tools (droid, gemini, claude, amp, ollama, etc.)
- Supports cloud models (Qwen, Claude, Gemini) and local Ollama models
- Simple config with short flags: `-s` (set), `-a` (add), `-l` (list)
- Arrow keys or vim motions (j/k) for navigation

## Installation

### For Users (Simple)

```bash
# Install with pipx (recommended)
pipx install git+https://github.com/sheikhlimon/ai-cli.git

# Use it - that's it!
ai-cli
```

### For Developers

```bash
# Clone and setup
git clone https://github.com/sheikhlimon/ai-cli.git
cd ai-cli
python3 -m venv venv
venv/bin/pip install -e .

# Run it
venv/bin/ai-cli
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup instructions.

## Quick Start

```bash
# Launch interactive selector (or just: ai-cli)
ai-cli

# Configure API keys
ai-cli config -s claude=sk-...
ai-cli config -s gemini=...
ai-cli config -s qwen=...

# Add custom AI tools (if not auto-detected)
ai-cli config -a my-tool

# View everything
ai-cli config -l              # Show API keys
ai-cli config -t              # Show custom tools
```

## Configuration

Set API keys via command or `.env` file:

```env
CLAUDE_API_KEY=your_key
GEMINI_API_KEY=your_key
QWEN_API_KEY=your_key
```

## Requirements

- Python 3.8+
- Optional: [Ollama](https://ollama.ai/) for local models

## License

MIT
