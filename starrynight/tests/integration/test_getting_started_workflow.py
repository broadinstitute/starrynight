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
        "file_pattern": "Batch1_Plate1_*_illum_calc.csv",
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

    This helper function performs common validation checks between different LoadData
    generation tests, including verifying channel assignments, well coverage, site coverage,
    plate information, and filename patterns.

    Args:
        generated_csv_path: Path to the generated LoadData CSV file
        ref_csv_path: Path to the reference LoadData CSV file
        additional_checks: List of additional SQL checks to perform, each defined as a dict with:
            - query: SQL query to execute (should return a single value)
            - error_msg: Error message template (can use {count} placeholder)

    Returns:
        List of validation error messages. Empty list if validation passed.

    """
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

            # 5. Run additional checks if provided
            if additional_checks:
                for check_idx, check in enumerate(additional_checks):
                    query = check["query"]
                    error_msg_template = check["error_msg"]

                    # Execute the custom query
                    count = conn.execute(query).fetchone()[0]

                    if count > 0:
                        # Format the error message with the count
                        error_msg = error_msg_template.format(count=count)
                        validation_errors.append(error_msg)

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
        f"No files matching pattern {file_pattern} were created"
    )

    # Load and potentially concatenate CSV files
    if len(matching_files) == 1:
        # Single file case - just load it directly
        combined_df = pd.read_csv(matching_files[0])
    else:
        # Multiple files case - concatenate them all
        print(
            f"Found {len(matching_files)} files matching pattern {file_pattern}"
        )
        dataframes = [pd.read_csv(f) for f in matching_files]
        combined_df = pd.concat(dataframes, ignore_index=True)
        print(f"Combined dataframe has {len(combined_df)} rows")

    # The combined CSV should contain required metadata columns
    for col in required_columns:
        assert col in combined_df.columns, (
            f"Required column '{col}' missing in CSV"
        )

    # Save the combined data to a temporary file for validation
    import tempfile

    # Create a temporary file for the combined CSV
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        combined_df.to_csv(temp_path, index=False)

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
