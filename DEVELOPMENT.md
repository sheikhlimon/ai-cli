# Development Guide

## What is venv?

A **virtual environment (venv)** is an isolated Python environment for this project. Think of it as a separate Python installation that:
- Keeps this project's dependencies separate from system Python
- Prevents conflicts with other Python projects
- Required on systems with externally-managed Python (like Arch Linux)

## Quick Setup (First Time)

```bash
# 1. Navigate to project
cd /home/limon/Work/ai-cli

# 2. Create virtual environment (only do this ONCE)
python3 -m venv venv

# 3. Install the project in the venv
venv/bin/pip install -e .
```

That's it! You now have a `venv/` folder with everything installed.

## Running the CLI

You have two options:

### Option 1: Direct execution (easiest)
```bash
# From project directory
venv/bin/ai-cli           # Launch tool selector
venv/bin/ai-cli config -l # Show config
```

### Option 2: Activate venv first
```bash
# Activate the venv
source venv/bin/activate   # Linux/Mac
# OR
venv\Scripts\activate      # Windows

# Now you can use ai-cli directly
ai-cli              # Launch tool selector
ai-cli config -l    # Show config

# When done, deactivate
deactivate
```

## Testing Your Changes

```bash
# After making code changes, just run:
venv/bin/ai-cli

# No need to reinstall because we used -e (editable mode)
```

## Running Tests

The project includes a comprehensive test suite with pytest.

### Basic Testing

```bash
# Run all tests
venv/bin/python -m pytest

# Run with verbose output
venv/bin/python -m pytest -v

# Run specific test file
venv/bin/python -m pytest tests/test_cli.py
```

### Test Markers

Tests are organized by markers for selective execution:

```bash
# Run only unit tests (fast)
venv/bin/python -m pytest -m unit

# Run only integration tests
venv/bin/python -m pytest -m integration

# Run only slow tests
venv/bin/python -m pytest -m slow
```

### Coverage Reports

```bash
# Install coverage tool (first time only)
venv/bin/pip install pytest-cov

# Run tests with coverage
venv/bin/python -m pytest --cov=ai_cli

# Generate HTML coverage report
venv/bin/python -m pytest --cov=ai_cli --cov-report=html
# Open htmlcov/index.html in browser
```

### Quick Test Commands

```bash
# Fast check (unit tests only)
venv/bin/python -m pytest -m unit -v

# Full test suite with coverage
venv/bin/python -m pytest --cov=ai_cli -v

# Watch mode (requires pytest-watch)
venv/bin/pip install pytest-watch
venv/bin/ptw
```

## Sharing with Others

### For Users (Simple Installation)

Tell them to use **pipx** (installs in isolated environment automatically):

```bash
# Install pipx first (if not installed)
# Arch: sudo pacman -S python-pipx
# Ubuntu: sudo apt install pipx
# Mac: brew install pipx

# Install ai-cli
pipx install git+https://github.com/yourusername/ai-cli.git

# Use it
ai-cli tools
```

### For Developers (Want to Contribute)

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/ai-cli.git
cd ai-cli

# 2. Setup venv
python3 -m venv venv
venv/bin/pip install -e .

# 3. Run it
venv/bin/ai-cli tools

# 4. Make changes and test
# Edit files...
venv/bin/ai-cli tools  # Changes take effect immediately
```

## Why venv?

**Without venv (the problem):**
```bash
pip install -e .
# Error: externally-managed-environment
# Can't install! Python is protected by the system.
```

**With venv (the solution):**
```bash
venv/bin/pip install -e .
# ✓ Works! Installing in isolated environment.
```

## Common Questions

**Q: Do I commit the venv/ folder?**  
A: No, it's in `.gitignore`. Each person creates their own venv.

**Q: I deleted venv/, what now?**  
A: Just recreate it:
```bash
python3 -m venv venv
venv/bin/pip install -e .
```

**Q: How do I update dependencies?**  
A: Edit `pyproject.toml`, then:
```bash
venv/bin/pip install -e . --upgrade
```

**Q: Can I use regular Python?**  
A: On some systems (not Arch). But venv works everywhere.

## Directory Structure

```
ai-cli/
├── ai_cli/          # Your code
├── venv/            # Virtual environment (DON'T commit)
├── pyproject.toml   # Dependencies
└── README.md        # User docs
```

## Pro Tips

1. **Always use `venv/bin/` prefix** when running commands
2. **Or activate** the venv to avoid typing it every time
3. **Editable mode (`-e`)** means changes apply immediately
4. **Each project** should have its own venv

## Real Example Session

```bash
# Day 1: Setup
cd ai-cli
python3 -m venv venv
venv/bin/pip install -e .
venv/bin/ai-cli tools  # ✓ Works!

# Day 2: Make changes
vim ai_cli/cli.py      # Edit code
venv/bin/ai-cli tools  # ✓ Changes apply immediately!

# Day 3: Someone else tries it
git clone <repo>
cd ai-cli
python3 -m venv venv
venv/bin/pip install -e .
venv/bin/ai-cli tools  # ✓ Works for them too!
```
