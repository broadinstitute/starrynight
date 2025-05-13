#!/usr/bin/env python3

import os
from pathlib import Path

import click
import pandas as pd


def process_csv_file(file_path, base_path):
    """Process a single CSV file."""
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


@click.command()
@click.argument("csv_files", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--base-path",
    type=click.Path(exists=True),
    help="Base path to prepend to file paths",
)
def main(csv_files, base_path):
    """Process CSV files containing PathName and FileName columns.

    Creates a melted dataframe with paths and checks file existence.
    """
    all_results = []

    for csv_file in csv_files:
        click.echo(f"Processing {csv_file}...")
        result_df = process_csv_file(csv_file, base_path)

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


if __name__ == "__main__":
    main()
