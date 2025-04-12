# pcpip-generate-dummy-structures

Tools to simulate and validate directory structures for pooled Cell Painting experiments.

<https://github.com/broadinstitute/starrynight/tree/main/docs/tester/assets/pcpip-generate-dummy-structures>

## Components

- `generate_csvs.py`: Generates CSV files with metadata and file paths based on experiment configuration
- `generate_outputs.py`: Creates simulated directory structures and placeholder files
- `process_json.py`: Processes JSON output into CSV files and file lists

## Usage Examples

### Generating CSV Files

```sh
# Generate CSV files and filelist
./run_generate_csvs.sh
```

This creates:
- CSV files in `csv_output/` suitable for CellProfiler pipelines
- Text files in `filelist_output/` listing all generated file paths

### Generating File Structure

```sh
# Generate simulated file structure
./run_generate_files.sh
```

This creates:

- Simulated directory structure (optionally with placeholder files if `--create-files` is used)
- `generated_paths.txt` with list of all paths

### Comparing Generated Paths

```sh
# Compare paths from both methods to check for discrepancies
comm -23 generated_paths_from_csvs.txt generated_paths.txt
```

This helps validate consistency between the different generation approaches.
