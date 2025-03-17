# StarryNight Project Guidelines

## Commands
- Build Python: `python -m build`
- Test: `pytest`
- Single test: `pytest path/to/test_file.py::test_function_name`
- Lint Python: `ruff`
- Frontend dev: `cd canvas && npm run dev`
- Frontend build: `cd canvas && npm run build`
- Frontend lint: `cd canvas && npm run lint`

## Code Style
### Python
- Snake_case for variables/functions, PascalCase for classes
- Imports: stdlib → third-party → local (grouped with blank lines)
- Consistent type annotations for all functions
- 4-space indentation, ~88 char line limit
- NumPy-style docstrings with triple double-quotes
- Prefer returning typed objects over raising exceptions

### TypeScript/React
- CamelCase for variables/functions, PascalCase for components/interfaces
- Type prefixes: 'T' for types (TProject)
- 2-space indentation
- Consistent JSX formatting with proper line breaks
- Strong typing with interfaces for all props
