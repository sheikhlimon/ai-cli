# Contributing Guide

## What is venv?

A **virtual environment (venv)** is an isolated Python environment for this project. Think of it as a separate Python installation that:
- Keeps this project's dependencies separate from system Python
- Prevents conflicts with other Python projects
- Required on systems with externally-managed Python (like Arch Linux)

## Quick Setup

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

## Distribution

**For users:**
```bash
pipx install git+https://github.com/sheikhlimon/ai-cli.git
```

**For contributors:**
```bash
git clone https://github.com/sheikhlimon/ai-cli.git
cd ai-cli
python3 -m venv venv
venv/bin/pip install -e .
```

## FAQ

**Q: Why venv?**  
A: Isolated dependencies, no system conflicts.

**Q: Do I commit venv/?**  
A: No, it's in `.gitignore`.

**Q: Deleted venv/?**  
A: `python3 -m venv venv && venv/bin/pip install -e .`

**Q: Update dependencies?**  
A: Edit `pyproject.toml`, then `venv/bin/pip install -e . --upgrade`

## Structure

```
ai-cli/
├── ai_cli/          # Source code
│   ├── cli.py       # Main interface (306 lines)
│   ├── models.py    # AI model manager (259 lines)
│   └── config.py    # Configuration (116 lines)
├── tests/           # Test suite
├── venv/            # Virtual env (gitignored)
└── pyproject.toml   # Dependencies
```
