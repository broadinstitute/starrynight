#!/usr/bin/env python3

from pathlib import Path
from typing import Optional

import click
import pandas as pd


def filter_csv_by_metadata(
    df: pd.DataFrame,
    plate_values: list[str] | None = None,
    well_values: list[str] | None = None,
    site_values: list[str] | None = None,
    cycle_values: list[str] | None = None,
) -> tuple[pd.DataFrame, dict]:
    """Filter a LoadData CSV DataFrame based on metadata values.

    Parameters
    ----------
    df : pd.DataFrame
        The LoadData CSV as a pandas DataFrame
    plate_values : Optional[List[str]]
        List of plate values to keep
    well_values : Optional[List[str]]
        List of well values to keep
    site_values : Optional[List[str]]
        List of site values to keep
    cycle_values : Optional[List[str]]
        List of cycle values to keep

    Returns
    -------
    Tuple[pd.DataFrame, dict]
        The filtered DataFrame and a dictionary with filtering statistics

    """
    original_rows = len(df)
    original_cols = len(df.columns)

    stats = {
        "original_rows": original_rows,
        "original_columns": original_cols,
    }

    # Filter by plate values
    if plate_values and "Metadata_Plate" in df.columns:
        df = df[df["Metadata_Plate"].isin(plate_values)]

    # Filter by well values
    if well_values and "Metadata_Well" in df.columns:
        df = df[df["Metadata_Well"].isin(well_values)]

    # Filter by site values
    if site_values and "Metadata_Site" in df.columns:
        df = df[
            df["Metadata_Site"].astype(str).isin([str(s) for s in site_values])
        ]

    # Filter by cycle values
    if cycle_values:
        # Method 1: Filter by Metadata_SBSCycle column if it exists
        if "Metadata_SBSCycle" in df.columns:
            df = df[
                df["Metadata_SBSCycle"]
                .astype(str)
                .isin([str(c) for c in cycle_values])
            ]

        # Method 2: Filter columns with cycle information in their names
        cycle_pattern_strings = [
            f"_Cycle{str(c).zfill(2)}_" for c in cycle_values
        ]

        # Keep columns that don't have cycle information or match specified cycles
        columns_to_keep = []
        for col in df.columns:
            # Check if this column has cycle information
            has_cycle_info = any(
                f"_Cycle{str(i).zfill(2)}_" in col for i in range(100)
            )

            if not has_cycle_info or any(
                pattern in col for pattern in cycle_pattern_strings
            ):
                columns_to_keep.append(col)

        df = df[columns_to_keep]

    stats["filtered_rows"] = len(df)
    stats["filtered_columns"] = len(df.columns)
    stats["rows_removed"] = original_rows - len(df)
    stats["columns_removed"] = original_cols - len(df.columns)

    return df, stats


@click.command()
@click.option(
    "--input-csv",
    required=True,
    type=click.Path(exists=True),
    help="Path to the input CSV file",
)
@click.option(
    "--output-csv",
    required=True,
    type=click.Path(),
    help="Path where the filtered CSV will be saved",
)
@click.option("--plate", help="Comma-separated list of plate values to keep")
@click.option("--well", help="Comma-separated list of well values to keep")
@click.option("--site", help="Comma-separated list of site values to keep")
@click.option("--cycle", help="Comma-separated list of cycle values to keep")
def main(
    input_csv: str,
    output_csv: str,
    plate: str,
    well: str,
    site: str,
    cycle: str,
) -> None:
    """Filter a LoadData CSV file to create a smaller dataset with only specific metadata values."""
    # Convert comma-separated strings to lists
    plate_values = plate.split(",") if plate else None
    well_values = well.split(",") if well else None
    site_values = site.split(",") if site else None
    cycle_values = cycle.split(",") if cycle else None

    # Read the input CSV
    input_path = Path(input_csv)
    df = pd.read_csv(input_path)

    # Filter the DataFrame
    filtered_df, stats = filter_csv_by_metadata(
        df, plate_values, well_values, site_values, cycle_values
    )

    # Save the filtered DataFrame
    output_path = Path(output_csv)
    filtered_df.to_csv(output_path, index=False)

    # Report statistics
    click.echo("Filtering results:")
    click.echo(
        f"  Original: {stats['original_rows']} rows, {stats['original_columns']} columns"
    )
    click.echo(
        f"  Filtered: {stats['filtered_rows']} rows, {stats['filtered_columns']} columns"
    )
    click.echo(
        f"  Removed:  {stats['rows_removed']} rows, {stats['columns_removed']} columns"
    )
    click.echo(f"Saved filtered CSV to {output_path}")


if __name__ == "__main__":
    main()
