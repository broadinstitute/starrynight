"""Test for the StarryNight getting-started workflow LoadData generation steps.

This test module focuses specifically on testing the LoadData generation functionality
of the StarryNight workflow by executing the CLI commands and validating the outputs.

The workflow is outlined in ../../../docs/user/getting-started.md

Current coverage:
- CP illum calc LoadData generation
- CP illum apply LoadData generation

Expanded coverage:
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
   - Pipeline type for validation
   - Reference CSV paths for comparison

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

import pandas as pd
import pytest

from .loaddata_validation import validate_loaddata_csv

# LoadData type configurations
LOADDATA_CONFIGS = [
    # CP illum calc LoadData configuration
    {
        "name": "cp_illum_calc",
        "command_parts": ["illum", "calc", "loaddata"],
        "output_dir_key": "cp_illum_calc_dir",
        "file_pattern": "Batch1_Plate1_illum_calc.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline1.csv",
        "pipeline_type": "cp_illum_calc",
    },
    # CP illum apply LoadData configuration
    {
        "name": "cp_illum_apply",
        "command_parts": ["illum", "apply", "loaddata"],
        "output_dir_key": "cp_illum_apply_dir",
        "file_pattern": "Batch1_Plate1_*_illum_apply.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline2.csv",
        "pipeline_type": "cp_illum_apply",
    },
    # CP segmentation check LoadData configuration
    {
        "name": "cp_segmentation_check",
        "command_parts": ["segcheck", "loaddata"],
        "output_dir_key": "cp_segcheck_dir",
        "file_pattern": "Batch1_Plate1_*_segcheck.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline3.csv",
        "pipeline_type": "cp_segmentation_check",
    },
    # SBS illum calc LoadData configuration
    {
        "name": "sbs_illum_calc",
        "command_parts": ["illum", "calc", "loaddata", "--sbs"],
        "output_dir_key": "sbs_illum_calc_dir",
        "file_pattern": "Batch1_Plate1_sbs_illum_calc.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline5.csv",
        "pipeline_type": "sbs_illum_calc",
    },
    # SBS illum apply LoadData configuration
    {
        "name": "sbs_illum_apply",
        "command_parts": ["illum", "apply", "loaddata", "--sbs"],
        "output_dir_key": "sbs_illum_apply_dir",
        "file_pattern": "Batch1_Plate1_*_sbs_illum_apply.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline6.csv",
        "pipeline_type": "sbs_illum_apply",
    },
    # SBS preprocessing LoadData configuration
    {
        "name": "sbs_preprocessing",
        "command_parts": ["preprocess", "loaddata"],
        "output_dir_key": "sbs_preprocess_dir",
        "file_pattern": "Batch1_Plate1_*_preprocess.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline7.csv",
        "pipeline_type": "sbs_preprocessing",
    },
    # Analysis LoadData configuration
    {
        "name": "analysis",
        "command_parts": ["analysis", "loaddata"],
        "output_dir_key": "analysis_dir",
        "file_pattern": "Batch1_Plate1_*_analysis.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline9.csv",
        "pipeline_type": "analysis",
    },
]


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
    pipeline_type = config["pipeline_type"]
    command_parts = config["command_parts"]

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

    # Skip basic column validation - comprehensive validation is done by the validation framework

    # Write to temporary file for validation
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        df.to_csv(temp_path, index=False)

    # Validate the combined data against reference LoadData CSV
    generated_csv_path = temp_path

    # Find the matching reference CSV in the fix_s1_output_dir
    ref_load_data_dir = fix_s1_output_dir["load_data_csv_dir"]
    ref_csv_paths = list(ref_load_data_dir.glob(ref_csv_pattern))
    assert len(ref_csv_paths) > 0, (
        f"Reference CSV not found with pattern: {ref_csv_pattern}"
    )
    ref_csv_path = ref_csv_paths[0]

    # Validate the LoadData CSV against the reference file using the new framework
    errors = validate_loaddata_csv(
        generated_csv_path=generated_csv_path,
        ref_csv_path=ref_csv_path,
        pipeline_type=pipeline_type,
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
