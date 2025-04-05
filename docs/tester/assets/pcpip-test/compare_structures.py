#!/usr/bin/env python3
"""
Structure Comparison Tool

Compares two file structure YAML files (produced by verify_file_structure.py)
to identify differences in organization, file existence, and content.

Core Operations:
1. Reads two processed YAML files defining file structures
2. Compares hierarchical structure (sections, sets, folders, types, files)
3. Performs type-specific comparisons for each file type
4. Optionally compares file embeddings for content similarity
5. Generates a detailed comparison report

Supported Semantic Types:
- CSV: metadata_csv, analysis_csv
- Images: raw_image, processed_image
- Other: illumination_file

Examples:
    python compare_structures.py first.yaml second.yaml -o comparison_report.yaml
    python compare_structures.py first.yaml second.yaml --output-format json
    python compare_structures.py first.yaml second.yaml --compare-embeddings
"""

import yaml
import json
import sys
import numpy as np
from pathlib import Path
import click
from pprint import pformat
from datetime import datetime


def load_yaml_structure(yaml_path):
    """Load and validate a YAML structure file.

    Args:
        yaml_path (Path): Path to the YAML file
    Returns:
        dict: Loaded and validated structure
    """
    try:
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        # Basic validation
        if not isinstance(data, dict):
            raise ValueError("YAML root must be a dictionary")

        # Validate each section has required keys
        for section_name, section in data.items():
            if "path" not in section:
                raise ValueError(
                    f"Section '{section_name}' missing required 'path' key"
                )
            if "contents" not in section:
                raise ValueError(
                    f"Section '{section_name}' missing required 'contents' key"
                )

        return data
    except Exception as e:
        click.echo(f"Error loading YAML structure from {yaml_path}: {e}", err=True)
        sys.exit(1)


def compare_embeddings(embedding_path1, embedding_path2, tolerance=0.0):
    """Compare two embeddings and return similarity results.

    Automatically detects and handles different embedding formats:
    - NumPy arrays (.npy files)
    - Text-based embeddings (hash strings, vectors, etc.)

    Args:
        embedding_path1 (str): Path to first embedding file
        embedding_path2 (str): Path to second embedding file
        tolerance (float): Tolerance for numerical differences
    Returns:
        dict: Comparison results with match status and similarity score
    """
    # Check if both files exist
    path1, path2 = Path(embedding_path1), Path(embedding_path2)
    if not path1.exists() or not path2.exists():
        return {"match": False, "error": "One or both embedding files missing"}

    # Try to detect file type by content examination instead of relying on extension
    try:
        # First try opening as binary NumPy file
        try:
            # If this succeeds, it's a NumPy file
            embedding1 = np.load(path1)
            embedding2 = np.load(path2)

            # Check shapes
            if embedding1.shape != embedding2.shape:
                return {
                    "match": False,
                    "error": f"Shape mismatch: {embedding1.shape} vs {embedding2.shape}",
                }

            # Calculate MSE
            mse = np.mean((embedding1 - embedding2) ** 2)
            similarity = 1.0 / (1.0 + mse)

            return {
                "match": mse <= tolerance,
                "similarity": float(similarity),
                "mse": float(mse),
                "method": "numpy_array",
            }
        except (IOError, ValueError):
            # Not a NumPy file, try as text
            with open(path1, "r") as f1, open(path2, "r") as f2:
                content1 = f1.read().strip()
                content2 = f2.read().strip()

            # Check if content looks like hash strings (alphanumeric only)
            is_hash = all(c.isalnum() for c in content1 + content2)

            # Check if content looks like numeric vectors
            try:
                # Try to parse as numeric vectors
                values1 = [float(x) for x in content1.split()]
                values2 = [float(x) for x in content2.split()]

                if len(values1) != len(values2):
                    return {
                        "match": False,
                        "error": "Dimension mismatch in vector embeddings",
                    }

                # Calculate MSE
                mse = sum((v1 - v2) ** 2 for v1, v2 in zip(values1, values2)) / len(
                    values1
                )
                similarity = 1.0 / (1.0 + mse)

                return {
                    "match": mse <= tolerance,
                    "similarity": similarity,
                    "mse": mse,
                    "method": "vector",
                }
            except ValueError:
                # Not a numeric vector, just compare as strings
                return {
                    "match": content1 == content2,
                    "similarity": 1.0 if content1 == content2 else 0.0,
                    "method": "hash" if is_hash else "text",
                }
    except Exception as e:
        # Fallback for any unexpected errors
        return {"match": False, "error": f"Comparison error: {str(e)}"}


def compare_files(file1, file2, options):
    """Compare two file entries based on their basic properties.

    Args:
        file1 (dict): First file information
        file2 (dict): Second file information
        options (dict): Comparison options
    Returns:
        dict: Comparison results
    """
    result = {
        "status": "different",
        "details": {
            "path": {"first": file1["path"], "second": file2["path"]},
            "size": {"first": file1["size"], "second": file2["size"]},
        },
    }

    # Check if one or both files don't exist
    if file1["size"] is None and file2["size"] is None:
        result["status"] = "both_missing"
    elif file1["size"] is None:
        result["status"] = "missing_in_first"
    elif file2["size"] is None:
        result["status"] = "missing_in_second"
    # If both exist, check if identical
    elif file1["size"] == file2["size"]:
        result["status"] = (
            "possibly_identical"  # Size match doesn't guarantee identical content
        )

    # Compare embeddings if requested and available
    if (
        options.get("compare_embeddings", False)
        and "embedding_path" in file1
        and "embedding_path" in file2
        and file1["size"] is not None
        and file2["size"] is not None
    ):
        embedding_result = compare_embeddings(
            file1["embedding_path"],
            file2["embedding_path"],
            options.get("tolerance", 0.0),
        )

        result["details"]["embedding"] = embedding_result

        # Update overall status based on embedding match
        if embedding_result.get("match", False):
            result["status"] = "identical"

    return result


# Type-specific comparison functions
def compare_metadata_csv(file1, file2, options):
    """Compare two metadata CSV files.

    Args:
        file1 (dict): First file information
        file2 (dict): Second file information
        options (dict): Comparison options
    Returns:
        dict: Comparison results with CSV-specific details
    """
    # Get basic file comparison
    result = compare_files(file1, file2, options)

    # Add CSV-specific comparison if both files exist
    if file1["size"] is not None and file2["size"] is not None:
        # Compare headers if available
        if "headers" in file1 and "headers" in file2:
            headers1, headers2 = file1["headers"], file2["headers"]

            # Check if headers were truncated
            headers_truncated1 = any("more columns" in str(h) for h in headers1)
            headers_truncated2 = any("more columns" in str(h) for h in headers2)
            headers_truncated = headers_truncated1 or headers_truncated2

            # Compare visible headers
            visible_headers_match = headers1 == headers2

            # Compare true header counts if available
            total_count1 = file1.get("header_count", len(headers1))
            total_count2 = file2.get("header_count", len(headers2))
            count_match = total_count1 == total_count2

            result["details"]["headers"] = {
                "match": count_match,
                "visible_match": visible_headers_match,
                "truncated": headers_truncated,
                "count": {"first": total_count1, "second": total_count2},
                "difference": []
                if visible_headers_match
                else [h for h in headers1 if h not in headers2]
                + [h for h in headers2 if h not in headers1],
            }

            # Update status if headers don't match
            if not count_match and result["status"] == "possibly_identical":
                result["status"] = "different"

    return result


def compare_analysis_csv(file1, file2, options):
    """Compare two analysis CSV files.

    Args:
        file1 (dict): First file information
        file2 (dict): Second file information
        options (dict): Comparison options
    Returns:
        dict: Comparison results with CSV-specific details
    """
    # Analysis CSVs have the same comparison logic as metadata CSVs
    return compare_metadata_csv(file1, file2, options)


def compare_raw_image(file1, file2, options):
    """Compare two raw image files.

    Args:
        file1 (dict): First file information
        file2 (dict): Second file information
        options (dict): Comparison options
    Returns:
        dict: Comparison results for image files
    """
    # For now, just use the basic file comparison
    # In a real implementation, might extract image dimensions, format, etc.
    return compare_files(file1, file2, options)


def compare_processed_image(file1, file2, options):
    """Compare two processed image files.

    Args:
        file1 (dict): First file information
        file2 (dict): Second file information
        options (dict): Comparison options
    Returns:
        dict: Comparison results for image files
    """
    # For now, just use the basic file comparison
    return compare_files(file1, file2, options)


def compare_illumination_file(file1, file2, options):
    """Compare two illumination files.

    Args:
        file1 (dict): First file information
        file2 (dict): Second file information
        options (dict): Comparison options
    Returns:
        dict: Comparison results
    """
    # For now, just use the basic file comparison
    return compare_files(file1, file2, options)


# Registry of comparison functions by semantic type
COMPARISON_HANDLERS = {
    # CSV types
    "metadata_csv": compare_metadata_csv,
    "analysis_csv": compare_analysis_csv,
    # Image types
    "raw_image": compare_raw_image,
    "processed_image": compare_processed_image,
    # Other types
    "illumination_file": compare_illumination_file,
}


def compare_file_types(type_group1, type_group2, options):
    """Compare two file type groups.

    Args:
        type_group1 (dict): First type group
        type_group2 (dict): Second type group
        options (dict): Comparison options
    Returns:
        dict: Comparison results
    """
    semantic_type = type_group1["type"]  # Both should have the same type

    # Get the appropriate comparison handler
    if semantic_type not in COMPARISON_HANDLERS:
        click.echo(
            f"Warning: No comparison handler for type '{semantic_type}', using generic",
            err=True,
        )
        handler = compare_files
    else:
        handler = COMPARISON_HANDLERS[semantic_type]

    # Map files by name for easier comparison
    files1 = {Path(f["path"]).name: f for f in type_group1["files"]}
    files2 = {Path(f["path"]).name: f for f in type_group2["files"]}

    # Find common and unique files
    all_files = set(files1.keys()) | set(files2.keys())

    # Compare each file
    file_comparisons = {}
    for filename in all_files:
        if filename in files1 and filename in files2:
            # File exists in both - compare
            file_comparisons[filename] = handler(
                files1[filename], files2[filename], options
            )
        elif filename in files1:
            # File only in first
            file_comparisons[filename] = {
                "status": "missing_in_second",
                "details": {
                    "path": {"first": files1[filename]["path"], "second": None}
                },
            }
        else:
            # File only in second
            file_comparisons[filename] = {
                "status": "missing_in_first",
                "details": {
                    "path": {"first": None, "second": files2[filename]["path"]}
                },
            }

    # Determine overall status
    statuses = [comparison["status"] for comparison in file_comparisons.values()]
    if all(status == "identical" for status in statuses):
        overall_status = "identical"
    elif all(status in ["identical", "possibly_identical"] for status in statuses):
        overall_status = "possibly_identical"
    elif any(
        status in ["missing_in_first", "missing_in_second"] for status in statuses
    ):
        overall_status = "different_files"
    else:
        overall_status = "different_content"

    return {
        "type": semantic_type,
        "status": overall_status,
        "file_count": {"first": len(files1), "second": len(files2)},
        "files": file_comparisons,
    }


def compare_folder_types(folder1, folder2, options):
    """Compare types within two folders.

    Args:
        folder1 (dict): First folder
        folder2 (dict): Second folder
        options (dict): Comparison options
    Returns:
        dict: Comparison results
    """
    # Map types by type name
    types1 = {t["type"]: t for t in folder1["types"]}
    types2 = {t["type"]: t for t in folder2["types"]}

    # Find all unique types
    all_types = set(types1.keys()) | set(types2.keys())

    # Compare each type
    type_comparisons = {}
    for type_name in all_types:
        if type_name in types1 and type_name in types2:
            # Type exists in both, compare files
            type_comparisons[type_name] = compare_file_types(
                types1[type_name], types2[type_name], options
            )
        elif type_name in types1:
            # Type only in first
            type_comparisons[type_name] = {
                "type": type_name,
                "status": "missing_in_second",
                "file_count": {"first": len(types1[type_name]["files"]), "second": 0},
            }
        else:
            # Type only in second
            type_comparisons[type_name] = {
                "type": type_name,
                "status": "missing_in_first",
                "file_count": {"first": 0, "second": len(types2[type_name]["files"])},
            }

    # Determine overall status
    if not type_comparisons:
        overall_status = "empty"
    elif all(comp["status"] == "identical" for comp in type_comparisons.values()):
        overall_status = "identical"
    elif all(
        comp["status"] in ["identical", "possibly_identical"]
        for comp in type_comparisons.values()
    ):
        overall_status = "possibly_identical"
    elif any(
        comp["status"] in ["missing_in_first", "missing_in_second"]
        for comp in type_comparisons.values()
    ):
        overall_status = "different_types"
    else:
        overall_status = "different_content"

    return {
        "folder": folder1["folder"],  # Both should have the same folder name
        "status": overall_status,
        "types": type_comparisons,
    }


def compare_set_folders(set1, set2, options):
    """Compare folders in two sets.

    Args:
        set1 (list): Folders in first set
        set2 (list): Folders in second set
        options (dict): Comparison options
    Returns:
        dict: Comparison results
    """
    # Map folders by name
    folders1 = {f["folder"]: f for f in set1}
    folders2 = {f["folder"]: f for f in set2}

    # Find all unique folder names
    all_folders = set(folders1.keys()) | set(folders2.keys())

    # Compare each folder
    folder_comparisons = {}
    for folder_name in all_folders:
        if folder_name in folders1 and folder_name in folders2:
            # Folder exists in both, compare types
            folder_comparisons[folder_name] = compare_folder_types(
                folders1[folder_name], folders2[folder_name], options
            )
        elif folder_name in folders1:
            # Folder only in first
            folder_comparisons[folder_name] = {
                "folder": folder_name,
                "status": "missing_in_second",
            }
        else:
            # Folder only in second
            folder_comparisons[folder_name] = {
                "folder": folder_name,
                "status": "missing_in_first",
            }

    # Determine overall status
    if not folder_comparisons:
        overall_status = "empty"
    elif all(comp["status"] == "identical" for comp in folder_comparisons.values()):
        overall_status = "identical"
    elif all(
        comp["status"] in ["identical", "possibly_identical", "empty"]
        for comp in folder_comparisons.values()
    ):
        overall_status = "possibly_identical"
    elif any(
        comp["status"] in ["missing_in_first", "missing_in_second"]
        for comp in folder_comparisons.values()
    ):
        overall_status = "different_folders"
    else:
        overall_status = "different_content"

    return {
        "status": overall_status,
        "folder_count": {"first": len(folders1), "second": len(folders2)},
        "folders": folder_comparisons,
    }


def compare_section_sets(section1, section2, options):
    """Compare sets in two sections.

    Args:
        section1 (dict): First section
        section2 (dict): Second section
        options (dict): Comparison options
    Returns:
        dict: Comparison results
    """
    # Get contents from both sections
    contents1 = section1["contents"]
    contents2 = section2["contents"]

    # Find all unique set names
    all_sets = set(contents1.keys()) | set(contents2.keys())

    # Compare each set
    set_comparisons = {}
    for set_name in all_sets:
        if set_name in contents1 and set_name in contents2:
            # Set exists in both, compare folders
            set_comparisons[set_name] = compare_set_folders(
                contents1[set_name], contents2[set_name], options
            )
        elif set_name in contents1:
            # Set only in first
            set_comparisons[set_name] = {
                "status": "missing_in_second",
                "folder_count": {"first": len(contents1[set_name]), "second": 0},
            }
        else:
            # Set only in second
            set_comparisons[set_name] = {
                "status": "missing_in_first",
                "folder_count": {"first": 0, "second": len(contents2[set_name])},
            }

    # Determine overall status
    if all(comp["status"] == "identical" for comp in set_comparisons.values()):
        overall_status = "identical"
    elif all(
        comp["status"] in ["identical", "possibly_identical", "empty"]
        for comp in set_comparisons.values()
    ):
        overall_status = "possibly_identical"
    elif any(
        comp["status"] in ["missing_in_first", "missing_in_second"]
        for comp in set_comparisons.values()
    ):
        overall_status = "different_sets"
    else:
        overall_status = "different_content"

    return {
        "path": {"first": section1["path"], "second": section2["path"]},
        "status": overall_status,
        "sets": set_comparisons,
    }


def compare_structures(structure1, structure2, options):
    """Compare two complete file structures.

    Args:
        structure1 (dict): First structure
        structure2 (dict): Second structure
        options (dict): Comparison options
    Returns:
        dict: Comparison results
    """
    # Find all unique section names
    all_sections = set(structure1.keys()) | set(structure2.keys())

    # Compare each section
    section_comparisons = {}
    for section_name in all_sections:
        if section_name in structure1 and section_name in structure2:
            # Section exists in both, compare contents
            section_comparisons[section_name] = compare_section_sets(
                structure1[section_name], structure2[section_name], options
            )
        elif section_name in structure1:
            # Section only in first
            section_comparisons[section_name] = {
                "status": "missing_in_second",
                "path": {"first": structure1[section_name]["path"], "second": None},
            }
        else:
            # Section only in second
            section_comparisons[section_name] = {
                "status": "missing_in_first",
                "path": {"first": None, "second": structure2[section_name]["path"]},
            }

    # Determine overall status
    if all(comp["status"] == "identical" for comp in section_comparisons.values()):
        overall_status = "identical"
    elif all(
        comp["status"] in ["identical", "possibly_identical"]
        for comp in section_comparisons.values()
    ):
        overall_status = "possibly_identical"
    elif any(
        comp["status"] in ["missing_in_first", "missing_in_second"]
        for comp in section_comparisons.values()
    ):
        overall_status = "different_sections"
    else:
        overall_status = "different_content"

    # Create comparison report
    return {
        "comparison_time": datetime.now().isoformat(),
        "status": overall_status,
        "first_structure": str(options["first_yaml"]),
        "second_structure": str(options["second_yaml"]),
        "options": {
            k: v for k, v in options.items() if k not in ["first_yaml", "second_yaml"]
        },
        "sections": section_comparisons,
    }


def format_output(diff_data, format_type):
    """Format comparison data in the specified output format.

    Args:
        diff_data (dict): Comparison data
        format_type (str): Output format (yaml, json, text)
    Returns:
        str: Formatted output
    """
    if format_type == "yaml":
        return yaml.dump(diff_data, default_flow_style=False, sort_keys=False)
    elif format_type == "json":
        return json.dumps(diff_data, indent=2)
    elif format_type == "text":
        summary = []
        summary.append("=" * 80)
        summary.append(f"STRUCTURE COMPARISON: {diff_data['status'].upper()}")
        summary.append("-" * 80)
        summary.append(f"First:  {diff_data['first_structure']}")
        summary.append(f"Second: {diff_data['second_structure']}")
        summary.append(f"Time:   {diff_data['comparison_time']}")
        summary.append("-" * 80)

        # Add section summaries
        for section_name, section_info in diff_data["sections"].items():
            summary.append(f"Section '{section_name}': {section_info['status']}")
            if section_info["status"] in ["missing_in_first", "missing_in_second"]:
                continue

            # Summarize sets
            for set_name, set_info in section_info["sets"].items():
                summary.append(f"  Set '{set_name}': {set_info['status']}")

                # Add details for different files
                if set_info["status"] not in [
                    "identical",
                    "missing_in_first",
                    "missing_in_second",
                ]:
                    for folder_name, folder_info in set_info.get("folders", {}).items():
                        if folder_info["status"] not in [
                            "identical",
                            "missing_in_first",
                            "missing_in_second",
                        ]:
                            summary.append(
                                f"    Folder '{folder_name}': {folder_info['status']}"
                            )

                            # Add type differences
                            for type_name, type_info in folder_info.get(
                                "types", {}
                            ).items():
                                if type_info["status"] not in [
                                    "identical",
                                    "missing_in_first",
                                    "missing_in_second",
                                ]:
                                    summary.append(
                                        f"      Type '{type_name}': {type_info['status']}"
                                    )

                                    # Add file differences
                                    for file_name, file_info in type_info.get(
                                        "files", {}
                                    ).items():
                                        if file_info["status"] not in [
                                            "identical",
                                            "missing_in_first",
                                            "missing_in_second",
                                        ]:
                                            summary.append(
                                                f"        File '{file_name}': {file_info['status']}"
                                            )

        summary.append("=" * 80)
        return "\n".join(summary)
    else:
        return pformat(diff_data)


@click.command()
@click.argument(
    "first_yaml", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.argument(
    "second_yaml", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "-o",
    "--output-file",
    type=click.Path(dir_okay=False, path_type=Path),
    help="Output file for comparison results",
)
@click.option(
    "--output-format",
    type=click.Choice(["yaml", "json", "text"]),
    default="yaml",
    help="Format for comparison output (default: yaml)",
)
@click.option(
    "--compare-embeddings/--no-compare-embeddings",
    default=False,
    help="Compare file embeddings when available",
)
@click.option(
    "--tolerance",
    type=float,
    default=0.0,
    help="Tolerance for numerical differences in embeddings",
)
def main(
    first_yaml, second_yaml, output_file, output_format, compare_embeddings, tolerance
):
    """Compare two structure YAML files and report differences.

    Args:
        first_yaml (Path): First YAML file with verified structure
        second_yaml (Path): Second YAML file with verified structure
        output_file (Path, optional): Output file for comparison results
        output_format (str): Format for comparison output
        compare_embeddings (bool): Whether to compare file embeddings
        tolerance (float): Tolerance for numerical differences
    """
    # Load YAML files
    click.echo(f"Loading structures from {first_yaml} and {second_yaml}...")
    structure1 = load_yaml_structure(first_yaml)
    structure2 = load_yaml_structure(second_yaml)

    # Comparison options
    options = {
        "first_yaml": first_yaml,
        "second_yaml": second_yaml,
        "compare_embeddings": compare_embeddings,
        "tolerance": tolerance,
    }

    # Perform comparison
    click.echo("Comparing structures...")
    comparison_data = compare_structures(structure1, structure2, options)

    # Format the output
    output_text = format_output(comparison_data, output_format)

    # Save or print results
    if output_file:
        with open(output_file, "w") as f:
            f.write(output_text)
        click.echo(f"Comparison results saved to {output_file}")
    else:
        click.echo("\nComparison Results:")
        click.echo(output_text)

    # Print summary
    click.echo(f"\nOverall comparison result: {comparison_data['status'].upper()}")


if __name__ == "__main__":
    main()
