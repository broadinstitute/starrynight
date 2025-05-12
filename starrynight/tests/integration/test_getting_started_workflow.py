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
    metadata_checks: list[dict[str, Any]] | None = None,
    custom_value_checks: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Validate a generated LoadData CSV file against a reference CSV file.

    This helper function compares the generated CSV with a reference CSV,
    checking critical elements that must match between the two files.

    The validation focuses on:
    1. Metadata coverage (wells, sites, plates)
    2. Channel frame assignments
    3. Standard quality checks (filename patterns, etc.)
    4. Custom checks specific to the pipeline step

    Args:
        generated_csv_path: Path to the generated LoadData CSV file
        ref_csv_path: Path to the reference LoadData CSV file
        additional_checks: List of additional SQL count-based checks to perform, each with:
            - query: SQL query executing a COUNT that identifies invalid records
            - error_msg: Error message template (can use {count} placeholder)
        metadata_checks: Optional custom metadata value coverage checks
        custom_value_checks: Optional additional value coverage checks for columns

    Standard count-based checks and additional checks follow the same format:
    - Return a single COUNT of records that fail validation
    - Have access to the "generated" table (the CSV being validated)
    - Return 0 if validation passes, >0 if validation fails
    - Use "{count}" in the error message to include the count of failing records

    Value coverage checks can be customized to validate:
    - Single columns or composite keys (multiple columns together)
    - Exact matches, subsets, or supersets between reference and generated values
    - Custom error messages with formatted values

    Example value coverage check:
    [
        {
            "columns": ["Metadata_Plate", "Metadata_Well"], # Can be string for single column
            "label": "plate-well combinations",
            "mode": "subset", # "subset" (default), "superset", or "exact"
            "error_msg_template": "Custom error format: {missing_values}"
        }
    ]

    Example additional count checks:
    [
        # Basic missing field check
        {
            "query": "SELECT COUNT(*) FROM generated WHERE ImageNumber IS NULL",
            "error_msg": "Found {count} rows missing ImageNumber"
        },

        # Pattern validation check
        {
            "query": "SELECT COUNT(*) FROM generated WHERE Metadata_Well NOT LIKE '[A-Z]%'",
            "error_msg": "Found {count} rows with malformed well IDs"
        },
    ]

    Returns:
        List of validation error messages. Empty list if validation passed.

    """
    # Extract standard checks and combine with additional checks
    standard_checks, all_count_checks = _get_validation_checks(
        additional_checks
    )

    # Perform validation and collect errors
    return _perform_validation(
        generated_csv_path,
        ref_csv_path,
        all_count_checks,
        metadata_checks,
        custom_value_checks,
    )


def _get_validation_checks(
    additional_checks: list[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Create standard validation checks and combine with additional checks.

    Args:
        additional_checks: Optional list of additional checks to include

    Returns:
        Tuple containing (standard_checks, all_checks_combined)

    """
    # Define standard count-based checks
    standard_checks = [
        # Filename pattern check
        {
            "query": """
                SELECT COUNT(*) FROM generated
                WHERE FileName_OrigDNA NOT LIKE '%Channel%'
                OR FileName_OrigZO1 NOT LIKE '%Channel%'
                OR FileName_OrigPhalloidin NOT LIKE '%Channel%'
            """,
            "error_msg": "Found {count} filenames that don't match the expected pattern",
        },
        # Metadata completeness check
        {
            "query": """
                SELECT COUNT(*) FROM generated
                WHERE Metadata_Batch IS NULL
                OR Metadata_Plate IS NULL
                OR Metadata_Well IS NULL
                OR Metadata_Site IS NULL
            """,
            "error_msg": "Found {count} rows with missing metadata fields",
        },
        # Path and filename completeness check
        {
            "query": """
                SELECT COUNT(*) FROM generated
                WHERE FileName_OrigDNA IS NULL
                OR FileName_OrigZO1 IS NULL
                OR FileName_OrigPhalloidin IS NULL
                OR PathName_OrigDNA IS NULL
                OR PathName_OrigZO1 IS NULL
                OR PathName_OrigPhalloidin IS NULL
            """,
            "error_msg": "Found {count} rows with missing filename or pathname information",
        },
    ]

    # Combine standard and additional checks
    all_count_checks = standard_checks.copy()
    if additional_checks:
        all_count_checks.extend(additional_checks)

    return standard_checks, all_count_checks


def _perform_validation(
    generated_csv_path: Path,
    ref_csv_path: Path,
    all_count_checks: list[dict[str, Any]],
    metadata_checks: list[dict[str, Any]] | None = None,
    custom_value_checks: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Execute validation checks between generated and reference CSVs.

    Args:
        generated_csv_path: Path to the generated CSV to validate
        ref_csv_path: Path to the reference CSV for comparison
        all_count_checks: List of validation checks to perform
        metadata_checks: Optional custom metadata checks (defaults to standard checks)
        custom_value_checks: Optional additional value coverage checks

    Returns:
        List of validation error messages (empty if validation passed)

    """
    validation_errors = []

    try:
        # Register both CSVs in a DuckDB in-memory database
        with duckdb.connect(":memory:") as conn:
            # Register CSV data as views
            conn.execute(
                f"CREATE VIEW generated AS SELECT * FROM read_csv_auto('{str(generated_csv_path)}')"
            )
            conn.execute(
                f"CREATE VIEW reference AS SELECT * FROM read_csv_auto('{str(ref_csv_path)}')"
            )

            # Check 1: Compare channel-frame assignments for consistency
            _check_reference_consistency(conn, validation_errors)

            # Check 2: Compare metadata values for complete coverage
            if metadata_checks is not None:
                # Use custom metadata checks if provided
                for check in metadata_checks:
                    check_value_coverage(
                        conn=conn,
                        validation_errors=validation_errors,
                        columns=check.get("columns") or check.get("column"),
                        label=check["label"],
                        mode=check.get("mode", "subset"),
                        error_msg_template=check.get("error_msg_template"),
                    )
            else:
                # Use standard metadata checks
                _check_metadata_coverage(conn, validation_errors)

            # Check 3: Run any custom value coverage checks
            if custom_value_checks:
                for check in custom_value_checks:
                    check_value_coverage(
                        conn=conn,
                        validation_errors=validation_errors,
                        columns=check.get("columns") or check.get("column"),
                        label=check["label"],
                        mode=check.get("mode", "subset"),
                        error_msg_template=check.get("error_msg_template"),
                    )

            # Check 4: Run all count-based checks (standard and additional)
            _run_count_checks(conn, all_count_checks, validation_errors)

    except duckdb.Error as e:
        # Provide context for database errors to aid in debugging
        query_error_msg = (
            f"DuckDB error during CSV validation: {str(e)}. "
            f"This may indicate an issue with the CSV format, invalid column names, "
            f"or incompatible data types between the generated and reference CSVs."
        )
        validation_errors.append(query_error_msg)

    return validation_errors


def _check_reference_consistency(
    conn: duckdb.DuckDBPyConnection, validation_errors: list[str]
) -> None:
    """Compare channel frame assignments between reference and generated CSVs.

    This verification ensures that the generated data maintains the same
    relationship between channels and frames as the reference data.

    Args:
        conn: Active DuckDB connection with views registered
        validation_errors: List to append any errors to

    """
    # Use our generalized check_value_coverage function with multiple columns
    # and "exact" mode to ensure frame combinations match exactly
    check_value_coverage(
        conn=conn,
        validation_errors=validation_errors,
        columns=["Frame_OrigDNA", "Frame_OrigZO1", "Frame_OrigPhalloidin"],
        label="channel frame assignments",
        mode="exact",
        error_msg_template="Channel frame assignments don't match between reference and generated CSVs. "
        "This may indicate differences in channel ordering or missing frames.",
    )


def check_value_coverage(
    conn: duckdb.DuckDBPyConnection,
    validation_errors: list[str],
    columns: list[str] | str,
    label: str,
    mode: str = "subset",  # "subset", "superset", "exact"
    error_msg_template: str | None = None,
) -> None:
    """Check value coverage between reference and generated tables.

    This function compares distinct values between reference and generated tables
    for one or more columns, with different comparison modes.

    Args:
        conn: Active DuckDB connection with views registered
        validation_errors: List to append any errors to
        columns: Column name or list of column names to check
        label: Human-readable label for the column(s) being checked
        mode: Comparison mode -
              "subset" (reference ⊆ generated, default),
              "superset" (reference ⊇ generated),
              "exact" (reference = generated)
        error_msg_template: Custom error message template with placeholders
                           {label}, {missing_values}, {ref_values}, {gen_values}

    """
    # Handle single column or multiple columns
    if isinstance(columns, str):
        columns = [columns]

    # Build SQL for single column or composite key
    if len(columns) == 1:
        col = columns[0]
        ref_sql = f"SELECT DISTINCT {col} FROM reference"
        gen_sql = f"SELECT DISTINCT {col} FROM generated"
    else:
        # For multiple columns, create composite key using concatenation
        concat_cols = " || ',' || ".join(columns)
        ref_sql = (
            f"SELECT DISTINCT {concat_cols} AS composite_key FROM reference"
        )
        gen_sql = (
            f"SELECT DISTINCT {concat_cols} AS composite_key FROM generated"
        )

    # Get distinct values from both tables
    ref_values = {row[0] for row in conn.execute(ref_sql).fetchall()}
    gen_values = {row[0] for row in conn.execute(gen_sql).fetchall()}

    # Determine values to report based on comparison mode
    if mode == "subset" or mode == "exact":
        # Check if all reference values exist in generated
        missing_values = ref_values - gen_values
        if missing_values:
            # Use custom template if provided, otherwise use default
            if error_msg_template:
                error_msg = error_msg_template.format(
                    label=label,
                    missing_values=missing_values,
                    ref_values=sorted(ref_values),
                    gen_values=sorted(gen_values),
                )
            else:
                error_msg = (
                    f"Reference {label} {missing_values} not found in generated CSV. "
                    f"Reference values: {sorted(ref_values)}, "
                    f"Generated values: {sorted(gen_values)}"
                )
            validation_errors.append(error_msg)

    if mode == "superset" or mode == "exact":
        # Check if generated has extra values not in reference
        extra_values = gen_values - ref_values
        if extra_values:
            # For superset or exact mode, report extra values
            extra_error = (
                f"Generated {label} contains extra values not in reference: {extra_values}. "
                f"Reference values: {sorted(ref_values)}, "
                f"Generated values: {sorted(gen_values)}"
            )
            validation_errors.append(extra_error)


def _check_metadata_coverage(
    conn: duckdb.DuckDBPyConnection, validation_errors: list[str]
) -> None:
    """Check if all reference metadata values are present in the generated data.

    This ensures that the generated file includes data for all the same
    metadata entities (wells, sites, plates) that exist in the reference.

    Args:
        conn: Active DuckDB connection with views registered
        validation_errors: List to append any errors to

    """
    # Define metadata checks for common columns
    metadata_checks = [
        {"column": "Metadata_Well", "label": "wells"},
        {"column": "Metadata_Site", "label": "sites"},
        {"column": "Metadata_Plate", "label": "plates"},
    ]

    # Run each metadata check using the generalized function
    for check in metadata_checks:
        check_value_coverage(
            conn=conn,
            validation_errors=validation_errors,
            columns=check["column"],
            label=check["label"],
            mode="subset",  # We want to ensure reference ⊆ generated
        )


def _run_count_checks(
    conn: duckdb.DuckDBPyConnection,
    checks: list[dict[str, Any]],
    validation_errors: list[str],
) -> None:
    """Run all count-based validation checks.

    Args:
        conn: Active DuckDB connection with views registered
        checks: List of validation checks to perform
        validation_errors: List to append any errors to

    """
    for i, check in enumerate(checks):
        # Verify check has required keys
        if "query" not in check or "error_msg" not in check:
            validation_errors.append(
                f"Invalid check #{i + 1}: must contain 'query' and 'error_msg' keys"
            )
            continue

        # Run the check and add error if count > 0
        count = conn.execute(check["query"]).fetchone()[0]
        if count > 0:
            validation_errors.append(check["error_msg"].format(count=count))


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
