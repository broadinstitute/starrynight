"""Test for the StarryNight getting-started workflow LoadData generation steps.

This test module focuses specifically on testing the LoadData generation functionality
of the StarryNight workflow by executing the CLI commands and validating the outputs.

The workflow is outlined in ../../../docs/user/getting-started.md

Current scope:
- CP illum calc LoadData generation
- CP illum apply LoadData generation

Future extensions:
- CP segmentation check LoadData generation
- SBS illum calc LoadData generation
- SBS illum apply LoadData generation
- SBS preprocessing LoadData generation
- Analysis LoadData generation

Testing strategy:
This module uses a parameterized approach to test multiple LoadData generation steps:

1. A single test function that is parameterized with both:
   - Setup approach: full workflow vs. pre-generated files
   - LoadData type: which workflow step to test (illum_calc, illum_apply, etc.)

2. Each LoadData type has its own configuration including:
   - Command parameters (specific to that step)
   - Expected file patterns and naming conventions
   - Required columns for validation
   - Reference CSV paths for comparison
   - Additional validation checks specific to the step

Running the tests:
- Run all tests: pytest test_getting_started_workflow.py
- Run only fast tests: pytest test_getting_started_workflow.py -v -k fast
- Run only full workflow tests: pytest test_getting_started_workflow.py -v -k full
- Run specific LoadData type: pytest test_getting_started_workflow.py -v -k cp_illum_calc
- Run specific LoadData type and setup approach: pytest test_getting_started_workflow.py -v -k "cp_illum_calc and full"
"""

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Optional

import duckdb
import pandas as pd
import pytest

# LoadData type configurations
LOADDATA_CONFIGS = [
    # CP illum calc LoadData configuration
    {
        "name": "cp_illum_calc",
        "command_parts": ["illum", "calc", "loaddata"],
        "output_dir_key": "cp_illum_calc_dir",
        "file_pattern": "Batch1_Plate1_illum_calc.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline1.csv",
        "required_columns": [
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
        ],
        "additional_checks": [],
    },
    # CP illum apply LoadData configuration
    {
        "name": "cp_illum_apply",
        "command_parts": ["illum", "apply", "loaddata"],
        "output_dir_key": "cp_illum_apply_dir",
        "file_pattern": "Batch1_Plate1_*_illum_apply.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline2.csv",
        "required_columns": [
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
            # Additional columns specific to illum_apply
            "FileName_IllumPhalloidin",
            "FileName_IllumZO1",
            "FileName_IllumDNA",
            "PathName_IllumPhalloidin",
            "PathName_IllumZO1",
            "PathName_IllumDNA",
        ],
        "additional_checks": [
            {
                "query": """
                    SELECT COUNT(*) FROM generated
                    WHERE FileName_IllumDNA IS NULL
                    OR FileName_IllumZO1 IS NULL
                    OR FileName_IllumPhalloidin IS NULL
                    OR PathName_IllumDNA IS NULL
                    OR PathName_IllumZO1 IS NULL
                    OR PathName_IllumPhalloidin IS NULL
                """,
                "error_msg": "Found {count} rows missing illumination filename information",
            }
        ],
    },
]


def validate_loaddata_csv(
    generated_csv_path: Path,
    ref_csv_path: Path,
    additional_checks: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Validate a generated LoadData CSV file against a reference CSV file.

    This helper function compares the generated CSV with a reference CSV,
    checking critical elements that must match between the two files.

    The validation focuses on:
    1. Metadata coverage (wells, sites, plates)
    2. Channel frame assignments
    3. Filename pattern correctness
    4. Custom checks specific to the pipeline step

    Args:
        generated_csv_path: Path to the generated LoadData CSV file
        ref_csv_path: Path to the reference LoadData CSV file
        additional_checks: List of additional SQL checks to perform, each with:
            - query: SQL query executing a COUNT that identifies invalid records
            - error_msg: Error message template (can use {count} placeholder)

    The additional_checks should contain SQL queries that:
    - Return a single COUNT of records that fail validation
    - Have access to the "generated" table (the CSV being validated)
    - Return 0 if validation passes, >0 if validation fails

    Example additional checks:
    [
        {
            "query": "SELECT COUNT(*) FROM generated WHERE ImageNumber IS NULL",
            "error_msg": "Found {count} rows missing ImageNumber"
        },
        {
            "query": "SELECT COUNT(*) FROM generated WHERE Metadata_Well NOT LIKE '[A-Z]%'",
            "error_msg": "Found {count} malformed well IDs"
        }
    ]

    Returns:
        List of validation error messages. Empty list if validation passed.

    """
    validation_errors = []

    try:
        # Register both CSVs in a DuckDB in-memory database
        with duckdb.connect(":memory:") as conn:
            # Helper function for count-based validation checks
            def run_count_check(query: str, error_msg_template: str) -> None:
                """Execute a query that returns a count and add error if count > 0."""
                count = conn.execute(query).fetchone()[0]
                if count > 0:
                    validation_errors.append(
                        error_msg_template.format(count=count)
                    )

            # Register CSV data as views
            conn.execute(
                f"CREATE VIEW generated AS SELECT * FROM read_csv_auto('{str(generated_csv_path)}')"
            )
            conn.execute(
                f"CREATE VIEW reference AS SELECT * FROM read_csv_auto('{str(ref_csv_path)}')"
            )

            # Check 1: Compare channel assignments
            # This verifies the relationship between channels and frames is preserved
            channel_frames_sql = """
                SELECT DISTINCT Frame_OrigDNA, Frame_OrigZO1, Frame_OrigPhalloidin
                FROM {table} ORDER BY Frame_OrigDNA, Frame_OrigZO1, Frame_OrigPhalloidin
            """
            ref_channels = conn.execute(
                channel_frames_sql.format(table="reference")
            ).fetchall()
            gen_channels = conn.execute(
                channel_frames_sql.format(table="generated")
            ).fetchall()

            if ref_channels != gen_channels:
                validation_errors.append(
                    f"Channel frame assignments don't match: Reference={ref_channels}, Generated={gen_channels}"
                )

            # Check 2: Compare metadata coverage
            # For each metadata type, ensure all reference values exist in the generated file
            for metadata_col, label in [
                ("Metadata_Well", "wells"),
                ("Metadata_Site", "sites"),
                ("Metadata_Plate", "plates"),
            ]:
                # Get distinct values from both tables
                ref_values = {
                    row[0]
                    for row in conn.execute(
                        f"SELECT DISTINCT {metadata_col} FROM reference"
                    ).fetchall()
                }

                gen_values = {
                    row[0]
                    for row in conn.execute(
                        f"SELECT DISTINCT {metadata_col} FROM generated"
                    ).fetchall()
                }

                # Find values in reference that are missing from generated
                missing_values = ref_values - gen_values
                if missing_values:
                    validation_errors.append(
                        f"Reference {label} {missing_values} not found in generated CSV. "
                        f"Reference values: {sorted(ref_values)}, "
                        f"Generated values: {sorted(gen_values)}"
                    )

            # Check 3: Verify filename patterns
            # Ensure generated filenames follow expected patterns
            run_count_check(
                query="""
                    SELECT COUNT(*) FROM generated
                    WHERE FileName_OrigDNA NOT LIKE '%Channel%'
                    OR FileName_OrigZO1 NOT LIKE '%Channel%'
                    OR FileName_OrigPhalloidin NOT LIKE '%Channel%'
                """,
                error_msg_template="Found {count} filenames that don't match the expected pattern",
            )

            # Check 4: Run any additional pipeline-specific checks
            if additional_checks:
                for i, check in enumerate(additional_checks):
                    # Verify check has required keys
                    if "query" not in check or "error_msg" not in check:
                        validation_errors.append(
                            f"Invalid additional check #{i + 1}: must contain 'query' and 'error_msg' keys"
                        )
                        continue

                    run_count_check(check["query"], check["error_msg"])

    except duckdb.Error as e:
        validation_errors.append(
            f"DuckDB error during CSV validation: {str(e)}"
        )

    return validation_errors


@pytest.mark.parametrize(
    "setup_fixture_name, description",
    [
        ("fix_starrynight_basic_setup", "full workflow"),
        ("fix_starrynight_pregenerated_setup", "pre-generated files"),
    ],
    ids=["full", "fast"],
)
@pytest.mark.parametrize("config", LOADDATA_CONFIGS, ids=lambda c: c["name"])
def test_loaddata_generation(
    setup_fixture_name: str,
    description: str,
    config: dict[str, Any],
    request: pytest.FixtureRequest,
    fix_s1_workspace: dict[str, Path],
    fix_s1_output_dir: dict[str, Path],
) -> None:
    """Test LoadData generation for different workflow steps.

    This test is parameterized to run with:
    1. Different setup approaches (full workflow vs. pre-generated files)
    2. Different LoadData types (illum_calc, illum_apply, etc.)

    Args:
        setup_fixture_name: Name of the fixture to use for setup
        description: Description of the setup approach (for test logs)
        config: Configuration for the specific LoadData type being tested
        request: pytest request object to get the fixture by name
        fix_s1_workspace: Fixture providing workspace directory structure
        fix_s1_output_dir: Fixture providing reference output data for validation

    """
    # Get the appropriate fixture (basic or pre-generated) using the request object
    setup_fixture = request.getfixturevalue(setup_fixture_name)

    # Get paths from the fixture
    index_file = setup_fixture["index_file"]
    experiment_json_path = setup_fixture["experiment_json_path"]

    # Get LoadData type-specific configuration
    loaddata_name = config["name"]
    output_dir_key = config["output_dir_key"]
    file_pattern = config["file_pattern"]
    ref_csv_pattern = config["ref_csv_pattern"]
    required_columns = config["required_columns"]
    command_parts = config["command_parts"]
    additional_checks = config.get("additional_checks", [])

    # Build the command for generating LoadData files
    loaddata_cmd = [
        "starrynight",
        *command_parts,  # e.g., ["illum", "calc", "loaddata"]
        "-i",
        str(index_file),
        "-o",
        str(fix_s1_workspace[output_dir_key]),
        "--exp_config",
        str(experiment_json_path),
        "--use_legacy",
    ]

    # Run the command and check it was successful
    result = subprocess.run(
        loaddata_cmd, capture_output=True, text=True, check=False
    )

    # Check if the command was successful
    assert result.returncode == 0, (
        f"{loaddata_name} LoadData generation command failed: {result.stderr}"
    )

    # Verify LoadData files were created
    loaddata_dir = fix_s1_workspace[output_dir_key]

    # Check for the presence of at least one LoadData CSV file in the directory
    csv_files = list(loaddata_dir.glob("*.csv"))
    assert len(csv_files) > 0, "No LoadData CSV files were created"

    # Check for matching files using pattern
    matching_files = list(loaddata_dir.glob(file_pattern))
    assert len(matching_files) > 0, (
        f"No files matching pattern {file_pattern} were created. "
        f"Found files: {[f.name for f in csv_files]}"
    )

    # Use pandas for CSV file handling - simpler for this test context
    if len(matching_files) == 1:
        # Single file - just read it directly
        df = pd.read_csv(matching_files[0])
    else:
        # Multiple files - concatenate using pandas
        print(
            f"Found {len(matching_files)} files matching pattern {file_pattern}"
        )
        dataframes = []

        # Read each file with error handling
        for file_path in matching_files:
            try:
                dataframes.append(pd.read_csv(file_path))
            except Exception as e:
                print(f"Warning: Error processing file {file_path}: {e}")

        # Concatenate the dataframes
        df = pd.concat(dataframes, ignore_index=True)
        print(f"Combined CSV has {len(df)} rows")

    # Verify required columns exist
    for col in required_columns:
        assert col in df.columns, f"Required column '{col}' missing in CSV"

    # Write to temporary file for validation
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        df.to_csv(temp_path, index=False)

    # Validate the combined data against reference LoadData CSV
    generated_csv_path = temp_path

    # Find the matching reference CSV in the fix_s1_output_dir
    ref_load_data_dir = fix_s1_output_dir["load_data_csv_dir"]
    ref_csv_path = list(ref_load_data_dir.glob(ref_csv_pattern))[0]

    # Use the helper function to validate the LoadData CSV
    validation_errors = validate_loaddata_csv(
        generated_csv_path=generated_csv_path,
        ref_csv_path=ref_csv_path,
        additional_checks=additional_checks,
    )

    # Report any validation errors
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

    # Clean up the temporary file
    try:
        temp_path.unlink()
    except Exception as e:
        print(f"Warning: Failed to delete temporary file {temp_path}: {e}")
