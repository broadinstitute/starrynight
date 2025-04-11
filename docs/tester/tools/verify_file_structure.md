# verify_file_structure Tool

The `verify_file_structure.py` tool validates file structures defined in YAML against actual files on disk. It requires explicit semantic file typing for specialized processing and provides detailed reports on file sizes, headers, and optional embeddings.

## Core Functionality

- **Path Resolution**: Checks the existence of files and directories
- **Size Verification**: Records file sizes for comparison
- **Header Extraction**: For CSV files, extracts and records headers
- **Embedding Generation**: Creates content fingerprints for deeper comparison
- **Semantic Typing**: Categorizes files into specific types for appropriate handling
- **YAML Reporting**: Generates detailed validation reports

## Supported Semantic Types

- **CSV Types**: `metadata_csv`, `analysis_csv` - CSV files with different purposes
- **Image Types**: `raw_image`, `processed_image` - Original and processed images
- **Other Types**: `illumination_file` - Specialized files like illumination corrections

## Usage

```bash
python verify_file_structure.py [options] <input_yaml>
```

### Options

- `-o, --output <file>`: Output file for validation report (default: stdout)
- `--replace-path <old_path> <new_path>`: Replace path prefix in file paths
- `--embedding-dir <dir>`: Directory to store embeddings for content fingerprinting
- `--verify-contents/--no-verify-contents`: Whether to verify file contents (default: True)

## Input YAML Structure

```yaml
section_name:
  level: plate
  path: /path/to/base/
  contents:
    set1:
      - folder: Folder1
        types:
          - type: metadata_csv
            files:
              - file1.csv
```

- `section_name`: Main category of files (e.g., "illumination_files")
- `level`: Organizational level (e.g., "plate", "batch")
- `path`: Base path for files in this section
- `contents`: Contains sets of folders and file types
- `set1`: Named set of folders containing files
- `folder`: Directory containing files of specified types
- `types`: List of file types in this folder
- `type`: Semantic file type (e.g., "metadata_csv")
- `files`: List of filenames to check

## Output Format

The tool generates a YAML report with detailed information about each file:

```yaml
section_name:
  level: plate
  path: /path/to/base/
  contents:
    set1:
      - folder: Folder1
        types:
          - type: metadata_csv
            files:
              - name: file1.csv
                exists: true
                size: 1024
                headers: ["Column1", "Column2", ...]
                embedding: path/to/embedding.emb
```

## Examples

### Basic Usage

```bash
python verify_file_structure.py input.yaml -o validated_output.yaml
```

### Path Replacement

Useful for comparing files in different locations:

```bash
python verify_file_structure.py input.yaml \
  --replace-path /original/path /new/path \
  -o output.yaml
```

### Embedding Generation

Generate content fingerprints for deeper comparison:

```bash
python verify_file_structure.py input.yaml \
  --embedding-dir /path/to/embeddings \
  -o output.yaml
```

## Usage in Pipeline Validation

In the pipeline validation process, `verify_file_structure.py` is used primarily in Stages 3-5 to:

1. Validate the structure of reference pipeline outputs
2. Validate the structure of StarryNight pipeline outputs
3. Generate detailed reports that can be compared with `compare_structures.py`

For detailed usage examples, refer to the individual pipeline validation documents.
