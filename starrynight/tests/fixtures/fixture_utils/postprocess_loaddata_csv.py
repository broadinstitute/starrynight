#!/usr/bin/env python3
"""Post-process LoadData CSV files for StarryNight test fixtures.

This script handles several post-processing steps for LoadData CSV files:
1. Updates file paths to use the correct absolute paths
2. Renames Metadata_SBSCycle header to Metadata_Cycle
3. Removes the "Well" prefix from Metadata_Well column values

Usage:
    python postprocess_loaddata_csv.py --input-dir <input_dir> [--output-dir <output_dir>]
                                       [--source-path <old_path>] [--target-path <new_path>]
                                       [--fixture-id <fixture_id>] [--update-paths]
                                       [--update-headers] [--clean-wells]

Example:
    python postprocess_loaddata_csv.py --input-dir ./trimmed_load_data_dir --update-paths --update-headers --clean-wells

"""

import argparse
import subprocess
import sys
from pathlib import Path

import pandas as pd


def get_repo_root():
    """Get the absolute path of the repository root."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("Error: Not in a git repository or git command failed")
        sys.exit(1)


def process_csv_file(
    file_path,
    output_path=None,
    source_path=None,
    target_path=None,
    update_paths=False,
    update_headers=False,
    clean_wells=False,
):
    """Process a single CSV file with all requested operations.

    Args:
        file_path: Path to the CSV file
        output_path: Path to save processed file (if None, overwrites original)
        source_path: Original path to replace
        target_path: New path to use
        update_paths: Whether to update file paths
        update_headers: Whether to update headers
        clean_wells: Whether to clean well identifiers

    Returns:
        bool: Whether any modifications were made

    """
    # Determine target file
    target_file = output_path if output_path else file_path

    # If we need to copy to output_path
    if output_path and file_path != output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(Path(file_path).read_text())

    modified = False

    # Update paths if requested
    if update_paths and source_path and target_path:
        content = Path(target_file).read_text()
        updated_content = content.replace(source_path, target_path)
        if content != updated_content:
            Path(target_file).write_text(updated_content)
            print(f"Updated paths in: {target_file}")
            modified = True

    # Update headers and well identifiers if requested
    if update_headers or clean_wells:
        try:
            df = pd.read_csv(target_file)
            headers_modified = False

            # Rename Metadata_SBSCycle to Metadata_Cycle if needed
            if update_headers and "Metadata_SBSCycle" in df.columns:
                df = df.rename(columns={"Metadata_SBSCycle": "Metadata_Cycle"})
                headers_modified = True
                print(
                    f"Renamed Metadata_SBSCycle to Metadata_Cycle in: {target_file}"
                )

            # Remove 'Well' prefix from Metadata_Well values if needed
            if clean_wells and "Metadata_Well" in df.columns:
                orig_wells = df["Metadata_Well"].copy()
                df["Metadata_Well"] = df["Metadata_Well"].apply(
                    lambda x: x[4:]
                    if isinstance(x, str) and x.startswith("Well")
                    else x
                )

                if not orig_wells.equals(df["Metadata_Well"]):
                    headers_modified = True
                    print(f"Cleaned Well identifiers in: {target_file}")

            # Save if modified
            if headers_modified:
                df.to_csv(target_file, index=False)
                modified = True

        except Exception as e:
            print(f"Error processing {target_file}: {e}")

    return modified


def main():
    parser = argparse.ArgumentParser(
        description="Post-process LoadData CSV files"
    )

    parser.add_argument(
        "--input-dir",
        required=True,
        help="Directory containing CSV files to process",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory to save processed files (if different from input)",
    )
    parser.add_argument("--source-path", help="Original path to replace")
    parser.add_argument("--target-path", help="New path to use")
    parser.add_argument(
        "--fixture-id", default="s1", help="Fixture ID (s1, s2, l1)"
    )
    parser.add_argument(
        "--update-paths", action="store_true", help="Update file paths"
    )
    parser.add_argument(
        "--update-headers",
        action="store_true",
        help="Update headers (SBSCycle to Cycle)",
    )
    parser.add_argument(
        "--clean-wells", action="store_true", help="Clean well identifiers"
    )

    args = parser.parse_args()

    # Check if at least one operation is specified
    if not any([args.update_paths, args.update_headers, args.clean_wells]):
        parser.error(
            "At least one operation (--update-paths, --update-headers, --clean-wells) must be specified"
        )

    # Auto-generate paths if needed
    if args.update_paths and not args.target_path:
        repo_root = get_repo_root()
        fixture_id = args.fixture_id
        target_path = (
            f"{repo_root}/scratch/fix_{fixture_id}_pcpip_output/Source1/Batch1/"
        )

        if not args.source_path:
            args.source_path = (
                "/home/ubuntu/bucket/projects/AMD_screening/20231011_batch_1/"
            )

        print(f"Using source path: {args.source_path}")
        print(f"Using target path: {target_path}")
    else:
        target_path = args.target_path

    # Process all CSV files in the input directory
    input_path = Path(args.input_dir)
    csv_files = list(input_path.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in {args.input_dir}")
        return

    print(f"Processing {len(csv_files)} CSV files...")

    # Process each CSV file
    processed_count = 0
    for file in csv_files:
        output_file = (
            Path(args.output_dir) / file.name if args.output_dir else None
        )
        if process_csv_file(
            file,
            output_file,
            args.source_path,
            target_path,
            args.update_paths,
            args.update_headers,
            args.clean_wells,
        ):
            processed_count += 1

    print(f"Processed {processed_count} out of {len(csv_files)} files")


if __name__ == "__main__":
    main()
