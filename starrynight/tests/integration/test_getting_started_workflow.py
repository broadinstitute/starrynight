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


def get_available_columns(
    conn: duckdb.DuckDBPyConnection,
) -> tuple[set[str], set[str]]:
    """Get available columns from both reference and generated tables.

    Args:
        conn: Database connection with views

    Returns:
        Tuple of (reference columns, generated columns)

    """
    ref_columns = {
        row[0]
        for row in conn.execute("PRAGMA table_info(reference)").fetchall()
    }
    gen_columns = {
        row[0]
        for row in conn.execute("PRAGMA table_info(generated)").fetchall()
    }
    return ref_columns, gen_columns


def get_standard_checks(columns: set[str]) -> list[dict[str, Any]]:
    """Build standard validation checks based on available columns.

    Args:
        columns: Set of column names available in the table

    Returns:
        List of SQL check dictionaries

    """
    standard_checks = []

    # Filename pattern check (only if all filename columns exist)
    filename_cols = [
        "FileName_OrigDNA",
        "FileName_OrigZO1",
        "FileName_OrigPhalloidin",
    ]
    if all(col in columns for col in filename_cols):
        standard_checks.append(
            {
                "query": """
                SELECT COUNT(*) FROM generated
                WHERE FileName_OrigDNA NOT LIKE '%Channel%'
                OR FileName_OrigZO1 NOT LIKE '%Channel%'
                OR FileName_OrigPhalloidin NOT LIKE '%Channel%'
            """,
                "error_msg": "Found {count} filenames that don't match the expected pattern",
            }
        )

    # Metadata nullness check (only if all metadata columns exist)
    metadata_cols = [
        "Metadata_Batch",
        "Metadata_Plate",
        "Metadata_Well",
        "Metadata_Site",
    ]
    if all(col in columns for col in metadata_cols):
        standard_checks.append(
            {
                "query": """
                SELECT COUNT(*) FROM generated
                WHERE Metadata_Batch IS NULL
                OR Metadata_Plate IS NULL
                OR Metadata_Well IS NULL
                OR Metadata_Site IS NULL
            """,
                "error_msg": "Found {count} rows with missing metadata fields",
            }
        )

    # Path and filename nullness check (only if all path/filename columns exist)
    path_cols = [
        "FileName_OrigDNA",
        "FileName_OrigZO1",
        "FileName_OrigPhalloidin",
        "PathName_OrigDNA",
        "PathName_OrigZO1",
        "PathName_OrigPhalloidin",
    ]
    if all(col in columns for col in path_cols):
        standard_checks.append(
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
            }
        )

    return standard_checks


def validate_loaddata_csv(
    generated_csv_path: Path,
    ref_csv_path: Path,
    additional_checks: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Validate generated LoadData CSV against reference file.

    Compares CSVs for:
    1. Matching distinct values in key columns
    2. Non-null required fields
    3. Pattern-matching for formatted fields

    Args:
        generated_csv_path: Path to generated CSV
        ref_csv_path: Path to reference CSV
        additional_checks: SQL checks with "query" and "error_msg" keys

    Returns:
        Error messages (empty list if validation passed)

    Example:
        additional_checks=[{
            "query": "SELECT COUNT(*) FROM generated WHERE ImageNumber IS NULL",
            "error_msg": "Found {count} rows missing ImageNumber"
        }]

    """
    errors = []

    try:
        # Create in-memory database with both CSVs as views
        with duckdb.connect(":memory:") as conn:
            conn.execute(
                f"CREATE VIEW generated AS SELECT * FROM read_csv_auto('{str(generated_csv_path)}')"
            )
            conn.execute(
                f"CREATE VIEW reference AS SELECT * FROM read_csv_auto('{str(ref_csv_path)}')"
            )

            # Get available columns from both tables
            ref_columns, gen_columns = get_available_columns(conn)

            # 1. Check frame columns if they exist
            validate_frame_columns(conn, errors, ref_columns, gen_columns)

            # 2. Check metadata columns if they exist
            validate_metadata_columns(conn, errors, ref_columns, gen_columns)

            # 3. Run standard and additional SQL checks
            validate_with_sql_checks(
                conn, errors, gen_columns, additional_checks
            )

    except duckdb.Error as e:
        errors.append(f"Database error: {str(e)} (check CSV format/types)")

    return errors


def validate_frame_columns(
    conn: duckdb.DuckDBPyConnection,
    errors: list[str],
    ref_columns: set[str],
    gen_columns: set[str],
) -> None:
    """Validate frame column values if they exist.

    Args:
        conn: Database connection
        errors: List to append errors to
        ref_columns: Available reference columns
        gen_columns: Available generated columns

    """
    frame_columns = ["Frame_OrigDNA", "Frame_OrigZO1", "Frame_OrigPhalloidin"]

    # Only validate if all columns exist in both tables
    if all(col in ref_columns and col in gen_columns for col in frame_columns):
        check_column_values(
            conn,
            errors,
            frame_columns,
            "channel frame assignments",
            mode="exact",
        )


def validate_metadata_columns(
    conn: duckdb.DuckDBPyConnection,
    errors: list[str],
    ref_columns: set[str],
    gen_columns: set[str],
) -> None:
    """Validate metadata column values if they exist.

    Args:
        conn: Database connection
        errors: List to append errors to
        ref_columns: Available reference columns
        gen_columns: Available generated columns

    """
    metadata_checks = [
        ("Metadata_Well", "wells"),
        ("Metadata_Site", "sites"),
        ("Metadata_Plate", "plates"),
    ]

    for col, label in metadata_checks:
        if col in ref_columns and col in gen_columns:
            check_column_values(conn, errors, col, label)


def validate_with_sql_checks(
    conn: duckdb.DuckDBPyConnection,
    errors: list[str],
    gen_columns: set[str],
    additional_checks: list[dict[str, Any]] | None = None,
) -> None:
    """Run SQL-based checks on the generated data.

    Args:
        conn: Database connection
        errors: List to append errors to
        gen_columns: Available columns in generated table
        additional_checks: Additional SQL checks to run

    """
    # Get standard checks based on available columns
    standard_checks = get_standard_checks(gen_columns)

    # Add any additional checks
    if additional_checks:
        standard_checks.extend(additional_checks)

    # Run all the count-based checks
    for check in standard_checks:
        # Try to execute the query, catching column-related errors
        try:
            count = conn.execute(check["query"]).fetchone()[0]
            if count > 0:
                errors.append(check["error_msg"].format(count=count))
        except duckdb.Error as e:
            if "not found" in str(e):
                # Skip this check if columns aren't found
                continue
            else:
                # Raise other SQL errors
                raise


def check_column_values(
    conn: duckdb.DuckDBPyConnection,
    errors: list[str],
    columns: list[str] | str,
    label: str,
    mode: str = "subset",  # "subset", "exact", "superset"
) -> None:
    """Compare column values between reference and generated tables.

    Args:
        conn: Database connection with views
        errors: List to append errors to
        columns: Column(s) to check
        label: Name for error messages
        mode: "subset" (default), "exact", or "superset"

    """
    # Handle single column or multiple columns
    if isinstance(columns, str):
        columns = [columns]

    # Get distinct values from both tables
    if len(columns) == 1:
        col = columns[0]
        ref_values = {
            row[0]
            for row in conn.execute(
                f"SELECT DISTINCT {col} FROM reference"
            ).fetchall()
        }
        gen_values = {
            row[0]
            for row in conn.execute(
                f"SELECT DISTINCT {col} FROM generated"
            ).fetchall()
        }
    else:
        # For multiple columns, concatenate as a composite key
        concat_cols = " || ',' || ".join(columns)
        ref_values = {
            row[0]
            for row in conn.execute(
                f"SELECT DISTINCT {concat_cols} FROM reference"
            ).fetchall()
        }
        gen_values = {
            row[0]
            for row in conn.execute(
                f"SELECT DISTINCT {concat_cols} FROM generated"
            ).fetchall()
        }

    # Check if reference values exist in generated (subset mode)
    if mode in ["subset", "exact"]:
        missing = ref_values - gen_values
        if missing:
            errors.append(f"Missing {label} in generated CSV: {missing}")

    # Check if generated has extra values (superset mode)
    if mode in ["superset", "exact"]:
        extra = gen_values - ref_values
        if extra:
            errors.append(f"Extra {label} in generated CSV: {extra}")


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

    # Validate the LoadData CSV against the reference file
    errors = validate_loaddata_csv(
        generated_csv_path=generated_csv_path,
        ref_csv_path=ref_csv_path,
        additional_checks=additional_checks,
    )

    # Report any validation errors
    if errors:
        error_message = "\n".join(
            f"Error {i + 1}: {error}" for i, error in enumerate(errors)
        )
        pytest.fail(
            f"CSV validation failed with {len(errors)} error(s):\n{error_message}"
        )

    # Clean up the temporary file
    try:
        temp_path.unlink()
    except Exception as e:
        print(f"Warning: Failed to delete temporary file {temp_path}: {e}")
