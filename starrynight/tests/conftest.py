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

The assertions in fixtures are appropriate for verifying setup preconditions
and ensuring the test environment is correctly configured before tests run.
"""

import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

import pooch
import pytest
from pooch import Untar

# Configure a single Pooch registry for all test data
STARRYNIGHT_CACHE = pooch.create(
    path=pooch.os_cache("starrynight"),
    base_url="https://github.com/shntnu/starrynight/releases/download/v0.0.1/",
    registry={
        # Input component of FIX-S1 (small test fixture without stitchcrop and QC)
        "fix_s1_input.tar.gz": "md5:01de912bdff0379b671c39b400dda915",
        # Output component of FIX-S1
        "fix_s1_output.tar.gz": "md5:1bcc54c61cbe2c4b96c6b09ffc8d4f0f",
    },
)


@pytest.fixture(scope="session")
def fix_s1_input_archive():
    """Fixture that downloads and caches the FIX-S1 input test data archive.

    This fixture handles the input component of the standard FIX-S1 test fixture
    (small test fixture without stitchcrop and QC).

    Returns:
        str: Path to the downloaded archive file.

    """
    # Download and cache the test data using the global registry
    archive_path = STARRYNIGHT_CACHE.fetch(
        "fix_s1_input.tar.gz", processor=None
    )

    # Verify the archive
    archive_path_obj = Path(archive_path)
    assert archive_path_obj.exists(), (
        "Test data archive not downloaded correctly"
    )
    assert tarfile.is_tarfile(archive_path_obj), (
        "Downloaded file is not a valid tar archive"
    )

    return archive_path


@pytest.fixture(scope="session")
def fix_s1_output_archive():
    """Fixture that downloads and caches the FIX-S1 output test data archive.

    This fixture handles the output component of the standard FIX-S1 test fixture
    (small test fixture without stitchcrop and QC).

    Returns:
        str: Path to the downloaded archive file.

    """
    # Download and cache the test data using the global registry
    archive_path = STARRYNIGHT_CACHE.fetch(
        "fix_s1_output.tar.gz", processor=None
    )

    # Verify the archive
    archive_path_obj = Path(archive_path)
    assert archive_path_obj.exists(), (
        "Output test data archive not downloaded correctly"
    )
    assert tarfile.is_tarfile(archive_path_obj), (
        "Output file is not a valid tar archive"
    )

    return archive_path


@pytest.fixture(scope="module")
def fix_s1_input_dir(tmp_path_factory):
    """Fixture that provides a temporary directory with extracted FIX-S1 input data.

    This fixture handles the input component of the standard FIX-S1 test fixture
    (small test fixture without stitchcrop and QC).

    This fixture:
    1. Creates a temporary directory
    2. Uses pooch processor to extract the FIX-S1 input data archive into it
    3. Yields a dictionary with paths to key directories
    4. Cleans up the temporary directory after the test is done

    Args:
        tmp_path_factory: pytest fixture for creating temporary directories

    Returns:
        dict: Dictionary containing paths to key directories:
            - base_dir: The base temporary directory
            - input_dir: Path to the extracted fix_s1_input directory

    """
    # Create a temporary directory
    base_dir = tmp_path_factory.mktemp("fix_s1_input_test")

    # Use pooch to download and extract in one step
    STARRYNIGHT_CACHE.fetch(
        "fix_s1_input.tar.gz", processor=Untar(extract_dir=str(base_dir))
    )

    # Create paths to important directories
    input_dir = base_dir / "fix_s1_input"

    # Verify the extraction worked correctly
    assert input_dir.exists(), "Input test data not extracted correctly"

    yield {"base_dir": base_dir, "input_dir": input_dir}

    # Cleanup is handled automatically by pytest's tmp_path_factory


@pytest.fixture(scope="module")
def fix_s1_output_dir(tmp_path_factory):
    """Fixture that provides a temporary directory with extracted FIX-S1 output data.

    This fixture handles the output component of the standard FIX-S1 test fixture
    (small test fixture without stitchcrop and QC).

    This fixture:
    1. Creates a temporary directory
    2. Uses pooch processor to extract the FIX-S1 output data archive into it
    3. Yields a dictionary with paths to key directories
    4. Cleans up the temporary directory after the test is done

    Args:
        tmp_path_factory: pytest fixture for creating temporary directories

    Returns:
        dict: Dictionary containing paths to key directories:
            - base_dir: The base temporary directory
            - output_dir: Path to the extracted fix_s1_output directory
            - workspace_dir: Path to Source1/workspace directory with outputs

    """
    # Create a temporary directory
    base_dir = tmp_path_factory.mktemp("fix_s1_output_test")

    # Use pooch to download and extract in one step
    STARRYNIGHT_CACHE.fetch(
        "fix_s1_output.tar.gz", processor=Untar(extract_dir=str(base_dir))
    )

    # Create paths to important directories
    output_dir = base_dir / "fix_s1_output"
    workspace_dir = output_dir / "Source1" / "workspace"
    load_data_csv_dir = workspace_dir / "load_data_csv"

    # Verify the extraction worked correctly
    assert output_dir.exists(), "Output test data not extracted correctly"
    assert workspace_dir.exists(), "Output workspace directory not found"
    assert load_data_csv_dir.exists(), (
        "LoadData CSV directory not found in output"
    )

    yield {
        "base_dir": base_dir,
        "output_dir": output_dir,
        "workspace_dir": workspace_dir,
        "load_data_csv_dir": load_data_csv_dir,
    }

    # Cleanup is handled automatically by pytest's tmp_path_factory


@pytest.fixture(scope="function")
def fix_s1_workspace(tmp_path_factory):
    """Fixture that creates a workspace directory structure for FIX-S1 tests.

    This fixture creates a temporary directory with the structure needed for
    processing the FIX-S1 test fixture (small test fixture without stitchcrop and QC).
    The structure matches the expected output directory structure:

    - workspace/
      - cellprofiler/
        - loaddata/
          - cp/
            - illum/
              - illum_apply/
              - illum_calc/
          - sbs/
            - illum/
              - illum_apply/
              - illum_calc/
      - index/
      - inventory/
        - inv/

    Returns:
        dict: Dictionary with paths to key directories in the workspace

    """
    # Create base workspace directory
    workspace_dir = tmp_path_factory.mktemp("workspace")

    # Create subdirectories that match the expected output structure
    dir_structure = [
        # CP illumination directories
        "cellprofiler/loaddata/cp/illum/illum_calc",
        "cellprofiler/loaddata/cp/illum/illum_apply",
        # SBS illumination directories
        "cellprofiler/loaddata/sbs/illum/illum_calc",
        "cellprofiler/loaddata/sbs/illum/illum_apply",
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
        # JSON files
        "experiment_json": workspace_dir / "experiment.json",
        "experiment_init_json": workspace_dir / "experiment_init.json",
    }


@pytest.fixture(scope="function")
def fix_starrynight_basic_setup(fix_s1_input_dir, fix_s1_workspace):
    """Fixture that sets up the basic StarryNight workflow environment.

    Performs steps 1-5 of the getting-started workflow:
    1. Initialize experiment configuration
    2. Edit configuration with required channel values
    3. Generate inventory from input data
    4. Generate index from inventory
    5. Create experiment file from index and configuration

    This fixture generates all files from scratch by running the actual CLI commands.
    For faster testing that skips these steps, use fix_starrynight_pregenerated_setup.

    Returns:
        dict: Dictionary containing:
            - index_file: Path to the generated index.parquet file
            - experiment_json_path: Path to the generated experiment.json file

    """
    # Set up test environment
    workspace_dir = fix_s1_workspace["workspace_dir"]
    inventory_dir = fix_s1_workspace["inventory_dir"]
    index_dir = fix_s1_workspace["index_dir"]
    input_dir = fix_s1_input_dir["input_dir"]

    # Step 1: Initialize experiment configuration
    exp_init_cmd = [
        "starrynight",
        "exp",
        "init",
        "-e",
        "Pooled CellPainting [Generic]",
        "-o",
        str(workspace_dir),
    ]

    # Run the command and check it was successful
    result = subprocess.run(
        exp_init_cmd, capture_output=True, text=True, check=False
    )

    # Check if the command was successful
    assert result.returncode == 0, (
        f"Experiment init command failed: {result.stderr}"
    )

    # Define expected config properties
    expected_config_keys = [
        "barcode_csv_path",
        "use_legacy",
        "cp_img_overlap_pct",
        "cp_img_frame_type",
        "cp_acquisition_order",
        "sbs_img_overlap_pct",
        "sbs_img_frame_type",
        "sbs_acquisition_order",
    ]

    # Verify experiment_init.json was created
    exp_init_path = workspace_dir / "experiment_init.json"
    assert exp_init_path.exists(), "experiment_init.json was not created"

    # Read the file and verify its contents
    with exp_init_path.open() as f:
        actual_config = json.load(f)

    # Verify the configuration has the expected keys
    for key in expected_config_keys:
        assert key in actual_config, (
            f"Key '{key}' missing in experiment_init.json"
        )

    # Step 2: Edit experiment_init.json as specified in the docs
    with exp_init_path.open() as f:
        exp_init_data = json.load(f)

    # Update with required channel values specifically mentioned in getting-started.md
    exp_init_data.update(
        {
            "cp_nuclei_channel": "DAPI",
            "cp_cell_channel": "PhalloAF750",
            "cp_mito_channel": "ZO1AF488",
            "sbs_nuclei_channel": "DAPI",
            "sbs_cell_channel": "PhalloAF750",
            "sbs_mito_channel": "ZO1AF488",
        }
    )

    with exp_init_path.open("w") as f:
        json.dump(exp_init_data, f, indent=4)

    # Verify the modified configuration
    with exp_init_path.open() as f:
        modified_config = json.load(f)

    # Check that channel values were added
    assert modified_config["cp_nuclei_channel"] == "DAPI", (
        "cp_nuclei_channel not correctly set"
    )
    assert modified_config["cp_cell_channel"] == "PhalloAF750", (
        "cp_cell_channel not correctly set"
    )
    assert modified_config["cp_mito_channel"] == "ZO1AF488", (
        "cp_mito_channel not correctly set"
    )

    # Step 3: Generate inventory
    inventory_cmd = [
        "starrynight",
        "inventory",
        "gen",
        "-d",
        str(input_dir),
        "-o",
        str(inventory_dir),
    ]

    # Run the command and check it was successful
    result = subprocess.run(
        inventory_cmd, capture_output=True, text=True, check=False
    )

    # Check if the command was successful
    assert result.returncode == 0, (
        f"Inventory generation command failed: {result.stderr}"
    )

    # Verify the inventory file was created
    inventory_file = inventory_dir / "inventory.parquet"
    assert inventory_file.exists(), "Inventory file was not created"

    # Verify the inventory/inv directory exists (for temporary processing files)
    inv_dir = inventory_dir / "inv"
    assert inv_dir.exists(), "Inventory 'inv' subdirectory was not created"

    # Step 4: Generate index
    index_gen_cmd = [
        "starrynight",
        "index",
        "gen",
        "-i",
        str(inventory_file),
        "-o",
        str(index_dir),
    ]

    # Create the index directory if it doesn't exist
    index_dir.mkdir(exist_ok=True, parents=True)

    # Run the command and check it was successful
    result = subprocess.run(
        index_gen_cmd, capture_output=True, text=True, check=False
    )

    # Check if the command was successful
    assert result.returncode == 0, (
        f"Index generation command failed: {result.stderr}"
    )

    # Verify the index file was created
    index_file = index_dir / "index.parquet"
    assert index_file.exists(), "Index file was not created"

    # Step 5: Create experiment file
    exp_create_cmd = [
        "starrynight",
        "exp",
        "new",
        "-i",
        str(index_file),
        "-e",
        "Pooled CellPainting [Generic]",
        "-c",
        str(exp_init_path),
        "-o",
        str(workspace_dir),
    ]

    # Run the command and check it was successful
    result = subprocess.run(
        exp_create_cmd, capture_output=True, text=True, check=False
    )

    # Check if the command was successful
    assert result.returncode == 0, (
        f"Experiment file creation command failed: {result.stderr}"
    )

    # Verify the experiment.json file was created
    experiment_json_path = workspace_dir / "experiment.json"
    assert experiment_json_path.exists(), "experiment.json was not created"

    # Read the experiment file and check key configurations
    with experiment_json_path.open() as f:
        experiment_config = json.load(f)

    # Verify the experiment file contains expected keys (list a subset of keys)
    expected_exp_keys = [
        "dataset_id",
        "index_path",
        "inventory_path",
        "sbs_config",
        "cp_config",
        "use_legacy",
    ]

    for key in expected_exp_keys:
        assert key in experiment_config, (
            f"Key '{key}' missing in experiment.json"
        )

    # Verify channel configurations were correctly transferred from experiment_init.json
    assert experiment_config["cp_config"]["nuclei_channel"] == "DAPI", (
        "nuclei_channel not correctly set in cp_config"
    )
    assert experiment_config["cp_config"]["cell_channel"] == "PhalloAF750", (
        "cell_channel not correctly set in cp_config"
    )
    assert experiment_config["cp_config"]["mito_channel"] == "ZO1AF488", (
        "mito_channel not correctly set in cp_config"
    )

    # Return the paths needed for subsequent processing steps
    return {
        "index_file": index_file,
        "experiment_json_path": experiment_json_path,
    }


@pytest.fixture(scope="function")
def fix_starrynight_pregenerated_setup(fix_s1_workspace):
    """Fixture that provides pre-generated files for basic StarryNight workflow setup.

    Instead of running steps 1-5 of the getting-started workflow, this fixture
    loads pre-generated files from the fixtures directory. This makes tests run faster
    when you're only testing the LoadData generation step.

    Returns:
        dict: Dictionary containing:
            - index_file: Path to the pre-generated index.parquet file
            - experiment_json_path: Path to the pre-generated experiment.json file

    """
    # Get paths to workspace and fixtures
    workspace_dir = fix_s1_workspace["workspace_dir"]
    fixtures_dir = Path(__file__).parent / "fixtures" / "basic_setup"

    # Define paths to pre-generated files in fixtures directory
    pregenerated_index_file = fixtures_dir / "index.parquet"
    pregenerated_experiment_json = fixtures_dir / "experiment.json"

    # Ensure the pre-generated files exist
    assert pregenerated_index_file.exists(), (
        f"Pre-generated index file not found at {pregenerated_index_file}"
    )
    assert pregenerated_experiment_json.exists(), (
        f"Pre-generated experiment file not found at {pregenerated_experiment_json}"
    )

    # Copy files to workspace directory to maintain expected structure
    index_file = fix_s1_workspace["index_dir"] / "index.parquet"
    experiment_json_path = workspace_dir / "experiment.json"

    # Create parent directories if they don't exist
    index_file.parent.mkdir(parents=True, exist_ok=True)

    # Copy the files
    shutil.copy2(pregenerated_index_file, index_file)
    shutil.copy2(pregenerated_experiment_json, experiment_json_path)

    # Return the same structure as fix_starrynight_basic_setup
    return {
        "index_file": index_file,
        "experiment_json_path": experiment_json_path,
    }
