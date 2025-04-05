# pcpip-test

A test suite for validating and testing the StarryNight pipeline specification system.

## Purpose

This folder contains testing utilities for the StarryNight optical pooled screening (OPS) data processing pipeline. The tools here help:

- Validate pipeline configurations against expected specifications
- Test output file structures and organization
- Verify data integrity across pipeline stages
- Support development of new pipeline components

## Components

### Current Tools

- `parse_yaml.py` - Validation script that processes YAML specifications to check file existence and extract metadata

### Test Fixtures

- `minimal/` - Directory containing minimal test fixtures:
  - `input.yaml` - Example input specification
  - `output_pcpip.yaml` - Example processed output for pcpip pipeline
  - `output_starrynight.yaml` - Example processed output for starrynight pipeline

## Tool: parse_yaml.py

```bash
python parse_yaml.py input.yaml [-o output_file] [--replace-path OLD_PATH NEW_PATH]
```

The script:
1. Reads a YAML file defining expected file structure
2. Resolves all relative paths to absolute paths
3. Checks if each file exists and records its size
4. For CSV files, extracts and records column headers
5. Outputs a detailed report showing what was found vs. expected

### Path Replacement

The `--replace-path` option allows you to test a different output directory with the same structure by replacing path prefixes:

```bash
python parse_yaml.py input.yaml --replace-path "../../../../scratch/starrynight_example_output" "../../../../scratch/reproduce_starrynight_example_output"
```

This is particularly useful when:
- Comparing output from different runs of the same pipeline
- Testing reproduction of results in a different location
- Validating alternative implementations against the same specification

## Creating an Output Example

To create a minimal output example using the test fixtures:

1. Create a new directory for the outputs:
   ```bash
   mkdir -p minimal-output-example
   ```

2. Run parse_yaml.py on the input YAML files:
   ```bash
   # Process the input.yaml file
   python parse_yaml.py minimal/input.yaml -o minimal-output-example/input_parsed.yaml

   # Process the output_pcpip.yaml file
   python parse_yaml.py minimal/output_pcpip.yaml -o minimal-output-example/output_pcpip_parsed.yaml

   # Process the output_starrynight.yaml file
   python parse_yaml.py minimal/output_starrynight.yaml -o minimal-output-example/output_starrynight_parsed.yaml
   ```

3. Review the generated files in the minimal-output-example directory to see:
   - Which files exist and which don't
   - File sizes of existing files
   - CSV headers for any CSV files referenced in the YAMLs

4. Test with an alternative output directory:
   ```bash
   # Process with path replacement (test a different output folder)
   python parse_yaml.py minimal/output_pcpip.yaml -o minimal-output-example/output_pcpip_parsed.yaml --replace-path "../../../../scratch/pcpip_example_output" "../../../../scratch/reproduce_pcpip_example_output"
   ```

This provides a complete example of the tool's functionality with both inputs and expected outputs.

## Integration with StarryNight

This test suite integrates with the broader StarryNight platform by:
- Testing pipeline specifications defined in pcpip-io.json
- Validating file structure integrity between processing stages
- Ensuring data organization follows the expected hierarchy:
  - Batch → Plate → Well → Site → Cycle level organization
  - Cell painting and barcoding image processing paths

## Example

Input YAML defines expected files:
```yaml
images:
    level: plate
    path: path/to/images/
    files:
      set1:
        - folder: Plate1
          files:
            - tiff:
              - path/to/image1.tiff
              - path/to/image2.tiff
```

Output YAML reports what was found:
```yaml
images:
    level: plate
    path: path/to/images/
    files:
      set1:
        - folder: Plate1
          files:
            - tiff:
              - path: /absolute/path/to/image1.tiff
                size: 1024000
              - path: /absolute/path/to/image2.tiff
                size: null  # File doesn't exist
```
