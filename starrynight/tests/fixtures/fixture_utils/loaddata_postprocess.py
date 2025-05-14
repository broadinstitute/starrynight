#!/usr/bin/env python3

from pathlib import Path

import click
import pandas as pd


def process_csv_paths_and_metadata(
    df: pd.DataFrame, source_path: str, target_path: str
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Process a LoadData CSV DataFrame to update paths and metadata.

    Parameters
    ----------
    df : pd.DataFrame
        The LoadData CSV as a pandas DataFrame
    source_path : str
        Original path prefix to replace
    target_path : str
        New path prefix to use

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, int]]
        The processed DataFrame and a dictionary with processing statistics

    """
    stats = {
        "path_columns_updated": 0,
        "renamed_metadata_sbscycle": 0,
        "well_values_modified": 0,
    }

    # Replace path prefixes in PathName_* columns
    path_columns = [col for col in df.columns if col.startswith("PathName_")]
    for col in path_columns:
        # Replace paths that start with the source path
        mask = df[col].str.startswith(source_path)
        if mask.any():
            df.loc[mask, col] = df.loc[mask, col].str.replace(
                source_path, target_path, regex=False
            )
            stats["path_columns_updated"] += 1

    # Rename Metadata_SBSCycle to Metadata_Cycle if it exists
    if "Metadata_SBSCycle" in df.columns:
        df.rename(columns={"Metadata_SBSCycle": "Metadata_Cycle"}, inplace=True)
        stats["renamed_metadata_sbscycle"] = 1

    # Remove "Well" prefix from Metadata_Well values
    if "Metadata_Well" in df.columns:
        mask = df["Metadata_Well"].str.startswith("Well")
        if mask.any():
            df.loc[mask, "Metadata_Well"] = df.loc[
                mask, "Metadata_Well"
            ].str.replace("Well", "", regex=False)
            stats["well_values_modified"] = mask.sum()

    return df, stats


@click.command()
@click.option(
    "--input-csv",
    required=True,
    type=click.Path(exists=True),
    help="Path to input CSV file",
)
@click.option(
    "--output-csv",
    required=True,
    type=click.Path(),
    help="Path to save processed file",
)
@click.option(
    "--source-path",
    required=True,
    type=str,
    help="Original path prefix to replace",
)
@click.option(
    "--target-path", required=True, type=str, help="New path prefix to use"
)
def main(
    input_csv: str, output_csv: str, source_path: str, target_path: str
) -> None:
    """Update LoadData CSV files to work in a local testing environment.

    This script processes a LoadData CSV file by:
    1. Replacing absolute paths (using source and target paths)
    2. Renaming "Metadata_SBSCycle" column to "Metadata_Cycle"
    3. Removing "Well" prefix from values in "Metadata_Well" column
    """
    # Read the input CSV
    input_path = Path(input_csv)
    df = pd.read_csv(input_path)

    # Process the DataFrame
    processed_df, stats = process_csv_paths_and_metadata(
        df, source_path, target_path
    )

    # Save the processed DataFrame
    output_path = Path(output_csv)
    processed_df.to_csv(output_path, index=False)

    # Report changes
    click.echo("Processing results:")
    click.echo(f"  Path columns updated: {stats['path_columns_updated']}")
    click.echo(
        f"  Renamed 'Metadata_SBSCycle' to 'Metadata_Cycle': {'Yes' if stats['renamed_metadata_sbscycle'] else 'No'}"
    )
    click.echo(
        f"  'Well' prefix removed from {stats['well_values_modified']} values"
    )
    click.echo(f"Saved processed CSV to {output_path}")


if __name__ == "__main__":
    main()
