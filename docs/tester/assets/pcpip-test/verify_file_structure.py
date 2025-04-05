#!/usr/bin/env python3
"""
File Structure Validator

Validates file structures defined in YAML against actual files on disk.
Requires explicit semantic file typing for specialized processing.

Core Operations:
1. Reads YAML file defining expected structure
2. Resolves paths and checks if files exist
3. Records file sizes and metadata
4. Generates embeddings (if requested)
5. Outputs detailed report in YAML format

Supported Semantic Types:
- CSV: metadata_csv, analysis_csv
- Images: raw_image, processed_image
- Other: illumination_file

YAML Structure Example:
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

Examples:
    python verify_file_structure.py input.yaml -o validated_output.yaml
    python verify_file_structure.py input.yaml --replace-path /original/path /new/path
    python verify_file_structure.py input.yaml --embedding-dir /path/to/embeddings
"""

import yaml
import csv
import hashlib
import sys
from pathlib import Path
import click


def get_file_size(path):
    """Get file size in bytes or None if file doesn't exist.

    Args:
        path (Path): Path to the file
    Returns:
        int or None: File size in bytes if exists, otherwise None
    """
    try:
        p = Path(path)
        return p.stat().st_size if p.exists() else None
    except Exception as e:
        click.echo(f"Error getting file size for {path}: {e}", err=True)
        return None


def read_csv_headers(file_path, max_headers=20):
    """Read headers from CSV file with optional truncation.

    Args:
        file_path (str): Path to the CSV file
        max_headers (int): Maximum headers before summarizing
    Returns:
        list: CSV header names, possibly truncated with summary
    """
    try:
        with open(file_path, "r", newline="") as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader, [])

            # If we have more headers than max_headers, add a summary entry
            if len(headers) > max_headers:
                remaining = len(headers) - (max_headers - 1)
                return headers[: max_headers - 1] + [f"{remaining} more columns"]
            else:
                return headers
    except Exception as e:
        click.echo(f"Error reading CSV headers from {file_path}: {e}", err=True)
        return []


def generate_embedding_path(file_path, embedding_base_dir, semantic_type):
    """Generate path for storing file embeddings.

    Args:
        file_path (str): Original file path
        embedding_base_dir (str): Base directory for embeddings
        semantic_type (str): Semantic file type
    Returns:
        str or None: Path to embedding file, or None if file doesn't exist
    """
    p = Path(file_path)
    if not p.exists() or not embedding_base_dir:
        return None

    # Create a unique filename based on the original path
    file_hash = hashlib.md5(str(p).encode("utf-8")).hexdigest()[:10]
    embedding_filename = f"{p.stem}_{file_hash}_embedding.npy"

    # Preserve relative path structure within the embedding directory
    rel_path = p.absolute()
    rel_dir = rel_path.parent
    rel_hash = hashlib.md5(str(rel_dir).encode("utf-8")).hexdigest()[:8]

    # Create embeddings directory structure
    embedding_path = Path(embedding_base_dir) / semantic_type / rel_hash
    embedding_path.mkdir(parents=True, exist_ok=True)

    return str(embedding_path / embedding_filename)


# Generic handler function
def handle_generic_file(file_path, embedding_dir=None, semantic_type=None):
    """Handler for generic files without specialized processing.

    Args:
        file_path (str): Path to the file
        embedding_dir (str, optional): Base directory for embeddings
        semantic_type (str, optional): Semantic type identifier
    Returns:
        dict: Basic file information with path and size
    """
    return {"path": str(file_path), "size": get_file_size(file_path)}


# CSV File Handlers
def handle_metadata_csv(file_path, embedding_dir=None, semantic_type="metadata_csv"):
    """Handler for metadata CSV files.

    Args:
        file_path (str): Path to the CSV file
        embedding_dir (str, optional): Base directory for embeddings
        semantic_type (str): Semantic type identifier
    Returns:
        dict: File info with headers and embedding path if available
    """
    file_info = handle_generic_file(file_path)

    if file_info["size"] is not None:
        file_info["headers"] = read_csv_headers(file_path)

        # Add embedding information
        if embedding_dir:
            embedding_path = generate_embedding_path(
                file_path, embedding_dir, semantic_type
            )
            if embedding_path:
                file_info["embedding_path"] = embedding_path
                file_info["has_embedding"] = True

    return file_info


def handle_analysis_csv(file_path, embedding_dir=None, semantic_type="analysis_csv"):
    """Handler for analysis CSV files.

    Args:
        file_path (str): Path to the CSV file
        embedding_dir (str, optional): Base directory for embeddings
        semantic_type (str): Semantic type identifier
    Returns:
        dict: File info with headers and embedding path if available
    """
    file_info = handle_generic_file(file_path)

    if file_info["size"] is not None:
        file_info["headers"] = read_csv_headers(file_path)

        # Additional analysis for this file type could be added here

        # Add embedding information
        if embedding_dir:
            embedding_path = generate_embedding_path(
                file_path, embedding_dir, semantic_type
            )
            if embedding_path:
                file_info["embedding_path"] = embedding_path
                file_info["has_embedding"] = True

    return file_info


# Image File Handlers
def handle_raw_image(file_path, embedding_dir=None, semantic_type="raw_image"):
    """Handler for raw image files.

    Args:
        file_path (str): Path to the image file
        embedding_dir (str, optional): Base directory for embeddings
        semantic_type (str): Semantic type identifier
    Returns:
        dict: File info with embedding path if available
    """
    file_info = handle_generic_file(file_path)

    if file_info["size"] is not None and embedding_dir:
        # Add embedding information
        embedding_path = generate_embedding_path(
            file_path, embedding_dir, semantic_type
        )
        if embedding_path:
            file_info["embedding_path"] = embedding_path
            file_info["has_embedding"] = True

    return file_info


def handle_processed_image(
    file_path, embedding_dir=None, semantic_type="processed_image"
):
    """Handler for processed image files.

    Args:
        file_path (str): Path to the image file
        embedding_dir (str, optional): Base directory for embeddings
        semantic_type (str): Semantic type identifier
    Returns:
        dict: File info with embedding path if available
    """
    file_info = handle_generic_file(file_path)

    if file_info["size"] is not None and embedding_dir:
        # Add embedding information
        embedding_path = generate_embedding_path(
            file_path, embedding_dir, semantic_type
        )
        if embedding_path:
            file_info["embedding_path"] = embedding_path
            file_info["has_embedding"] = True

    return file_info


# Other File Handlers
def handle_illumination_file(
    file_path, embedding_dir=None, semantic_type="illumination_file"
):
    """Handler for illumination correction files.

    Args:
        file_path (str): Path to the illumination file
        embedding_dir (str, optional): Base directory for embeddings
        semantic_type (str): Semantic type identifier
    Returns:
        dict: File info with embedding path if available
    """
    file_info = handle_generic_file(file_path)

    if file_info["size"] is not None and embedding_dir:
        # Add embedding information
        embedding_path = generate_embedding_path(
            file_path, embedding_dir, semantic_type
        )
        if embedding_path:
            file_info["embedding_path"] = embedding_path
            file_info["has_embedding"] = True

    return file_info


# Registry of handler functions by semantic type
HANDLERS = {
    # CSV types
    "metadata_csv": handle_metadata_csv,
    "analysis_csv": handle_analysis_csv,
    # Image types
    "raw_image": handle_raw_image,
    "processed_image": handle_processed_image,
    # Other types
    "illumination_file": handle_illumination_file,
}


def build_file_paths(yaml_data, embedding_dir=None, path_replacement=None):
    """Process YAML data and validate against files on disk.

    Args:
        yaml_data (dict): Parsed YAML defining expected file structure
        embedding_dir (str, optional): Base directory for embeddings
        path_replacement (tuple, optional): (old_path, new_path) for replacement
    Returns:
        dict: Processed structure with paths, sizes, and metadata
    """
    result = {}

    for section_name, section_data in yaml_data.items():
        result[section_name] = section_data.copy()
        base_path = section_data["path"]

        # Apply path replacement if specified
        if path_replacement:
            old_path, new_path = path_replacement
            if base_path.startswith(old_path):
                base_path = base_path.replace(old_path, new_path, 1)
                result[section_name]["path"] = base_path

        # Process all contents in this section - require the "contents" key
        result[section_name]["contents"] = {}
        for set_name, folders in section_data["contents"].items():
            result[section_name]["contents"][set_name] = []

            for folder_item in folders:
                folder_path = Path(base_path) / folder_item["folder"]
                processed_folder = {"folder": folder_item["folder"], "types": []}

                for file_group in folder_item["types"]:
                    semantic_type = file_group["type"]

                    # Skip unknown semantic types with a warning
                    if semantic_type not in HANDLERS:
                        click.echo(
                            f"Warning: Unknown semantic type '{semantic_type}', skipping",
                            err=True,
                        )
                        continue

                    handler = HANDLERS[semantic_type]
                    processed_files = []

                    for file_name in file_group["files"]:
                        full_path = folder_path / file_name
                        file_info = handler(full_path, embedding_dir, semantic_type)
                        processed_files.append(file_info)

                    processed_folder["types"].append(
                        {"type": semantic_type, "files": processed_files}
                    )

                result[section_name]["contents"][set_name].append(processed_folder)

    return result


@click.command()
@click.argument(
    "input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "-o",
    "--output-file",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output file name (default: input_name_parsed.yaml)",
)
@click.option(
    "--replace-path",
    nargs=2,
    type=str,
    help="Replace OLD_PATH with NEW_PATH in all file paths",
)
@click.option(
    "--embedding-dir",
    type=click.Path(file_okay=False, path_type=Path),
    help="Base directory to store file embeddings (optional)",
)
def main(input_file, output_file, replace_path, embedding_dir):
    """Validate file structure against YAML definition.

    Args:
        input_file (Path): YAML file with expected file structure
        output_file (Path, optional): Output report file
        replace_path (tuple, optional): Path replacement values
        embedding_dir (Path, optional): Embeddings directory
    """
    # If output file not specified, derive it from input filename
    if not output_file:
        output_file = input_file.with_name(
            f"{input_file.stem}_parsed{input_file.suffix}"
        )

    # Parse YAML and build full paths with sizes
    try:
        with open(input_file, "r") as f:
            yaml_data = yaml.safe_load(f)

        # Apply path replacement if specified
        path_replacement = replace_path if replace_path else None
        processed_data = build_file_paths(yaml_data, embedding_dir, path_replacement)

        # Save processed data
        with open(output_file, "w") as f:
            yaml.dump(processed_data, f, default_flow_style=False, sort_keys=False)

        click.echo(f"Processed YAML file has been saved to: {output_file}")
        if path_replacement:
            click.echo(
                f"Path replacement applied: '{path_replacement[0]}' → '{path_replacement[1]}'"
            )
        if embedding_dir:
            click.echo(f"Embeddings will be stored in: {embedding_dir}")

    except KeyError as e:
        click.echo(f"Error: Missing required field in YAML structure: {e}", err=True)
        click.echo(
            "Please validate your YAML structure against the required format.", err=True
        )
        sys.exit(1)
    except TypeError as e:
        click.echo(f"Error: Invalid YAML structure: {e}", err=True)
        click.echo(
            "YAML must follow the required structure with explicit semantic types.",
            err=True,
        )
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
