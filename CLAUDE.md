# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# StarryNight Project Guidelines

## Project Structure
- This is a Python project, comprising 4 packages:
- starrynight (same name as the repo):
  - Main code is in the @starrynight/src directory
  - Tests are in the @starrynight/tests directory
- pipecraft
  - Main code is in the @pipecraft/src directory
  - Tests are in the @pipecraft/tests directory
- conductor
  - Main code is in the @conductor/src directory
  - Tests are in the @conductor/tests directory
- canvas

We will focus entirely on these directories

- @starrynight/src, @starrynight/tests
- @pipecraft/src, @pipecraft/tests

## Commands
- Test: `uv run pytest` (must always use uv run)
- Single test: `uv run pytest path/to/test_file.py::test_function_name`
- Lint Python: `ruff`

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

### Shell Scripts
- Use exports for environment variables
- Include clear error checking for required variables
- Use consistent indentation and descriptive comments

## Error Handling & Logging
- Use appropriate exception types
- Include context information in exceptions
- Log errors with sufficient context for debugging
- Prefer returning typed objects over raising exceptions when possible

## AI-Friendly Coding Practices
- Use descriptive variable and function names that clearly indicate purpose
- Provide type hints consistently for better code understanding
- Add comments explaining complex logic or algorithms
- Structure code in a modular way with clear separation of concerns
- Include docstrings that explain function purpose, parameters, and return values

## Common Patterns
- When writing new code, follow existing patterns in similar files
- Use type hints consistently
- Add tests for new functionality

## Common Issues
- If tests fail, check that you've installed the package in development mode
- If linting fails, run `ruff --fix` to automatically fix some issues

## Repository Details
- The GitHub repo is git@github.com:broadinstitute/starrynight.git so be sure to use that with the GitHub MCP server

## Development Tools
- Use `gh project` for doing anything related to GitHub projects because the MCP server does not yet support it
