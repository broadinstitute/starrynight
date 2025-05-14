#!/usr/bin/env python3
"""Utilities for working with CellProfiler LoadData CSV files.

This script combines functionality for:
1. Validating paths in LoadData CSVs
2. Post-processing LoadData CSVs (updating paths, headers, well identifiers)
3. Filtering LoadData CSVs based on criteria
"""

import subprocess
import sys
from pathlib import Path

import click
import pandas as pd

# -------------------------------------------------------------------------
# Validate LoadData Paths Functions (from validate_loaddata_paths.py)
# -------------------------------------------------------------------------


def validate_process_csv_file(file_path, base_path):
    """Process a single CSV file and check path existence."""
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Find PathName and FileName column pairs
    pathname_columns = [
        col for col in df.columns if col.startswith("PathName_")
    ]
    channels = [col.replace("PathName_", "") for col in pathname_columns]

    # Create FilePathName columns by joining PathName and FileName columns
    filepathname_dfs = []
    for channel in channels:
        if f"FileName_{channel}" in df.columns:
            # Join path and filename to create full path
            df[f"FilePathName_{channel}"] = (
                df[f"PathName_{channel}"].str.rstrip("/")
                + "/"
                + df[f"FileName_{channel}"]
            )

            # Select only the created column and "melt" it
            channel_df = df[[f"FilePathName_{channel}"]].copy()
            channel_df["Channel"] = channel
            channel_df = channel_df.rename(
                columns={f"FilePathName_{channel}": "FilePath"}
            )

            filepathname_dfs.append(channel_df)

    # Concatenate all melted dataframes
    if filepathname_dfs:
        result_df = pd.concat(filepathname_dfs, ignore_index=True)

        # Add base_path to make paths relative if provided
        if base_path:
            base_path_obj = Path(base_path)
            result_df["FilePath"] = result_df["FilePath"].apply(
                lambda x: base_path_obj / x
            )

        # Check which files exist
        result_df["FileExists"] = result_df["FilePath"].apply(
            lambda x: Path(x).exists()
        )

        return result_df

    return None


# -------------------------------------------------------------------------
# Post-Process LoadData CSV Functions (from postprocess_loaddata_csv.py)
# -------------------------------------------------------------------------


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


def postprocess_csv_file(
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


# -------------------------------------------------------------------------
# Filter LoadData CSV Functions (from filter_loaddata_csv.py)
# -------------------------------------------------------------------------


def parse_filter_values(value_str):
    """Parse comma-separated filter values into a list."""
    if not value_str:
        return []
    return [val.strip() for val in value_str.split(",")]


def filter_process_csv_file(csv_path, filter_criteria, output_dir):
    """Process a single CSV file and keep only required columns and rows matching filter criteria."""
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)

        # Keep all columns from the original CSV
        df_trimmed = df

        # Apply filters if specified
        original_row_count = len(df_trimmed)
        for col, values in filter_criteria.items():
            if col in df_trimmed.columns and values:
                # Convert both column and filter values to strings for comparison
                df_trimmed = df_trimmed[
                    df_trimmed[col].astype(str).isin([str(v) for v in values])
                ]

        # Drop columns that match the pattern *_Cycle{%02dcycle}_* for specified cycle values
        cycle_values = filter_criteria.get("Metadata_SBSCycle", [])
        if cycle_values:
            # First identify all cycle columns
            all_cycle_columns = []
            patterns_to_keep = []

            # Create patterns for cycles we want to keep
            for cycle in cycle_values:
                try:
                    cycle_pattern = f"_Cycle{int(cycle):02d}_"
                    patterns_to_keep.append(cycle_pattern)
                except (ValueError, TypeError):
                    print(f"Warning: Invalid cycle value: {cycle}")

            # Find all columns that have any cycle pattern
            for col in df_trimmed.columns:
                if any(
                    f"_Cycle{i:02d}_" in col for i in range(100)
                ):  # Check for Cycle00-Cycle99
                    all_cycle_columns.append(col)

            # Keep only cycle columns that match our patterns
            columns_to_drop = []
            for col in all_cycle_columns:
                if not any(pattern in col for pattern in patterns_to_keep):
                    columns_to_drop.append(col)

            if columns_to_drop:
                df_trimmed = df_trimmed.drop(columns=columns_to_drop)
                print(
                    f"  - Dropped {len(columns_to_drop)} cycle columns that didn't match cycles {cycle_values}"
                )

        filtered_row_count = len(df_trimmed)

        # Create output filename
        path_obj = Path(csv_path)
        base_name = path_obj.name
        output_path = Path(output_dir) / base_name

        # Save trimmed dataframe
        df_trimmed.to_csv(output_path, index=False)
        print(f"Processed {csv_path} -> {output_path}")
        print(f"  - Columns: {len(df.columns)} → {len(df_trimmed.columns)}")
        print(f"  - Rows: {original_row_count} → {filtered_row_count}")

        return output_path
    except Exception as e:
        print(f"Error processing {csv_path}: {str(e)}")
        return None


# -------------------------------------------------------------------------
# Command-line interface
# -------------------------------------------------------------------------


@click.group()
def cli():
    """Work with CellProfiler LoadData CSV files."""
    pass


@cli.command("validate")
@click.argument("csv_files", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--base-path",
    type=click.Path(exists=True),
    help="Base path to prepend to file paths",
)
def validate_command(csv_files, base_path):
    """Process CSV files containing PathName and FileName columns.

    Creates a melted dataframe with paths and checks file existence.
    """
    all_results = []

    for csv_file in csv_files:
        click.echo(f"Processing {csv_file}...")
        result_df = validate_process_csv_file(csv_file, base_path)

        if result_df is not None:
            all_results.append(result_df)

            # Print summary for this file
            missing_files = result_df[~result_df["FileExists"]]
            if not missing_files.empty:
                click.echo(
                    f"Found {len(missing_files)} missing files in {csv_file}"
                )
            else:
                click.echo(f"All files in {csv_file} exist")
        else:
            click.echo(f"No PathName/FileName pairs found in {csv_file}")

    # Combine all results if there are any
    if all_results:
        combined_df = pd.concat(all_results, ignore_index=True)
        missing_files_df = combined_df[~combined_df["FileExists"]]

        click.echo("\nSummary:")
        click.echo(f"Total files: {len(combined_df)}")
        click.echo(f"Missing files: {len(missing_files_df)}")

        # Save missing files to CSV if any are found
        if not missing_files_df.empty:
            output_file = "missing_files.csv"
            missing_files_df.to_csv(output_file, index=False)
            click.echo(f"Missing files saved to {output_file}")


@cli.command("postprocess")
@click.option(
    "--input-dir",
    required=True,
    help="Directory containing CSV files to process",
    type=click.Path(exists=True),
)
@click.option(
    "--output-dir",
    help="Directory to save processed files (if different from input)",
    type=click.Path(),
)
@click.option("--source-path", help="Original path to replace")
@click.option("--target-path", help="New path to use")
@click.option("--fixture-id", default="s1", help="Fixture ID (s1, s2, l1)")
@click.option("--update-paths", is_flag=True, help="Update file paths")
@click.option(
    "--update-headers",
    is_flag=True,
    help="Update headers (SBSCycle to Cycle)",
)
@click.option("--clean-wells", is_flag=True, help="Clean well identifiers")
def postprocess_command(
    input_dir,
    output_dir,
    source_path,
    target_path,
    fixture_id,
    update_paths,
    update_headers,
    clean_wells,
):
    """Post-process LoadData CSV files.

    Updates file paths, headers, and well identifiers.
    """
    # Check if at least one operation is specified
    if not any([update_paths, update_headers, clean_wells]):
        click.echo(
            "Error: At least one operation (--update-paths, --update-headers, --clean-wells) must be specified"
        )
        sys.exit(1)

    # Auto-generate paths if needed
    if update_paths and not target_path:
        repo_root = get_repo_root()
        target_path = (
            f"{repo_root}/scratch/fix_{fixture_id}_pcpip_output/Source1/Batch1/"
        )

        if not source_path:
            source_path = (
                "/home/ubuntu/bucket/projects/AMD_screening/20231011_batch_1/"
            )

        click.echo(f"Using source path: {source_path}")
        click.echo(f"Using target path: {target_path}")

    # Process all CSV files in the input directory
    input_path = Path(input_dir)
    csv_files = list(input_path.glob("*.csv"))

    if not csv_files:
        click.echo(f"No CSV files found in {input_dir}")
        return

    click.echo(f"Processing {len(csv_files)} CSV files...")

    # Process each CSV file
    processed_count = 0
    for file in csv_files:
        output_file = Path(output_dir) / file.name if output_dir else None
        if postprocess_csv_file(
            file,
            output_file,
            source_path,
            target_path,
            update_paths,
            update_headers,
            clean_wells,
        ):
            processed_count += 1

    click.echo(f"Processed {processed_count} out of {len(csv_files)} files")


@cli.command("filter")
@click.argument("directory_path", type=click.Path(exists=True))
@click.argument("output_directory", type=click.Path())
@click.option("--well", help="Comma-separated list of well values to keep")
@click.option("--site", help="Comma-separated list of site values to keep")
@click.option("--plate", help="Comma-separated list of plate values to keep")
@click.option("--cycle", help="Comma-separated list of cycle values to keep")
def filter_command(directory_path, output_directory, well, site, plate, cycle):
    """Filter CSV files based on criteria.

    Filters rows by well, site, plate, and cycle values.
    """
    # Create output directory if it doesn't exist
    Path(output_directory).mkdir(parents=True, exist_ok=True)
    click.echo(f"Output will be saved to: {output_directory}")

    # Parse filter criteria
    filter_criteria = {
        "Metadata_Well": parse_filter_values(well),
        "Metadata_Site": parse_filter_values(site),
        "Metadata_Plate": parse_filter_values(plate),
        "Metadata_SBSCycle": parse_filter_values(cycle),
    }

    # Print filter criteria
    for col, values in filter_criteria.items():
        if values:
            click.echo(f"Filtering {col}: keeping {values}")

    # Find all CSV files in the directory
    path_obj = Path(directory_path)
    csv_files = list(path_obj.glob("*.csv"))
    click.echo(f"Found {len(csv_files)} CSV files to process")

    # Process each CSV file
    processed_files = []
    for csv_file in csv_files:
        output_file = filter_process_csv_file(
            csv_file, filter_criteria, output_directory
        )
        if output_file:
            processed_files.append(output_file)

    click.echo(f"Successfully processed {len(processed_files)} files")


# For backward compatibility with direct script usage
def main():
    """Entry point for command-line use."""
    # Check if we're invoked with a subcommand, otherwise guess intent
    if len(sys.argv) > 1 and sys.argv[1] in [
        "validate",
        "postprocess",
        "filter",
    ]:
        cli()
    else:
        # Attempt to determine which command was intended based on arguments
        if "--base-path" in sys.argv:
            # validate_loaddata_paths.py signature
            # Convert original CLI (click) to our subcommand format
            sys.argv.insert(1, "validate")
            cli()
        elif "--input-dir" in sys.argv:
            # postprocess_loaddata_csv.py signature
            sys.argv.insert(1, "postprocess")
            cli()
        elif len(sys.argv) >= 3 and all(
            arg.startswith("--") is False for arg in sys.argv[1:3]
        ):
            # filter_loaddata_csv.py signature (2 positional args followed by options)
            sys.argv.insert(1, "filter")
            cli()
        else:
            # Default to showing help if we can't determine intent
            sys.argv.insert(1, "--help")
            cli()


if __name__ == "__main__":
    main()
