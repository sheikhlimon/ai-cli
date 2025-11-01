# AI CLI - Multi-model Manager
# A command-line interface for interacting with various AI models

## Features
- Unified interface for multiple AI models (Qwen, Claude, Gemini, GPT, Ollama, etc.)
- Compare outputs from different models
- Interactive chat sessions with individual models
- Batch operations
- Configuration management
- Support for both cloud and local (Ollama) models
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

## Prerequisites

- For cloud models (Qwen, Claude, Gemini, OpenAI): API keys
- For local models: Install and run [Ollama](https://ollama.ai/) with desired models

## Configuration

Create a `.env` file in your home directory or project root with your API keys:

```env
OPENAI_API_KEY=your_openai_api_key
CLAUDE_API_KEY=your_claude_api_key
GEMINI_API_KEY=your_gemini_api_key
QWEN_API_KEY=your_qwen_api_key
```

## Usage

### Basic Commands

```bash
# List available models (both cloud and local)
ai-cli list

# Query a specific model
ai-cli qwen "What is the meaning of life?"
ai-cli claude "Explain quantum computing"
ai-cli gemini "Write a poem about coding"
ai-cli openai-model "What is machine learning?" --model gpt-3.5-turbo
ai-cli ollama "What is AI?" --model llama2

# Compare responses from all models
ai-cli compare "How do I learn Python?"
```

### Interactive Mode

```bash
# Start an interactive chat session with a model
ai-cli interactive qwen
ai-cli interactive claude
ai-cli interactive gemini
ai-cli interactive gpt-3.5-turbo
ai-cli interactive ollama:llama2
```

### Advanced Features

```bash
# View configuration status
ai-cli config

# Manage configuration
ai-cli config --set openai=your_openai_key
ai-cli config --list
ai-cli config --reset

# Save response to a file
ai-cli qwen "Write a story" --output story.txt
ai-cli compare "Explain AI" -o comparison.txt
```

## Available Models

### Cloud Models
- Qwen (via Tongyi API)
- Claude (via Anthropic API)
- Gemini (via Google AI API)
- GPT models (via OpenAI API)

### Local Models
- Ollama models (any model installed with Ollama)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.