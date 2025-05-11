"""Test for the StarryNight getting-started workflow steps.

This test module verifies the core functionality of the StarryNight getting-started
workflow by executing the actual CLI commands and verifying their outputs.

The workflow is outlined in ../../../docs/user/getting-started.md

Current scope:
- Experiment configuration initialization and editing
- Inventory file generation

Future extensions:
- Index generation from inventory (parsing file paths)
- Experiment file creation from index and configuration
- LoadData CSV generation for illumination correction
- CellProfiler pipeline generation
- Illumination correction execution

Testing strategy:
This module executes each StarryNight CLI command directly to test the actual
functionality of the workflow. This strategy:
1. Ensures the CLI commands work as expected
2. Tests the complete end-to-end workflow as a user would experience it
3. Validates that each workflow step produces the expected outputs
4. Allows for incremental testing as the workflow gets extended

Each workflow step is executed in sequence with appropriate assertions to
verify the correctness of outputs. The test uses the FIX-S1 input and workspace
fixtures for consistent and reusable test data.
"""

import json
import re
import subprocess
from pathlib import Path

import duckdb
import pandas as pd
import pytest


def test_loaddata_generation(
    fix_starrynight_basic_setup, fix_s1_workspace, fix_s1_output_dir
):
    """Test the LoadData generation step of the getting-started workflow.

    This test focuses on step 6 of the workflow, using the fix_starrynight_basic_setup
    fixture to provide the necessary files from steps 1-5:

    6. Generate LoadData files for illumination correction
    7. Validate the generated LoadData CSV matches the reference LoadData CSV

    Args:
        fix_starrynight_basic_setup: Fixture providing initial setup (through steps 1-5)
        fix_s1_workspace: Fixture providing workspace directory structure with expected paths
        fix_s1_output_dir: Fixture providing reference output data for validation

    """
    # Get paths from the fixture
    index_file = fix_starrynight_basic_setup["index_file"]
    experiment_json_path = fix_starrynight_basic_setup["experiment_json_path"]

    # Generate LoadData files for illumination correction
    illum_calc_loaddata_cmd = [
        "starrynight",
        "illum",
        "calc",
        "loaddata",
        "-i",
        str(index_file),
        "-o",
        str(fix_s1_workspace["cp_illum_calc_dir"]),
        "--exp_config",
        str(experiment_json_path),
        "--use_legacy",
    ]

    # Run the command and check it was successful
    result = subprocess.run(
        illum_calc_loaddata_cmd, capture_output=True, text=True, check=False
    )

    # Check if the command was successful
    assert result.returncode == 0, (
        f"Illumination LoadData generation command failed: {result.stderr}"
    )

    # Verify LoadData files were created
    loaddata_dir = fix_s1_workspace["cp_illum_calc_dir"]

    # Check for the presence of at least one LoadData CSV file in the directory
    csv_files = list(loaddata_dir.glob("*.csv"))
    assert len(csv_files) > 0, "No LoadData CSV files were created"

    # Check for plate-specific CSV files (should be created for each plate)
    plate_csvs = list(loaddata_dir.glob("*Plate*_illum_calc.csv"))
    assert len(plate_csvs) > 0, "No plate-specific CSV files were created"

    # Verify the content of a plate-specific CSV file
    plate_csv = plate_csvs[0]
    df = pd.read_csv(plate_csv)

    # The CSV file should contain required metadata columns
    required_columns = [
        "Metadata_Batch",
        "Metadata_Plate",
        "Metadata_Well",
        "Metadata_Site",
        "FileName_OrigPhalloidin",
        "FileName_OrigZO1",
        "FileName_OrigDNA",
        "PathName_OrigPhalloidin",
        "PathName_OrigZO1",
        "PathName_OrigDNA",
    ]
    for col in required_columns:
        assert col in df.columns, f"Required column '{col}' missing in CSV"

    # Step 8: Validate the generated LoadData CSV against reference LoadData CSV
    # Define paths to the generated and reference CSV files
    generated_csv_path = plate_csvs[0]  # Use the first plate-specific CSV

    # Find the matching reference CSV in the fix_s1_output_dir
    ref_load_data_dir = fix_s1_output_dir["load_data_csv_dir"]
    ref_csv_path = list(
        ref_load_data_dir.glob("**/Plate1_trimmed/load_data_pipeline1.csv")
    )[0]

    # Load both CSV files with DuckDB using context manager for simplified validation
    # Collect all validation errors instead of stopping at first failure
    validation_errors = []

    try:
        # Use context manager for proper resource handling
        with duckdb.connect(":memory:") as conn:
            # Register CSV files as views using read_csv_auto for automatic type inference
            conn.execute(
                f"CREATE VIEW generated AS SELECT * FROM read_csv_auto('{str(generated_csv_path)}')"
            )
            conn.execute(
                f"CREATE VIEW reference AS SELECT * FROM read_csv_auto('{str(ref_csv_path)}')"
            )

            # 1. Verify channel frame assignments match between the CSVs
            ref_channels = conn.execute("""
                SELECT DISTINCT Frame_OrigDNA, Frame_OrigZO1, Frame_OrigPhalloidin
                FROM reference
                ORDER BY Frame_OrigDNA, Frame_OrigZO1, Frame_OrigPhalloidin
            """).fetchall()

            gen_channels = conn.execute("""
                SELECT DISTINCT Frame_OrigDNA, Frame_OrigZO1, Frame_OrigPhalloidin
                FROM generated
                ORDER BY Frame_OrigDNA, Frame_OrigZO1, Frame_OrigPhalloidin
            """).fetchall()

            if ref_channels != gen_channels:
                validation_errors.append(
                    f"Channel frame assignments don't match: Reference={ref_channels}, Generated={gen_channels}"
                )

            # 2. Verify all wells from reference exist in generated file
            ref_wells_rows = conn.execute(
                "SELECT DISTINCT Metadata_Well FROM reference"
            ).fetchall()
            gen_wells_rows = conn.execute(
                "SELECT DISTINCT Metadata_Well FROM generated"
            ).fetchall()

            # Convert to sets of values (extracting first column from each row)
            ref_wells = {row[0] for row in ref_wells_rows}
            gen_wells = {row[0] for row in gen_wells_rows}

            missing_wells = ref_wells - gen_wells
            if missing_wells:
                validation_errors.append(
                    f"Reference wells {missing_wells} not found in generated CSV. "
                    f"Reference values: {sorted(ref_wells)}, "
                    f"Generated values: {sorted(gen_wells)}"
                )

            # 2b. Verify all sites from reference exist in generated file
            ref_sites_rows = conn.execute(
                "SELECT DISTINCT Metadata_Site FROM reference"
            ).fetchall()
            gen_sites_rows = conn.execute(
                "SELECT DISTINCT Metadata_Site FROM generated"
            ).fetchall()

            # Convert to sets of values (extracting first column from each row)
            ref_sites = {row[0] for row in ref_sites_rows}
            gen_sites = {row[0] for row in gen_sites_rows}

            missing_sites = ref_sites - gen_sites
            if missing_sites:
                validation_errors.append(
                    f"Reference sites {missing_sites} not found in generated CSV. "
                    f"Reference values: {sorted(list(ref_sites))}, "
                    f"Generated values: {sorted(list(gen_sites))}"
                )

            # 3. Verify plate information matches
            ref_plates_rows = conn.execute(
                "SELECT DISTINCT Metadata_Plate FROM reference"
            ).fetchall()
            gen_plates_rows = conn.execute(
                "SELECT DISTINCT Metadata_Plate FROM generated"
            ).fetchall()

            # Convert to sets of values
            ref_plates = {row[0] for row in ref_plates_rows}
            gen_plates = {row[0] for row in gen_plates_rows}

            missing_plates = ref_plates - gen_plates
            if missing_plates:
                validation_errors.append(
                    f"Reference plates {missing_plates} not found in generated CSV. "
                    f"Reference values: {sorted(list(ref_plates))}, "
                    f"Generated values: {sorted(list(gen_plates))}"
                )

            # 4. Verify filename patterns
            filename_pattern_check = conn.execute("""
                SELECT COUNT(*) FROM generated
                WHERE FileName_OrigDNA NOT LIKE '%Channel%'
                OR FileName_OrigZO1 NOT LIKE '%Channel%'
                OR FileName_OrigPhalloidin NOT LIKE '%Channel%'
            """).fetchone()[0]

            if filename_pattern_check > 0:
                validation_errors.append(
                    f"Found {filename_pattern_check} filenames that don't match the expected pattern"
                )

            # After collecting all errors, report them if any exist
            if validation_errors:
                error_message = "\n".join(
                    [
                        f"Validation error {i + 1}: {error}"
                        for i, error in enumerate(validation_errors)
                    ]
                )
                pytest.fail(
                    f"CSV validation failed with {len(validation_errors)} error(s):\n{error_message}"
                )

    except duckdb.Error as e:
        pytest.fail(f"DuckDB error during CSV validation: {str(e)}")
