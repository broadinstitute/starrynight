# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# StarryNight Project Guidelines

## Commands
- Build Python: `python -m build`
- Test: `pytest`
- Single test: `pytest path/to/test_file.py::test_function_name`
- Lint Python: `ruff`
- Package with setuptools: `python -m pip install -e .`

## Code Style
### Python
- Snake_case for variables/functions, PascalCase for classes
- Imports: stdlib → third-party → local (grouped with blank lines)
- Consistent type annotations for all functions
- 4-space indentation, 80-88 char line limit
- NumPy-style docstrings with triple double-quotes
- Prefer returning typed objects over raising exceptions
- Prefer pathlib for file operations
- Use click for CLI interfaces
- Docstrings required for modules and public functions
