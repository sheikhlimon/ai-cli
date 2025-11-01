# How to Contribute

### Reporting Issues

- Check existing issues first
- Provide clear description and steps to reproduce
- Include your OS, Python version, and error messages

### Submitting Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature-name`)
3. Make your changes and test thoroughly
4. Commit with clear messages
5. Push and open a PR with description of changes

### Code Style

- Follow existing code patterns
- Keep it simple and readable
- Add tests for new features
- Run tests before submitting

## Development Setup

```bash
cd /home/limon/Work/ai-cli
python3 -m venv venv
venv/bin/pip install -e .
```

## Usage

```bash
# Direct execution
venv/bin/ai-cli         # Launch
venv/bin/ai-cli -l      # List config
venv/bin/ai-cli -s key  # Set key

# Or activate venv first
source venv/bin/activate  # Linux/Mac
ai-cli                    # Now works directly
deactivate                # When done
```

## Testing Changes

```bash
venv/bin/ai-cli  # Changes apply immediately (editable mode)
```

## Testing

```bash
venv/bin/python -m pytest              # All tests
venv/bin/python -m pytest -v           # Verbose
venv/bin/python -m pytest -m unit      # Unit tests only
venv/bin/python -m pytest --cov=ai_cli # With coverage
```

## Getting Started

**Fork and clone:**

```bash
git clone https://github.com/YOUR-USERNAME/ai-cli.git
cd ai-cli
git remote add upstream https://github.com/sheikhlimon/ai-cli.git
```

**Setup environment:**

```bash
python3 -m venv venv
venv/bin/pip install -e .
```

**Create a branch:**

```bash
git checkout -b my-feature
```

**Make changes, test, and commit:**

```bash
venv/bin/ai-cli  # Test your changes
venv/bin/python -m pytest  # Run tests
git add .
git commit -m "Add: my feature description"
git push origin my-feature
```

**Open a PR on GitHub**

## What is venv?

A virtual environment isolates Python dependencies for this project:

- Prevents conflicts with system Python
- Required on some systems (like Arch Linux)
- Each contributor has their own isolated setup

## FAQ

**Q: Why venv?**  
A: Isolated dependencies, no system conflicts.

**Q: Do I commit venv/?**  
A: No, it's in `.gitignore`.

**Q: Deleted venv/?**  
A: `python3 -m venv venv && venv/bin/pip install -e .`

**Q: Update dependencies?**  
A: Edit `pyproject.toml`, then `venv/bin/pip install -e . --upgrade`

## Project Structure

```
ai-cli/
├── ai_cli/          # Source code
│   ├── cli.py       # Main interface
│   ├── models.py    # AI model manager
│   └── config.py    # Configuration
├── tests/           # Test suite
├── venv/            # Virtual env (gitignored)
└── pyproject.toml   # Dependencies
```

## Questions?

Open an issue or start a discussion. We're happy to help!
