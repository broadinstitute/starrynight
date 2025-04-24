# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with documentation and code in this repository.

# StarryNight Documentation Guidelines

## Structure Principles
- Follow progressive disclosure (overview → concepts → details)
- Use clear section headers and consistent header levels
- Keep directory structure shallow (2-3 levels max)
- Ensure each section has a clear entry point document

## Content Standards
- Use consistent Markdown formatting with appropriate language tags
- Write concisely with numbered steps for complex procedures
- Include concrete examples with real commands and outputs
- Format code blocks, file paths, and commands appropriately
- Link to existing docs rather than duplicating content

## Code Standards

### Python
- Use snake_case for variables/functions, PascalCase for classes
- Import order: stdlib → third-party → local (grouped with blank lines)
- Type annotations for function parameters and returns
- 4-space indentation, ~88 char line limit
- NumPy-style docstrings with triple double-quotes
- Prefer returning typed objects over raising exceptions
- Use click/argparse for command-line interfaces
- Use pathlib for file path handling when possible

### Shell Scripts
- Use exports for environment variables
- Include clear error checking for required variables
- Use consistent indentation and descriptive comments

### Pipeline Files
- Document pipeline modifications in commit messages
- Maintain consistent module naming across related pipelines
- Include version and modification info in pipeline metadata
- Reference source of original pipelines in documentation

## Common Commands
- Build Python: `python -m build`
- Test: `pytest`
- Single test: `pytest path/to/test_file.py::test_function_name`
- Lint Python: `ruff`
- Generate pipeline graphs: `python /path/to/cp_graph.py input.json output.dot --rank-nodes --remove-unused-data`
- Render graphs: `dot -Gdpi=50 -Tpng input.dot -o output.png` or `dot -Tsvg input.dot -o output.svg`
- Filter LoadData CSVs: `python filter_loaddata_csv.py source_dir dest_dir --well WellA1,WellA2 --site 0,1 --cycle 1,2,3`
- Validate paths: `python validate_loaddata_paths.py path/to/loaddata.csv`

## Notes on Repository Restructuring
This repository is undergoing restructuring to improve organization:
- Implementation code (Python scripts, notebooks, test fixtures) is being moved out of `/docs/`
- Test code is being consolidated in a proper `/tests/` directory
- Notebooks will be moved to `/examples/notebooks/`
- Documentation will remain in `/docs/` with improved organization
