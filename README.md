# AI CLI - Multi-model Manager
# A command-line interface for interacting with various AI models

## Features
- Unified interface for multiple AI models (Qwen, Claude, Gemini, etc.)
- Compare outputs from different models
- Batch operations
- Configuration management
- Usage tracking

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai-cli
   ```

2. Install the package:
   ```bash
   pip install .
   # Or for development:
   pip install -e .
   ```

## Configuration

Create a `.env` file in your home directory or project root with your API keys:

```env
OPENAI_API_KEY=your_openai_api_key
CLAUDE_API_KEY=your_claude_api_key
GEMINI_API_KEY=your_gemini_api_key
```

## Usage

### Basic Commands

```bash
# List available models
ai-cli list

# Query a specific model
ai-cli qwen "What is the meaning of life?"
ai-cli claude "Explain quantum computing"
ai-cli gemini "Write a poem about coding"

# Compare responses from all models
ai-cli compare "How do I learn Python?"
```

### Advanced Features

```bash
# View configuration status
ai-cli config
```

## Available Models

- Qwen (via Tongyi API)
- Claude (via Anthropic API)
- Gemini (via Google AI API)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.