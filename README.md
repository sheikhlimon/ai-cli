# AI CLI

Multi-model AI manager with interactive TUI selector.

## Features

- Interactive TUI with arrow keys/vim motions (j/k)
- Unified interface for cloud models (Qwen, Claude, Gemini)
- Auto-detects local Ollama models
- Persistent API key configuration

## Installation

### For Users (Simple)

```bash
# Install with pipx (recommended - works everywhere)
pipx install git+https://github.com/yourusername/ai-cli.git

# Use it
ai-cli tools
```

### For Developers

```bash
# Clone and setup
git clone https://github.com/sheikhlimon/ai-cli.git
cd ai-cli
python3 -m venv venv
venv/bin/pip install -e .

# Run it
venv/bin/ai-cli tools
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup instructions.

## Quick Start

```bash
# Launch interactive selector
ai-cli tools

# Configure API keys
ai-cli config --set claude=sk-...
ai-cli config --set gemini=...
ai-cli config --set qwen=...

# View config
ai-cli config --list
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
