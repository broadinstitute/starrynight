#!/usr/bin/env python3
"""
StarryNight Pipeline File Structure Validator

This script validates file structures defined in YAML configuration files against the actual
files present on disk. It's part of the testing infrastructure for the StarryNight platform,
which processes and analyzes optical pooled screening (OPS) image data.

The script performs the following operations:
1. Reads a YAML file that defines an expected file structure for pipeline inputs/outputs
2. Resolves all relative paths to absolute paths
3. Checks if each specified file actually exists on disk
4. Records file sizes for all files (or None if missing)
5. For CSV files, extracts and records column headers
6. Outputs a detailed report in YAML format showing the validation results

This tool is particularly useful for:
- Testing pipeline configurations before running expensive computations
- Validating that pipeline outputs match expected specifications
- Comparing outputs from different pipeline runs or implementations
- Ensuring data organization follows the expected hierarchy

Examples:
    Basic usage:
        python verify_pipeline_files.py input.yaml -o output_parsed.yaml

    With path replacement (to test against a different root directory):
        python verify_pipeline_files.py input.yaml -o output_parsed.yaml --replace-path OLD_PATH NEW_PATH

    With embedding directory specified:
        python verify_pipeline_files.py input.yaml -o output_parsed.yaml --embedding-dir /path/to/embeddings

Part of the StarryNight platform testing infrastructure.
"""

import yaml
import csv
import hashlib
from pathlib import Path
import click


def get_file_size(path):
    """Get file size in bytes or None if file doesn't exist."""
    try:
        p = Path(path)
        return p.stat().st_size if p.exists() else None
    except Exception as e:
        click.echo(f"Error getting file size for {path}: {e}", err=True)
        return None


def read_csv_headers(file_path, max_headers=20):
    """Read headers from a CSV file and return the first max_headers.
    If there are more than max_headers, the last item will indicate how many more columns exist."""
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


def generate_embedding_path(file_path, embedding_base_dir, file_type_dir="embeddings"):
    """Generate a path for storing file embeddings in a central location.

    Args:
        file_path: The original file path
        embedding_base_dir: Base directory for all embeddings
        file_type_dir: Subdirectory for specific file type embeddings

    Returns:
        Path to the embedding file
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
    embedding_path = Path(embedding_base_dir) / file_type_dir / rel_hash
    embedding_path.mkdir(parents=True, exist_ok=True)

    return str(embedding_path / embedding_filename)


# Handler functions for different file types
def handle_generic_file(file_path, embedding_dir=None):
    """Handler for generic files"""
    return {"path": str(file_path), "size": get_file_size(file_path)}


def handle_csv_file(file_path, embedding_dir=None):
    """Handler for CSV files"""
    file_info = handle_generic_file(file_path)

    if file_info["size"] is not None:
        file_info["headers"] = read_csv_headers(file_path)

        # Add embedding information
        if embedding_dir:
            embedding_path = generate_embedding_path(
                file_path, embedding_dir, "csv_embeddings"
            )
            if embedding_path:
                file_info["embedding_path"] = embedding_path
                file_info["has_embedding"] = True

    return file_info


def handle_image_file(file_path, embedding_dir=None):
    """Handler for image files (tiff, png)"""
    file_info = handle_generic_file(file_path)

    if file_info["size"] is not None and embedding_dir:
        # Add embedding information
        embedding_path = generate_embedding_path(
            file_path, embedding_dir, "image_embeddings"
        )
        if embedding_path:
            file_info["embedding_path"] = embedding_path
            file_info["has_embedding"] = True

    return file_info


def handle_numpy_file(file_path, embedding_dir=None):
    """Handler for numpy files"""
    file_info = handle_generic_file(file_path)

    if file_info["size"] is not None and embedding_dir:
        # Add embedding information
        embedding_path = generate_embedding_path(
            file_path, embedding_dir, "numpy_embeddings"
        )
        if embedding_path:
            file_info["embedding_path"] = embedding_path
            file_info["has_embedding"] = True

    return file_info


def build_file_paths(yaml_data, embedding_dir=None, path_replacement=None):
    """Process YAML and return structure with full paths and file sizes.

    Args:
        yaml_data: The parsed YAML data
        embedding_dir: Base directory to store embeddings (optional)
        path_replacement: Tuple of (old_path, new_path) to replace in all paths
    """
    result = {}

    # Setup file handlers for each supported type
    file_handlers = {
        "csv": handle_csv_file,
        "tiff": handle_image_file,
        "png": handle_image_file,
        "npy": handle_numpy_file,
    }

    for section_name, section_data in yaml_data.items():
        result[section_name] = section_data.copy()
        base_path = section_data["path"]

        # Apply path replacement if specified
        if path_replacement:
            old_path, new_path = path_replacement
            if base_path.startswith(old_path):
                base_path = base_path.replace(old_path, new_path, 1)
                result[section_name]["path"] = base_path

        if "files" in section_data:
            for set_name, folders in section_data["files"].items():
                result[section_name]["files"][set_name] = []

                for folder_item in folders:
                    folder_path = Path(base_path) / folder_item["folder"]
                    processed_folder = {"folder": folder_item["folder"], "files": []}

                    for file_item in folder_item["files"]:
                        if isinstance(file_item, dict):
                            # Handle file type groups (csv, tiff, png, etc.)
                            processed_types = {}
                            for file_type, file_list in file_item.items():
                                processed_types[file_type] = []

                                # Get appropriate handler function for this file type
                                handler = file_handlers.get(
                                    file_type.lower(), handle_generic_file
                                )

                                for file_name in file_list:
                                    full_path = folder_path / file_name
                                    # Pass embedding_dir to the handler
                                    file_info = handler(full_path, embedding_dir)
                                    processed_types[file_type].append(file_info)

                            processed_folder["files"].append(processed_types)
                        else:
                            # Files must be grouped by type, ungrouped files are not supported
                            click.echo(
                                f"Warning: Ungrouped file '{file_item}' found in folder '{folder_item['folder']}'. Skipping.",
                                err=True,
                            )
                            continue

                    result[section_name]["files"][set_name].append(processed_folder)

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
    """
    Parse YAML file defining pipeline file structure and validate against actual files.

    INPUT_FILE: The YAML file to process.
    """
    # If output file not specified, derive it from input filename
    if not output_file:
        output_file = input_file.with_name(
            f"{input_file.stem}_parsed{input_file.suffix}"
        )

    # Parse YAML and build full paths with sizes
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


if __name__ == "__main__":
    main()
