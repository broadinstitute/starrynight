# Simulate Cell Painting Directory Structures

The utilities in this directory help simulate and validate the expected directory structure and file organization for pooled Cell Painting experiments.

## Overview

This directory contains tools to:
1. Generate CSV files that represent the expected metadata structure
2. Generate a simulated file structure based on the project's IO configuration
3. Compare the generated paths to validate consistency between approaches

## Available Scripts

### generate_csvs.py
Generates CSV files containing metadata and file paths based on the experiment configuration.
- Simulates metadata fields, file paths, and other parameters for Cell Painting pipelines
- Creates JSON that is processed into CSV files by process_json.py

### generate_outputs.py
Creates simulated directory structures and placeholder files based on the IO configuration.
- Can create actual placeholder files with the `--create-files` flag
- Outputs the paths in both JSON and plain text formats

### process_json.py
Processes the JSON output from generate_csvs.py into:
- CSV files suitable for CellProfiler pipelines (in csv_output/)
- Text files listing all file paths (in filelist_output/)

## Usage

```bash
# Generate CSV files and filelist
./run_generate_csvs.sh

# Generate simulated file structure
./run_generate_files.sh

# Compare the paths from both methods to check for discrepancies
comm -23 generated_paths_from_csvs.txt generated_paths.txt
```

## Example Output

After running these scripts, you'll get:
- `csv_output/`: Directory containing CSV files with metadata and path information
- `filelist_output/`: Directory containing text files with all generated file paths
- `Source1/`: Directory structure with simulated placeholder files (if --create-files was used)
- `generated_paths.txt` and `generated_paths_from_csvs.txt`: Text files for comparison
