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
FIXME: Need to explain what "Setup" means below (because otherwise "generated" and "pregenerated" don't make sense)

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
- Run only generated tests: pytest test_getting_started_workflow.py -v -k generated
- Run only pregenerated tests: pytest test_getting_started_workflow.py -v -k pregenerated
- Run specific step: pytest test_getting_started_workflow.py -v -k cp_illum_calc
- Run specific step and setup: pytest test_getting_started_workflow.py -v -k "cp_illum_calc and generated"
"""

import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from click.testing import CliRunner

from starrynight.cli.analysis import gen_analysis_load_data_cli
from starrynight.cli.illum import (
    gen_illum_apply_load_data_cli,
    gen_illum_calc_load_data_cli,
)
from starrynight.cli.preprocess import gen_preprocess_load_data_cli
from starrynight.cli.segcheck import gen_segcheck_load_data_cli

from ..fixtures.integration.constants import FIXTURE_CONFIGS  # noqa: TID252
from .constants import FIXTURE_COMPATIBILITY, WORKFLOW_CONFIGS
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
    optional_params = config.get("optional_params", {})

    # Determine which CLI command to use based on command_parts
    command_function = None
    cli_args = []

    # Map command_parts to the appropriate CLI function
    if "illum" in command_parts:
        if "calc" in command_parts:
            command_function = gen_illum_calc_load_data_cli
            if "--sbs" in command_parts:
                cli_args.append("--sbs")
        elif "apply" in command_parts:
            command_function = gen_illum_apply_load_data_cli
            if "--sbs" in command_parts:
                cli_args.append("--sbs")
    elif "segcheck" in command_parts:
        command_function = gen_segcheck_load_data_cli
    elif "preprocess" in command_parts:
        command_function = gen_preprocess_load_data_cli
    elif "analysis" in command_parts:
        command_function = gen_analysis_load_data_cli

    assert command_function is not None, (
        f"Could not determine CLI command for {command_parts}"
    )

    # Build the arguments for the CLI command
    cli_args.extend(
        [
            "-i",
            str(index_file),
            "-o",
            str(workspace[output_dir_key]),
            "--exp_config",
            str(experiment_json_path),
            "--use_legacy",
        ]
    )

    # Add optional parameters if specified
    # NOTE: Currently relying on StarryNight's default path resolution
    # for workflow dependencies (e.g., illum paths, corrected images).
    # When implementing full pipeline testing, we'll need to pass these
    # paths explicitly to ensure correct data flow between steps.
    for param_name, param_value in optional_params.items():
        cli_args.extend([f"--{param_name}", str(param_value)])

    # Use CliRunner to invoke the command
    runner = CliRunner()
    result = runner.invoke(command_function, cli_args)

    # Check if the command was successful
    assert result.exit_code == 0, (
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


@pytest.mark.parametrize("fixture_id", ["fix_s1", "fix_s2", "fix_l1"])
@pytest.mark.parametrize("mode", ["generated", "pregenerated"])
@pytest.mark.parametrize("config", WORKFLOW_CONFIGS, ids=lambda c: c["name"])
def test_complete_workflow(
    fixture_id: str,
    mode: str,
    config: dict[str, Any],
    request: pytest.FixtureRequest,
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
        fixture_id: Identifier for the test fixture (fix_s1, fix_s2)
        mode: Setup mode ("generated" or "pregenerated")
        config: Configuration for the specific workflow step being tested
        request: pytest request object for parameter access

    """
    # Skip test if config has skip=True
    if config.get("skip", False):
        skip_reason = config.get("skip_reason", "Test is disabled")
        pytest.skip(skip_reason)

    # Skip test if not compatible with this fixture_id
    test_name = config["name"]
    compatible_fixtures = FIXTURE_COMPATIBILITY.get(test_name, [])
    if fixture_id not in compatible_fixtures:
        pytest.skip(
            f"Test '{test_name}' is not compatible with fixture '{fixture_id}'"
        )

    # Check if this is a local-only fixture and enforce "generated" mode
    # NOTE: This import uses 'tests.' prefix because tests are run from starrynight/ directory
    # Pre-commit may try to change this to relative imports, but that breaks when pytest runs
    fixture_config = FIXTURE_CONFIGS.get(fixture_id, {})
    if fixture_config.get("local_only", False) and mode == "pregenerated":
        pytest.skip(
            f"Fixture '{fixture_id}' is local-only and does not support pregenerated mode"
        )

    # Dynamically select the appropriate fixtures based on fixture_id and mode
    fixture_name = f"{fixture_id}_starrynight_{mode}"
    workspace_name = f"{fixture_id}_workspace"
    output_dir_name = f"{fixture_id}_output_dir"

    # Get the fixtures from the request
    setup_fixture = request.getfixturevalue(fixture_name)
    workspace = request.getfixturevalue(workspace_name)
    output_dir = request.getfixturevalue(output_dir_name)

    print(f"\nRunning test with fixture: {fixture_id}, mode: {mode}")
    print(f"Testing workflow step: {config['name']}")

    # Step 1: Generate and validate LoadData files
    loaddata_dir, matching_files = generate_and_validate_loaddata(
        config=config,
        setup_fixture=setup_fixture,
        workspace=workspace,
        output_dir=output_dir,
    )

    # FIXME: When implementing the two steps below remember that WORKFLOW_CONFIGS will also
    # need to be updated. Right now it only references LoadData CSV files (e.g. file_pattern
    # and ref_csv_pattern are both related to LoadData CSV files)

    # Step 2: Generate and validate pipeline (not implemented)
    # pipeline_path = generate_pipeline(config, loaddata_dir, workspace)

    # Step 3: Execute and validate CellProfiler (not implemented)
    # output_dir = execute_pipeline(config, pipeline_path, loaddata_dir)
