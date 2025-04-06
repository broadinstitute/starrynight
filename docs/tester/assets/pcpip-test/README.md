# pcpip-test

Test suite for validating and testing outputs from optical pooled screening (OPS) data processing pipelines.

## Components

- `run_pcpip.sh`: Shell script to run the PCPIP test suite
- `verify_file_structure.py`: Validates file existence and extracts metadata using YAML specifications
- `compare_structures.py`: Compares differences between structure files produced by verify_file_structure.py

### Test Fixtures

- `minimal/`: Directory containing minimal test fixtures:
  - `input.yaml`: Example input specification
  - `output_pcpip.yaml`: Example processed output for pcpip pipeline
  - `output_starrynight.yaml`: Example processed output for starrynight pipeline

## Semantic Type System

Both tools use a consistent semantic type system to handle different file types appropriately:

- **CSV Types**: `metadata_csv`, `analysis_csv`
- **Image Types**: `raw_image`, `processed_image`
- **Other Types**: `illumination_file`

## Usage Examples

### Running Full Test Suite

```bash
bash run_pcpip.sh
```

The script runs the full PCPIP test suite.

### File Structure Verification

```bash
python verify_file_structure.py input.yaml [-o output_file] [--replace-path OLD_PATH NEW_PATH] [--embedding-dir DIR]
```

This tool:

1. Reads a YAML file defining expected file structure
2. Checks if each file exists and records its size
3. For CSV files, extracts and records column headers
4. Generates embeddings for content fingerprinting (optional)
5. Outputs a detailed report

#### Path Replacement

```bash
python verify_file_structure.py input.yaml --replace-path "../../../../scratch/pcpip_example_output" "../../../../scratch/reproduce_pcpip_example_output"
```

This is useful for comparing output from different runs or testing reproduction in different locations.

#### Embedding Generation

```bash
python verify_file_structure.py input.yaml --embedding-dir path/to/embeddings
```

Embeddings provide a content fingerprint for detecting changes in file content.

### Structure Comparison

```bash
python compare_structures.py first.yaml second.yaml [-o output_file] [--output-format FORMAT] [--compare-embeddings]
```

This tool compares two file structure YAML files to identify differences in organization and content.

#### Output Formats

The tool supports multiple output formats:
- `yaml` (default): YAML format for both human and machine readability
- `json`: JSON format for programmatic processing
- `text`: Text summary for quick human review

#### Embedding Comparison

```bash
python compare_structures.py first.yaml second.yaml --compare-embeddings --tolerance 0.01
```

This allows detection of changes in file content even when metadata matches.

## Creating an Output Example

To create a minimal output example using the test fixtures:

Create a new directory for the outputs:

```bash
mkdir -p minimal-output-example
```

Run verify_file_structure.py on the input YAML files:

```bash
# Process the input.yaml file
python verify_file_structure.py minimal/input.yaml -o minimal-output-example/input_parsed.yaml

# Process the output_pcpip.yaml file
python verify_file_structure.py minimal/output_pcpip.yaml -o minimal-output-example/output_pcpip_parsed.yaml

# Process the output_starrynight.yaml file
python verify_file_structure.py minimal/output_starrynight.yaml -o minimal-output-example/output_starrynight_parsed.yaml
```

Review the generated files in the minimal-output-example directory to see:

   - Which files exist and which don't
   - File sizes of existing files
   - CSV headers for any CSV files referenced in the YAMLs

Test with an alternative output directory:

```bash
# Process with path replacement, i.e., test a different output folder
python \
  verify_file_structure.py minimal/output_pcpip.yaml \
  -o minimal-output-example/reproduce_output_pcpip_parsed.yaml \
  --replace-path "../../../../scratch/pcpip_example_output" \
  "../../../../scratch/reproduce_pcpip_example_output"
```

Compare two output structures:

```bash
# Compare the original and reproduced outputs
python compare_structures.py minimal-output-example/output_pcpip_parsed.yaml minimal-output-example/reproduce_output_pcpip_parsed.yaml -o comparison.yaml
```

This provides a complete example of the tools' functionality with both validation and comparison capabilities.
