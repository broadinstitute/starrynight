"""Tests for the StarryNight example workflow described in the getting-started guide.

This test module verifies the StarryNight workflow functionality by executing CLI
commands and validating the outputs. There are two test approaches:

1. LoadData Generation Only (current implementation):
   - Tests only the generation of LoadData CSV files for each step

2. Complete Workflow (planned future implementation):
   - Will test all three steps: LoadData generation, pipeline generation, and execution
   - Follows the workflow outlined in ../../../docs/user/example-pipeline-cli.md

Testing strategy:
This module uses a parameterized approach to test multiple workflow steps:

1. Tests are parameterized with both:
   - Setup mode: "generated" (full workflow) vs. "pregenerated" (pre-generated files)
   - Workflow step: which stage to test (illum_calc, illum_apply, etc.)

2. Each workflow step has its own configuration including:
   - Command parameters
   - Expected file patterns
   - Pipeline type for validation
   - Reference paths for comparison

Running the tests:
- Run all tests: pytest test_getting_started_workflow.py
- Run only fast tests: pytest test_getting_started_workflow.py -v -k fast
- Run only full workflow tests: pytest test_getting_started_workflow.py -v -k full
- Run specific step: pytest test_getting_started_workflow.py -v -k cp_illum_calc
- Run specific step and setup: pytest test_getting_started_workflow.py -v -k "cp_illum_calc and full"
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from .loaddata_validation import compare_csvs


def generate_and_validate_loaddata(  # noqa: C901
    config: dict[str, Any],
    setup_fixture: dict[str, Any],
    workspace: dict[str, Path],
    output_dir: dict[str, Path],
) -> tuple[Path, list[Path]]:
    """Generate and validate LoadData CSV files for a workflow step.

    This function performs both the generation of LoadData files via the
    StarryNight CLI and their validation against reference files.

    Args:
        config: Configuration for the workflow step
        setup_fixture: The test fixture with paths and configuration
        workspace: Dictionary with workspace directories
        output_dir: Dictionary with reference output directories

    Returns:
        tuple: (loaddata_dir, matching_files)
            - loaddata_dir: Directory where LoadData files were created
            - matching_files: List of paths to generated LoadData files

    Raises:
        AssertionError: If LoadData generation or validation fails

    """
    # PART 1: GENERATE LOADDATA FILES
    # Get paths from the fixture
    index_file = setup_fixture["index_file"]
    experiment_json_path = setup_fixture["experiment_json_path"]

    # Get LoadData type-specific configuration
    loaddata_name = config["name"]
    output_dir_key = config["output_dir_key"]
    file_pattern = config["file_pattern"]
    ref_csv_pattern = config["ref_csv_pattern"]
    command_parts = config["command_parts"]

    # Build the command for generating LoadData files
    loaddata_cmd = [
        "starrynight",
        *command_parts,  # e.g., ["illum", "calc", "loaddata"]
        "-i",
        str(index_file),
        "-o",
        str(workspace[output_dir_key]),
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
    loaddata_dir = workspace[output_dir_key]

    # Check for the presence of at least one LoadData CSV file in the directory
    csv_files = list(loaddata_dir.glob("*.csv"))
    assert len(csv_files) > 0, "No LoadData CSV files were created"

    # Check for matching files using pattern
    matching_files = list(loaddata_dir.glob(file_pattern))
    assert len(matching_files) > 0, (
        f"No files matching pattern {file_pattern} were created. "
        f"Found files: {[f.name for f in csv_files]}"
    )

    # PART 2: VALIDATE LOADDATA FILES
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

    # Write to temporary file for validation
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        df.to_csv(temp_path, index=False)

    # Validate the combined data against reference LoadData CSV
    gen_csv_path = temp_path

    # Find the matching reference CSV in the output_dir
    ref_load_data_dir = output_dir["load_data_csv_dir"]
    ref_csv_paths = list(ref_load_data_dir.glob(ref_csv_pattern))
    assert len(ref_csv_paths) > 0, (
        f"Reference CSV not found with pattern: {ref_csv_pattern}"
    )
    ref_csv_path = ref_csv_paths[0]

    # Validate the LoadData CSV against the reference file using the validation framework
    report = compare_csvs(
        reference_csv_path=ref_csv_path,
        generated_csv_path=gen_csv_path,
        skip_column_substrings=["PathName"],
    )

    try:
        temp_path.unlink()
    except Exception as e:
        print(f"Warning: Failed to delete temporary file {temp_path}: {e}")

    # Report any validation errors
    if report.warnings:
        warning_message = f"CSV validation has {len(report.warnings)} warning(s):\n{report.format_warnings()}"
        print(warning_message)  # Print to console immediately (but don't fail)
    if report.errors:
        error_message = f"CSV validation failed with {len(report.errors)} error(s):\n{report.format_errors()}"
        print(error_message)  # Print to console immediately
        pytest.fail(error_message)  # Fail the test with same message

    # Clean up the temporary file
    return loaddata_dir, matching_files


# Workflow step configurations
WORKFLOW_CONFIGS = [
    # CP illum calc LoadData configuration
    {
        "name": "cp_illum_calc",
        "command_parts": ["illum", "calc", "loaddata"],
        "output_dir_key": "cp_illum_calc_dir",
        "file_pattern": "Batch1_Plate1_illum_calc.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline1.csv",
        "skip": False,
        "skip_reason": None,
    },
    # CP illum apply LoadData configuration
    {
        "name": "cp_illum_apply",
        "command_parts": ["illum", "apply", "loaddata"],
        "output_dir_key": "cp_illum_apply_dir",
        "file_pattern": "Batch1_Plate1_*_illum_apply.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline2.csv",
        "skip": False,
        "skip_reason": None,
    },
    # CP segmentation check LoadData configuration
    {
        "name": "cp_segmentation_check",
        "command_parts": ["segcheck", "loaddata"],
        "output_dir_key": "cp_segcheck_dir",
        "file_pattern": "Batch1_Plate1_*_segcheck.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline3.csv",
        "skip": True,
        "skip_reason": "Not implemented",
    },
    # SBS illum calc LoadData configuration
    {
        "name": "sbs_illum_calc",
        "command_parts": ["illum", "calc", "loaddata", "--sbs"],
        "output_dir_key": "sbs_illum_calc_dir",
        "file_pattern": "Batch1_Plate1_*_illum_calc.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline5.csv",
        "skip": False,  # Now testing with simplified validator
        "skip_reason": None,
    },
    # SBS illum apply LoadData configuration
    {
        "name": "sbs_illum_apply",
        "command_parts": ["illum", "apply", "loaddata", "--sbs"],
        "output_dir_key": "sbs_illum_apply_dir",
        "file_pattern": "Batch1_Plate1_*_illum_apply.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline6.csv",
        "skip": False,
        "skip_reason": None,
    },
    # SBS preprocessing LoadData configuration
    {
        "name": "sbs_preprocessing",
        "command_parts": ["preprocess", "loaddata"],
        "output_dir_key": "sbs_preprocess_dir",
        "file_pattern": "Batch1_Plate1_*_preprocess.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline7.csv",
        "skip": True,
        "skip_reason": "Not implemented",
    },
    # Analysis LoadData configuration
    {
        "name": "analysis",
        "command_parts": ["analysis", "loaddata"],
        "output_dir_key": "analysis_dir",
        "file_pattern": "Batch1_Plate1_*_analysis.csv",
        "ref_csv_pattern": "**/Plate1_trimmed/load_data_pipeline9.csv",
        "skip": True,
        "skip_reason": "Not implemented",
    },
]


@pytest.mark.parametrize(
    "fix_starrynight_setup",
    ["generated", "pregenerated"],
    ids=["full", "fast"],
    indirect=True,
)
@pytest.mark.parametrize("config", WORKFLOW_CONFIGS, ids=lambda c: c["name"])
def test_complete_workflow(
    fix_starrynight_setup: dict[str, Path],
    config: dict[str, Any],
    request: pytest.FixtureRequest,
    fix_s1_workspace: dict[str, Path],
    fix_s1_output_dir: dict[str, Path],
) -> None:
    """Test the complete three-step workflow for different steps.

    This test validates all three steps of the workflow:
    1. LoadData generation
    2. Pipeline generation: NOT YET IMPLEMENTED
    3. CellProfiler execution: NOT YET IMPLEMENTED

    This test is currently only validating the LoadData generation step.
    The test uses both modes of the fixture setup:
    - "generated": Runs the actual CLI commands to generate setup files (slow but validates CLI)
    - "pregenerated": Uses pre-generated setup files (faster for testing downstream functionality)

    Tests are automatically skipped if the config dictionary has "skip": True,
    with the skip reason taken from the "skip_reason" field.

    Args:
        fix_starrynight_setup: Fixture providing index and experiment configuration
        config: Configuration for the specific workflow step being tested
        request: pytest request object for parameter access
        fix_s1_workspace: Fixture providing workspace directory structure
        fix_s1_output_dir: Fixture providing reference output data for validation

    """
    # Skip test if config has skip=True
    if config.get("skip", False):
        skip_reason = config.get("skip_reason", "Test is disabled")
        pytest.skip(skip_reason)

    # Use the parameterized fixture directly
    setup_fixture = fix_starrynight_setup

    # Get current fixture mode for debugging
    current_mode = request.node.callspec.params.get("fix_starrynight_setup")
    print(f"\nRunning test with setup mode: {current_mode}")
    print(f"Testing workflow step: {config['name']}")

    # Step 1: Generate and validate LoadData files
    loaddata_dir, matching_files = generate_and_validate_loaddata(
        config=config,
        setup_fixture=setup_fixture,
        workspace=fix_s1_workspace,
        output_dir=fix_s1_output_dir,
    )

    # Step 2: Generate and validate pipeline (not implemented)
    # pipeline_path = generate_pipeline(config, loaddata_dir, fix_s1_workspace)

    # Step 3: Execute and validate CellProfiler (not implemented)
    # output_dir = execute_pipeline(config, pipeline_path, loaddata_dir)
