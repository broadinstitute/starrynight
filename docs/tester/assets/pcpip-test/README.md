# pcpip-test

A test suite for validating and testing the outputs from optical pooled screening (OPS) data processing pipelines.

## Components

### Current Tools

- `run_pcpip.sh` - Shell script to run the PCPIP test suite
- `verify_file_structure.py` - Validation script that processes YAML specifications to check file existence and extract metadata
- `compare_structures.py` - Comparison tool that analyzes differences between two structure files produced by verify_file_structure.py

### Test Fixtures

- `minimal/` - Directory containing minimal test fixtures:
  - `input.yaml` - Example input specification
  - `output_pcpip.yaml` - Example processed output for pcpip pipeline
  - `output_starrynight.yaml` - Example processed output for starrynight pipeline

## Semantic Type System

Both tools use a consistent semantic type system to handle different file types appropriately:

- **CSV Types**: `metadata_csv`, `analysis_csv`
- **Image Types**: `raw_image`, `processed_image`
- **Other Types**: `illumination_file`

## Tool: run_pcpip.sh

```bash
bash run_pcpip.sh
```

The script runs the full PCPIP test suite. See the script documentation for details.

## Tool: verify_file_structure.py

```bash
python verify_file_structure.py input.yaml [-o output_file] [--replace-path OLD_PATH NEW_PATH] [--embedding-dir DIR]
```

The script:
1. Reads a YAML file defining expected file structure
2. Resolves all relative paths to absolute paths
3. Checks if each file exists and records its size
4. For CSV files, extracts and records column headers and total header count
5. Generates embeddings for content fingerprinting (optional)
6. Outputs a detailed report showing what was found vs. expected

### Path Replacement

The `--replace-path` option allows you to test a different output directory with the same structure by replacing path prefixes:

```bash
python verify_file_structure.py input.yaml --replace-path "../../../../scratch/pcpip_example_output" "../../../../scratch/reproduce_pcpip_example_output"
```

This is particularly useful when:
- Comparing output from different runs of the same pipeline
- Testing reproduction of results in a different location
- Validating alternative implementations against the same specification

### Embedding Generation

The `--embedding-dir` option enables generation of file content embeddings:

```bash
python verify_file_structure.py input.yaml --embedding-dir path/to/embeddings
```

Embeddings provide a content fingerprint that can be used to detect changes in file content even when metadata (size, modification time) is identical. The script:
- Creates a unique identifier for each file
- Stores embeddings in an organized directory structure
- Supports different embedding formats (hash-based, binary)
- Uses content-specific embedding generation for each file type

## Tool: compare_structures.py

```bash
python compare_structures.py first.yaml second.yaml [-o output_file] [--output-format FORMAT] [--compare-embeddings]
```

This tool compares two file structure YAML files (produced by verify_file_structure.py) to identify differences in organization, file existence, and content.

The script:
1. Reads two processed YAML files defining file structures
2. Compares hierarchical structure (sections, sets, folders, types, files)
3. Performs type-specific comparisons for each file type
4. Optionally compares file embeddings for content similarity
5. Generates a detailed comparison report

### Output Formats

The tool supports multiple output formats:
- `yaml` (default) - YAML format for both human and machine readability
- `json` - JSON format for programmatic processing
- `text` - Text summary for quick human review

### Embedding Comparison

The `--compare-embeddings` option enables content-based comparisons:

```bash
python compare_structures.py first.yaml second.yaml --compare-embeddings --tolerance 0.01
```

This allows you to:
- Detect changes in file content even when metadata matches
- Calculate similarity scores between corresponding files
- Set tolerance levels for approximate matching
- Handle different embedding formats automatically

## Creating an Output Example

To create a minimal output example using the test fixtures:

1. Create a new directory for the outputs:
   ```bash
   mkdir -p minimal-output-example
   ```

2. Run verify_file_structure.py on the input YAML files:
   ```bash
   # Process the input.yaml file
   python verify_file_structure.py minimal/input.yaml -o minimal-output-example/input_parsed.yaml

   # Process the output_pcpip.yaml file
   python verify_file_structure.py minimal/output_pcpip.yaml -o minimal-output-example/output_pcpip_parsed.yaml

   # Process the output_starrynight.yaml file
   python verify_file_structure.py minimal/output_starrynight.yaml -o minimal-output-example/output_starrynight_parsed.yaml
   ```

3. Review the generated files in the minimal-output-example directory to see:
   - Which files exist and which don't
   - File sizes of existing files
   - CSV headers for any CSV files referenced in the YAMLs

4. Test with an alternative output directory:
   ```bash
   # Process with path replacement, i.e., test a different output folder
   python verify_file_structure.py minimal/output_pcpip.yaml -o minimal-output-example/reproduce_output_pcpip_parsed.yaml --replace-path "../../../../scratch/pcpip_example_output" "../../../../scratch/reproduce_pcpip_example_output"
   ```

5. Compare two output structures:
   ```bash
   # Compare the original and reproduced outputs
   python compare_structures.py minimal-output-example/output_pcpip_parsed.yaml minimal-output-example/reproduce_output_pcpip_parsed.yaml -o comparison.yaml
   ```

This provides a complete example of the tools' functionality with both validation and comparison capabilities.
