#!/usr/bin/env python3

import re
from pathlib import Path
from typing import Optional

import click
import pandas as pd


def find_path_filename_pairs(df: pd.DataFrame) -> list[tuple[str, str]]:
    """Find all PathName_X and FileName_X column pairs in the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The LoadData CSV as a pandas DataFrame

    Returns
    -------
    List[Tuple[str, str]]
        List of (PathName_X, FileName_X) column name pairs

    """
    # Find all PathName_ columns
    path_columns = [col for col in df.columns if col.startswith("PathName_")]
    pairs = []

    for path_col in path_columns:
        # Extract the suffix (X in PathName_X)
        suffix = path_col.replace("PathName_", "")

        # Check if corresponding FileName_ column exists
        file_col = f"FileName_{suffix}"
        if file_col in df.columns:
            pairs.append((path_col, file_col))

    return pairs


def validate_file_paths(
    df: pd.DataFrame, base_path: str | None = None
) -> tuple[list[dict], dict[str, int]]:
    """Validate that all referenced files in the LoadData CSV exist.

    Parameters
    ----------
    df : pd.DataFrame
        The LoadData CSV as a pandas DataFrame
    base_path : Optional[str]
        Base path to prepend to file paths

    Returns
    -------
    Tuple[List[Dict], Dict[str, int]]
        List of missing file information and summary statistics

    """
    # Find all PathName/FileName pairs
    path_file_pairs = find_path_filename_pairs(df)

    missing_files = []
    total_files = 0

    # Process each row
    for idx, row in df.iterrows():
        for path_col, file_col in path_file_pairs:
            if pd.notna(row[path_col]) and pd.notna(row[file_col]):
                total_files += 1

                # Construct file path
                file_path = Path(row[path_col]) / row[file_col]

                # Add base path if provided
                if base_path:
                    file_path = Path(base_path) / file_path

                # Check if file exists
                if not file_path.exists():
                    # Get metadata columns for context
                    metadata = {
                        col: row[col]
                        for col in df.columns
                        if col.startswith("Metadata_") and pd.notna(row[col])
                    }

                    # Add missing file info
                    missing_files.append(
                        {
                            "path": str(file_path),
                            "row_index": idx,
                            "path_column": path_col,
                            "file_column": file_col,
                            **metadata,
                        }
                    )

    # Create summary statistics
    stats = {
        "total_files": total_files,
        "missing_files": len(missing_files),
        "percent_missing": round(len(missing_files) / total_files * 100, 2)
        if total_files > 0
        else 0,
    }

    return missing_files, stats


@click.command()
@click.option(
    "--input-csv",
    required=True,
    type=click.Path(exists=True),
    help="Path to CSV file to validate",
)
@click.option(
    "--base-path", type=str, help="Base path to prepend to file paths"
)
@click.option(
    "--output-file",
    type=click.Path(),
    default="missing_files.csv",
    help="Path to save report of missing files (default: missing_files.csv)",
)
def main(input_csv: str, base_path: str | None, output_file: str) -> None:
    """Validate that all files referenced in a LoadData CSV file actually exist.

    This script checks all PathName_X/FileName_X pairs in the CSV, verifies that the
    referenced files exist, and reports any missing files.
    """
    # Read the input CSV
    input_path = Path(input_csv)
    df = pd.read_csv(input_path)

    # Validate file paths
    missing_files, stats = validate_file_paths(df, base_path)

    # Report summary
    click.echo(f"Validation results for {input_path}:")
    click.echo(f"  Total files referenced: {stats['total_files']}")
    click.echo(
        f"  Missing files: {stats['missing_files']} ({stats['percent_missing']}%)"
    )

    # Save report if there are missing files
    if missing_files:
        output_path = Path(output_file)
        pd.DataFrame(missing_files).to_csv(output_path, index=False)
        click.echo(f"  Missing files report saved to {output_path}")


if __name__ == "__main__":
    main()
