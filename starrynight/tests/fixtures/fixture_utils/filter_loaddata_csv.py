#!/usr/bin/env python3
import argparse
import glob
import os
from pathlib import Path

import pandas as pd


def process_csv_file(csv_path, filter_criteria, output_dir):
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
        base_name = Path.name(csv_path)
        output_path = Path.joinpath(output_dir, base_name)

        # Save trimmed dataframe
        df_trimmed.to_csv(output_path, index=False)
        print(f"Processed {csv_path} -> {output_path}")
        print(f"  - Columns: {len(df.columns)} → {len(df_trimmed.columns)}")
        print(f"  - Rows: {original_row_count} → {filtered_row_count}")

        return output_path
    except Exception as e:
        print(f"Error processing {csv_path}: {str(e)}")
        return None


def parse_filter_values(value_str):
    """Parse comma-separated filter values into a list."""
    if not value_str:
        return []
    return [val.strip() for val in value_str.split(",")]


def main():
    parser = argparse.ArgumentParser(
        description="Trim CSV files based on filter criteria"
    )
    parser.add_argument(
        "directory_path", help="Directory containing CSV files to process"
    )
    parser.add_argument(
        "output_directory",
        help="Directory where trimmed CSV files will be saved",
    )
    parser.add_argument(
        "--well", help="Comma-separated list of well values to keep"
    )
    parser.add_argument(
        "--site", help="Comma-separated list of site values to keep"
    )
    parser.add_argument(
        "--plate", help="Comma-separated list of plate values to keep"
    )
    parser.add_argument(
        "--cycle", help="Comma-separated list of cycle values to keep"
    )

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    Path(args.output_directory).mkdir(parents=True, exist_ok=True)
    print(f"Output will be saved to: {args.output_directory}")

    # Parse filter criteria
    filter_criteria = {
        "Metadata_Well": parse_filter_values(args.well),
        "Metadata_Site": parse_filter_values(args.site),
        "Metadata_Plate": parse_filter_values(args.plate),
        "Metadata_SBSCycle": parse_filter_values(args.cycle),
    }

    # Print filter criteria
    for col, values in filter_criteria.items():
        if values:
            print(f"Filtering {col}: keeping {values}")

    # Find all CSV files in the directory
    csv_files = Path.glob(Path.joinpath(args.directory_path, "*.csv"))
    print(f"Found {len(csv_files)} CSV files to process")

    # Process each CSV file
    processed_files = []
    for csv_file in csv_files:
        output_file = process_csv_file(
            csv_file, filter_criteria, args.output_directory
        )
        if output_file:
            processed_files.append(output_file)

    print(f"Successfully processed {len(processed_files)} files")


if __name__ == "__main__":
    main()
