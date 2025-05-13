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

    # Verify the archive (essential for fixture to function)
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

    # Verify the archive (essential for fixture to function)
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

    # Essential check: did extraction work at all?
    assert input_dir.exists(), "Input test data not extracted correctly"

    # Check that at least one expected subdirectory exists
    assert (input_dir / "Source1").exists(), (
        "Expected Source1 directory not found in input data"
    )

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

    # Essential check: did extraction create the main output directory?
    assert output_dir.exists(), "Output test data not extracted correctly"
    assert workspace_dir.exists(), (
        "Workspace directory not found in output data"
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
def fix_starrynight_setup(request, fix_s1_input_dir, fix_s1_workspace):
    """Fixture that sets up the StarryNight workflow environment.

    This fixture can operate in two modes, specified through indirect parameterization:
    - "generated": Executes actual CLI commands to generate all files (slow but thorough)
    - "pregenerated": Uses pre-generated files from fixtures (fast)

    Use indirect parameterization to specify the mode:
    @pytest.mark.parametrize("fix_starrynight_setup", ["generated"], indirect=True)
    @pytest.mark.parametrize("fix_starrynight_setup", ["pregenerated"], indirect=True)

    The default mode is "generated" if no parameter is specified.

    Performs steps 1-5 of the getting-started workflow when using "generated" mode:
    1. Initialize experiment configuration
    2. Edit configuration with required channel values
    3. Generate inventory from input data
    4. Generate index from inventory
    5. Create experiment file from index and configuration

    "pregenerated" mode copies pre-made files without running CLI commands.

    Returns:
        dict: Dictionary containing:
            - index_file: Path to the generated/pre-generated index.parquet file
            - experiment_json_path: Path to the generated/pre-generated experiment.json file

    """
    # Default to "generated" mode if no parameter is specified
    param = getattr(request, "param", "generated")

    if param == "generated":
        # Set up test environment
        workspace_dir = fix_s1_workspace["workspace_dir"]
        inventory_dir = fix_s1_workspace["inventory_dir"]
        index_dir = fix_s1_workspace["index_dir"]
        input_dir = fix_s1_input_dir["input_dir"]

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

        # Step 1 complete, proceed to next step

        # Verify experiment_init.json was created (essential for next steps)
        exp_init_path = workspace_dir / "experiment_init.json"
        assert exp_init_path.exists(), "experiment_init.json was not created"

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

    elif param == "pregenerated":
        # Get paths to workspace and fixtures
        workspace_dir = fix_s1_workspace["workspace_dir"]
        fixtures_dir = Path(__file__).parent / "fixtures" / "basic_setup"

        # Define paths to pre-generated files in fixtures directory
        pregenerated_index_file = fixtures_dir / "index.parquet"
        pregenerated_experiment_json = fixtures_dir / "experiment.json"

        # Essential checks: source files must exist to be copied
        assert pregenerated_index_file.exists(), (
            "Pre-generated index file not found"
        )
        assert pregenerated_experiment_json.exists(), (
            "Pre-generated experiment file not found"
        )

        # Copy files to workspace directory to maintain expected structure
        index_file = fix_s1_workspace["index_dir"] / "index.parquet"
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
    else:
        raise ValueError(f"Unknown parameter: {param}")
