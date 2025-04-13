# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# PCPIP Fixture Creation Tools

## Commands
- Run Python: `python script_name.py`
- Lint Python: `ruff`
- Run single test: `pytest path/to/test_file.py::test_function_name`
- Generate download list: `python create_starrynight_download_list.py`
- Filter LoadData CSVs: `python filter_loaddata_csv.py source_dir dest_dir --well WellA1,WellA2 --site 0,1 --cycle 1,2,3`
- Validate paths: `python validate_loaddata_paths.py path/to/loaddata.csv`
- Compress files: `./compress_starrynight_example.sh`

## Code Style
### Python
- Use snake_case for variables/functions, PascalCase for classes
- Import order: stdlib → third-party → local (grouped with blank lines)
- Type annotations for function parameters and returns
- Descriptive docstrings with meaningful parameter descriptions
- Use click/argparse for command-line interfaces
- Error handling with specific exception messages
- Use pathlib for file path handling when possible

### Shell Scripts
- Use exports for environment variables
- Include clear error checking for required variables
- Use consistent indentation and descriptive comments
