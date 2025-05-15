"""Global pytest fixtures and configuration.

Place shared test fixtures here to make them available to all tests.

Notes on Test Fixtures Organization:
------------------------------------
This file contains fixtures for test data and workspace setup.

As the project grows, follow these organizational best practices:

1. Keep in conftest.py:
   - Simple fixtures that just extract files or create basic directory structures
   - Fixtures that need to be broadly available to many tests
   - Fixture registrations (even if implementation is elsewhere)

2. Move to specialized modules in tests/fixtures/ directory:
   - Complex fixtures over ~100 lines
   - Fixtures that run CLI commands or invoke application logic
   - Fixtures with extensive validation or setup logic
   - Fixtures that depend on multiple other fixtures

3. General organization principles:
   - Group fixtures by feature or functional area
   - Split into domain-specific conftest.py files in subdirectories as needed
   - Maintain clear documentation on fixture dependencies and usage

Assertion Philosophy:
- Keep minimal assertions in fixtures (only what's needed for the fixture to function)
- Verify basic preconditions (file exists, command succeeded) in fixtures
- Move detailed validation (content structure, schema, values) to test functions
- Fixtures verify "Can I do my job?" while tests verify "Did the fixture do its job correctly?"
"""

import json
import shutil
import tarfile
from pathlib import Path

import pooch
import pytest
from click.testing import CliRunner
from pooch import Untar

from starrynight.cli.exp import init as exp_init
from starrynight.cli.exp import new as exp_new
from starrynight.cli.index import gen_index
from starrynight.cli.inv import gen_inv

# Define fixture-specific channel configurations
FIXTURE_CHANNEL_CONFIGS = {
    "fix_s1": {
        "cp_nuclei_channel": "DAPI",
        "cp_cell_channel": "PhalloAF750",
        "cp_mito_channel": "ZO1AF488",
        "sbs_nuclei_channel": "DAPI",
        "sbs_cell_channel": "PhalloAF750",
        "sbs_mito_channel": "ZO1AF488",
    },
    "fix_s2": {
        "cp_nuclei_channel": "DAPI",
        "cp_cell_channel": "PhalloAF750",
        "cp_mito_channel": "ZO1AF488",
        "sbs_nuclei_channel": "DAPI",
        "sbs_cell_channel": "PhalloAF750",
        "sbs_mito_channel": "ZO1AF488",
    },
}

# Configure a single Pooch registry for all test data
STARRYNIGHT_CACHE = pooch.create(
    path=pooch.os_cache("starrynight"),
    base_url="https://github.com/shntnu/starrynight/releases/download/v0.0.1/",
    registry={
        # Input component of FIX-S1 (small test fixture without stitchcrop and QC)
        "fix_s1_input.tar.gz": "sha256:ddba28e1593986013d10880678d2d7715af8d2ee1cfa11ae7bcea4d50c30f9e0",
        # Output component of FIX-S1
        "fix_s1_output.tar.gz": "sha256:a84788c2d5296c02e58c38c382c9b4019c414162a58021a7bfc7c5f20a38be2a",
        # Input component of FIX-S2 (identical inputs to FIX-S1 but with different outputs)
        "fix_s2_input.tar.gz": "sha256:ddba28e1593986013d10880678d2d7715af8d2ee1cfa11ae7bcea4d50c30f9e0",
        # Output component of FIX-S2
        "fix_s2_output.tar.gz": "sha256:dummy_sha256_for_fix_s2_output_to_be_replaced_with_actual_hash",
    },
)


@pytest.fixture(scope="module")
def fix_input_dir(request, tmp_path_factory):
    """Fixture that provides a temporary directory with extracted input data.

    This fixture can be parameterized to use different input data:
    - "fix_s1": Uses the FIX-S1 test fixture (default)
    - "fix_s2": Uses the FIX-S2 test fixture

    Use indirect parameterization to specify the parameters:
    @pytest.mark.parametrize("fix_input_dir", ["fix_s1"], indirect=True)
    @pytest.mark.parametrize("fix_input_dir", ["fix_s2"], indirect=True)

    The default fixture is "fix_s1" if no parameter is specified.

    Returns:
        dict: Dictionary with base_dir, input_dir, and fixture_id

    """
    # Get fixture ID from parameter, default to fix_s1
    fixture_id = getattr(request, "param", "fix_s1")

    # If parameter is a dictionary, extract fixture key
    if isinstance(fixture_id, dict):
        fixture_id = fixture_id.get("fixture", "fix_s1")

    # Validate the fixture ID
    if fixture_id not in FIXTURE_CHANNEL_CONFIGS:
        raise ValueError(
            f"Unknown fixture ID: {fixture_id}. Must be one of: {', '.join(FIXTURE_CHANNEL_CONFIGS.keys())}"
        )

    # Set up parameters based on fixture ID
    if fixture_id == "fix_s1":
        archive_name = "fix_s1_input.tar.gz"
        dir_prefix = "fix_s1_input_test"
        input_dir_name = "fix_s1_input"
        dataset_dir_name = "Source1"
    elif fixture_id == "fix_s2":
        archive_name = "fix_s2_input.tar.gz"
        dir_prefix = "fix_s2_input_test"
        input_dir_name = "fix_s2_input"
        dataset_dir_name = (
            "Source1"  # Using same dataset directory name for now
        )

    # Create a temporary directory
    base_dir = tmp_path_factory.mktemp(dir_prefix)

    # Use pooch to download and extract in one step
    STARRYNIGHT_CACHE.fetch(
        archive_name, processor=Untar(extract_dir=str(base_dir))
    )

    # Create paths to important directories
    input_dir = base_dir / input_dir_name

    # Essential check: did extraction work at all?
    assert input_dir.exists(), "Input test data not extracted correctly"

    # Check that at least one expected dataset directory exists
    dataset_dir = input_dir / dataset_dir_name
    assert dataset_dir.exists(), (
        f"Expected {dataset_dir_name} directory not found in input data"
    )

    # Verify that image files exist in the input directory
    image_files = list(input_dir.glob("**/*.tiff"))
    if not image_files:
        # Try alternative extensions
        image_files = list(input_dir.glob("**/*.tif"))

    assert len(image_files) > 0, (
        f"No image files (*.tiff, *.tif) found in {input_dir_name}"
    )

    # Include fixture_id in the returned dictionary
    return {
        "base_dir": base_dir,
        "input_dir": input_dir,
        "fixture_id": fixture_id,
    }


def _setup_output_dir(
    tmp_path_factory: pytest.TempPathFactory,
    archive_name: str,
    dir_prefix: str,
    output_dir_name: str,
    dataset_dir_name: str,
) -> dict[str, Path]:
    """Set up an output directory from a test archive.

    Args:
        tmp_path_factory: pytest fixture for creating temporary directories
        archive_name: Name of the archive file to extract
        dir_prefix: Prefix for the temporary directory name
        output_dir_name: Name of the extracted output directory
        dataset_dir_name: Name of the dataset directory (e.g., 'Source1')

    Returns:
        dict: Dictionary with paths to key directories

    """
    # Create a temporary directory
    base_dir = tmp_path_factory.mktemp(dir_prefix)

    # Use pooch to download and extract in one step
    STARRYNIGHT_CACHE.fetch(
        archive_name, processor=Untar(extract_dir=str(base_dir))
    )

    # Create paths to important directories
    output_dir = base_dir / output_dir_name
    workspace_dir = output_dir / dataset_dir_name / "workspace"
    load_data_csv_dir = workspace_dir / "load_data_csv"

    # Essential check: did extraction create the main output directory?
    assert output_dir.exists(), "Output test data not extracted correctly"
    assert workspace_dir.exists(), (
        f"Workspace directory not found in {dataset_dir_name} output data"
    )

    # Verify that load_data_csv directory exists
    assert load_data_csv_dir.exists(), (
        f"load_data_csv directory not found in {dataset_dir_name} workspace"
    )

    # Check for LoadData CSV files
    load_data_files = list(load_data_csv_dir.glob("load_data_*.csv"))
    assert len(load_data_files) > 0, (
        f"No LoadData CSV files found in {dataset_dir_name} output data"
    )

    return {
        "base_dir": base_dir,
        "output_dir": output_dir,
        "workspace_dir": workspace_dir,
        "load_data_csv_dir": load_data_csv_dir,
    }


@pytest.fixture(scope="module")
def fix_s1_output_dir(tmp_path_factory):
    """Fixture that provides a temporary directory with extracted FIX-S1 output data."""
    result = _setup_output_dir(
        tmp_path_factory,
        "fix_s1_output.tar.gz",
        "fix_s1_output_test",
        "fix_s1_pcpip_output",
        "Source1",
    )
    yield result
    # Cleanup is handled automatically by pytest's tmp_path_factory


@pytest.fixture(scope="module")
def fix_s2_output_dir(tmp_path_factory):
    """Fixture that provides a temporary directory with extracted FIX-S2 output data."""
    result = _setup_output_dir(
        tmp_path_factory,
        "fix_s2_output.tar.gz",
        "fix_s2_output_test",
        "fix_s2_pcpip_output",
        "Source1",  # Using same dataset directory name for now, can be changed as needed
    )
    yield result
    # Cleanup is handled automatically by pytest's tmp_path_factory


def _setup_workspace(
    tmp_path_factory: pytest.TempPathFactory, workspace_prefix: str
) -> dict[str, Path]:
    """Create a workspace directory structure for tests.

    Args:
        tmp_path_factory: pytest fixture for creating temporary directories
        workspace_prefix: Prefix for the temporary workspace directory

    Returns:
        dict: Dictionary with paths to key directories in the workspace

    """
    # Create base workspace directory
    workspace_dir = tmp_path_factory.mktemp(workspace_prefix)

    # Create subdirectories that match the expected output structure
    dir_structure = [
        # CP illumination directories
        "cellprofiler/loaddata/cp/illum/illum_calc",
        "cellprofiler/loaddata/cp/illum/illum_apply",
        # SBS illumination directories
        "cellprofiler/loaddata/sbs/illum/illum_calc",
        "cellprofiler/loaddata/sbs/illum/illum_apply",
        # CP segmentation check directory
        "cellprofiler/loaddata/cp/segcheck",
        # SBS preprocessing directory
        "cellprofiler/loaddata/sbs/preprocess",
        # Analysis directory
        "cellprofiler/loaddata/analysis",
        # Index and inventory
        "index",
        "inventory/inv",
    ]

    # Create each directory
    for dir_path in dir_structure:
        (workspace_dir / dir_path).mkdir(parents=True, exist_ok=True)

    # Create empty placeholder files for experiment JSONs
    (workspace_dir / "experiment.json").touch()
    (workspace_dir / "experiment_init.json").touch()

    # Return dictionary with paths to all important directories
    return {
        "workspace_dir": workspace_dir,
        # Main workspace directories
        "index_dir": workspace_dir / "index",
        "inventory_dir": workspace_dir / "inventory",
        "inventory_inv_dir": workspace_dir / "inventory" / "inv",
        # CP illumination directories
        "cp_illum_calc_dir": workspace_dir
        / "cellprofiler"
        / "loaddata"
        / "cp"
        / "illum"
        / "illum_calc",
        "cp_illum_apply_dir": workspace_dir
        / "cellprofiler"
        / "loaddata"
        / "cp"
        / "illum"
        / "illum_apply",
        # SBS illumination directories
        "sbs_illum_calc_dir": workspace_dir
        / "cellprofiler"
        / "loaddata"
        / "sbs"
        / "illum"
        / "illum_calc",
        "sbs_illum_apply_dir": workspace_dir
        / "cellprofiler"
        / "loaddata"
        / "sbs"
        / "illum"
        / "illum_apply",
        # CP segmentation check directory
        "cp_segcheck_dir": workspace_dir
        / "cellprofiler"
        / "loaddata"
        / "cp"
        / "segcheck",
        # SBS preprocessing directory
        "sbs_preprocess_dir": workspace_dir
        / "cellprofiler"
        / "loaddata"
        / "sbs"
        / "preprocess",
        # Analysis directory
        "analysis_dir": workspace_dir
        / "cellprofiler"
        / "loaddata"
        / "analysis",
        # JSON files
        "experiment_json": workspace_dir / "experiment.json",
        "experiment_init_json": workspace_dir / "experiment_init.json",
    }


@pytest.fixture(scope="function")
def fix_s1_workspace(tmp_path_factory):
    """Fixture that creates a workspace directory structure for FIX-S1 tests."""
    return _setup_workspace(tmp_path_factory, "fix_s1_workspace")


@pytest.fixture(scope="function")
def fix_s2_workspace(tmp_path_factory):
    """Fixture that creates a workspace directory structure for FIX-S2 tests."""
    return _setup_workspace(tmp_path_factory, "fix_s2_workspace")


def _handle_generated_setup(
    workspace: dict[str, Path], input_dir: Path, channel_config: dict[str, str]
) -> dict[str, Path]:
    """Set up a StarryNight workflow environment using CLI commands.

    Args:
        workspace: Dictionary containing workspace directories
        input_dir: Path to input data directory
        channel_config: Dictionary with required channel configuration

    Returns:
        dict: Dictionary with index_file and experiment_json_path

    """
    workspace_dir = workspace["workspace_dir"]
    inventory_dir = workspace["inventory_dir"]
    index_dir = workspace["index_dir"]

    # Step 1: Initialize experiment configuration
    runner = CliRunner()
    result = runner.invoke(
        exp_init,
        ["-e", "Pooled CellPainting [Generic]", "-o", str(workspace_dir)],
    )

    # Check if the command was successful
    assert result.exit_code == 0, (
        f"Experiment init command failed: {result.stderr}"
    )

    # Verify experiment_init.json was created (essential for next steps)
    exp_init_path = workspace_dir / "experiment_init.json"
    assert exp_init_path.exists(), "experiment_init.json was not created"

    # Step 2: Edit experiment_init.json as specified in the docs
    with exp_init_path.open() as f:
        exp_init_data = json.load(f)

    # Update with required channel values from config parameter
    exp_init_data.update(channel_config)

    with exp_init_path.open("w") as f:
        json.dump(exp_init_data, f, indent=4)

    # Basic check that file still exists after modification
    assert exp_init_path.exists(), "Modified experiment_init.json not found"

    # Step 3: Generate inventory
    result = runner.invoke(
        gen_inv, ["-d", str(input_dir), "-o", str(inventory_dir)]
    )

    # Check if the command was successful
    assert result.exit_code == 0, (
        f"Inventory generation command failed: {result.stderr}"
    )

    # Essential check: inventory file must exist for next steps
    inventory_file = inventory_dir / "inventory.parquet"
    assert inventory_file.exists(), "Inventory file was not created"

    # Step 4: Generate index
    # Create the index directory if it doesn't exist
    index_dir.mkdir(exist_ok=True, parents=True)

    result = runner.invoke(
        gen_index, ["-i", str(inventory_file), "-o", str(index_dir)]
    )

    # Check if the command was successful
    assert result.exit_code == 0, (
        f"Index generation command failed: {result.stderr}"
    )

    # Essential check: index file must exist for next steps
    index_file = index_dir / "index.parquet"
    assert index_file.exists(), "Index file was not created"

    # Step 5: Create experiment file
    result = runner.invoke(
        exp_new,
        [
            "-i",
            str(index_file),
            "-e",
            "Pooled CellPainting [Generic]",
            "-c",
            str(exp_init_path),
            "-o",
            str(workspace_dir),
        ],
    )

    # Check if the command was successful
    assert result.exit_code == 0, (
        f"Experiment file creation command failed: {result.stderr}"
    )

    # Essential check: experiment.json file must exist to return it
    experiment_json_path = workspace_dir / "experiment.json"
    assert experiment_json_path.exists(), "experiment.json was not created"

    # Return the paths needed for subsequent processing steps
    return {
        "index_file": index_file,
        "experiment_json_path": experiment_json_path,
    }


def _handle_pregenerated_setup(
    workspace: dict[str, Path], fixture_id: str
) -> dict[str, Path]:
    """Set up a StarryNight workflow environment using pre-generated files.

    Args:
        workspace: Dictionary containing workspace directories
        fixture_id: Fixture identifier (e.g., 'fix_s1', 'fix_s2')

    Returns:
        dict: Dictionary with index_file and experiment_json_path

    """
    workspace_dir = workspace["workspace_dir"]

    # Use fixture-specific subdirectory for pregenerated files
    # Each fixture must have its own subdirectory under basic_setup
    fixtures_base_dir = Path(__file__).parent / "fixtures" / "basic_setup"
    fixtures_dir = fixtures_base_dir / fixture_id

    # If fixture directory doesn't exist, fall back to basic_setup for backward compatibility
    if not fixtures_dir.exists():
        raise FileNotFoundError(
            f"Fixture directory not found for {fixture_id} at {fixtures_dir}"
        )

    # Define paths to pre-generated files in fixtures directory
    pregenerated_index_file = fixtures_dir / "index.parquet"
    pregenerated_experiment_json = fixtures_dir / "experiment.json"

    # Essential checks: source files must exist to be copied
    assert pregenerated_index_file.exists(), (
        f"Pre-generated index file not found for {fixture_id} at {pregenerated_index_file}"
    )
    assert pregenerated_experiment_json.exists(), (
        f"Pre-generated experiment file not found for {fixture_id} at {pregenerated_experiment_json}"
    )

    # Copy files to workspace directory to maintain expected structure
    index_file = workspace["index_dir"] / "index.parquet"
    experiment_json_path = workspace_dir / "experiment.json"

    # Create parent directories if they don't exist
    index_file.parent.mkdir(parents=True, exist_ok=True)

    # Copy the files
    shutil.copy2(pregenerated_index_file, index_file)
    shutil.copy2(pregenerated_experiment_json, experiment_json_path)

    # Essential checks: copied files must exist for fixture to function
    assert index_file.exists(), "Failed to copy index file to workspace"
    assert experiment_json_path.exists(), (
        "Failed to copy experiment file to workspace"
    )

    # Return the same structure as the generated mode
    return {
        "index_file": index_file,
        "experiment_json_path": experiment_json_path,
    }


@pytest.fixture(scope="function")
def fix_starrynight_setup(request, fix_input_dir):
    """Fixture that sets up the StarryNight workflow environment.

    This fixture can operate in multiple modes, specified through indirect parameterization:
    - Mode parameter: "generated" or "pregenerated"
      - "generated": Executes actual CLI commands to generate all files (slow but thorough)
      - "pregenerated": Uses pre-generated files from fixtures (fast)

    The fixture ID is taken directly from the fix_input_dir fixture.

    Use indirect parameterization to specify both parameters:
    @pytest.mark.parametrize(
        "fix_input_dir,fix_starrynight_setup",
        [
            ("fix_s1", {"mode": "generated"}),
            ("fix_s1", {"mode": "pregenerated"}),
            ("fix_s2", {"mode": "generated"}),
            ("fix_s2", {"mode": "pregenerated"}),
        ],
        indirect=True,
    )

    Returns:
        dict: Dictionary containing:
            - index_file: Path to the generated/pre-generated index.parquet file
            - experiment_json_path: Path to the generated/pre-generated experiment.json file

    """
    # Extract the fixture ID from fix_input_dir
    fixture_id = fix_input_dir["fixture_id"]

    # Extract mode parameter with a default of "generated"
    param = getattr(request, "param", {"mode": "generated"})
    if isinstance(param, str):
        mode = param
    else:
        mode = param.get("mode", "generated")

    # Get the channel configuration for this fixture
    channel_config = FIXTURE_CHANNEL_CONFIGS[fixture_id]

    # Get workspace fixture dynamically
    workspace_fixture = request.getfixturevalue(f"{fixture_id}_workspace")

    # Execute the appropriate setup based on mode parameter
    if mode == "generated":
        return _handle_generated_setup(
            workspace_fixture, fix_input_dir["input_dir"], channel_config
        )
    elif mode == "pregenerated":
        return _handle_pregenerated_setup(workspace_fixture, fixture_id)
    else:
        raise ValueError(f"Unknown mode: {mode}")
