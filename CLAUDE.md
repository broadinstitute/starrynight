# StarryNight Project Guidelines

## Build, Test & Lint Commands
- Install dependencies: `uv pip install -e .` (in project root)
- Run tests: `python -m pytest tests/` (all) or `python -m pytest tests/path/to/test_file.py::TestClass::test_function` (specific)
- Run linting: `python -m ruff check`
- Type checking: `basedpyright`
- Run the CLI: `starrynight` or `conductor`
- Build packages: `python -m build`

## Code Style
- **Imports**: Organized as stdlib → third-party → local, alphabetized (ruff enforced)
- **Types**: Required annotations (except `self`), use `dict[str, list[int]]` syntax (Union with `|`)
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
- **Documentation**: NumPy-style docstrings with Parameters/Returns sections
- **Error handling**: Use specific exceptions, validate parameters with assertions or ValueError
- **Path handling**: Use cloudpathlib for both local and cloud storage operations
- **Libraries**: Pydantic for models, networkx for graph operations, click for CLIs
