import json
import shutil
from pathlib import Path

import pooch
import pytest
from click.testing import CliRunner
from pooch import Untar

from starrynight.cli.exp import init as exp_init
from starrynight.cli.exp import new as exp_new
from starrynight.cli.index import gen_index
from starrynight.cli.inv import gen_inv

# Comprehensive fixture configuration
FIXTURE_CONFIGS = {
    "fix_s1": {
        # Channel configurations
        "channels": {
            "cp_nuclei_channel": "DAPI",
            "cp_cell_channel": "PhalloAF750",
            "cp_mito_channel": "ZO1AF488",
            "sbs_nuclei_channel": "DAPI",
            "sbs_cell_channel": "PhalloAF750",
            "sbs_mito_channel": "ZO1AF488",
        },
        # Input configuration
        "input": {
            "archive_name": "fix_s1_input.tar.gz",
            "dir_prefix": "fix_s1_input_test",
            "dir_name": "fix_s1_input",
            "dataset_dir_name": "Source1",
            "sha256": "ddba28e1593986013d10880678d2d7715af8d2ee1cfa11ae7bcea4d50c30f9e0",
        },
        # Output configuration
        "output": {
            "archive_name": "fix_s1_output.tar.gz",
            "dir_prefix": "fix_s1_output_test",
            "dir_name": "fix_s1_pcpip_output",
            "dataset_dir_name": "Source1",
            "sha256": "a84788c2d5296c02e58c38c382c9b4019c414162a58021a7bfc7c5f20a38be2a",
        },
    },
    "fix_s2": {
        # Channel configurations
        "channels": {
            "cp_nuclei_channel": "DAPI",
            "cp_cell_channel": "PhalloAF750",
            "cp_mito_channel": "ZO1AF488",
            "sbs_nuclei_channel": "DAPI",
            "sbs_cell_channel": "PhalloAF750",
            "sbs_mito_channel": "ZO1AF488",
        },
        # Input configuration
        "input": {
            "archive_name": "fix_s1_input.tar.gz",
            "dir_prefix": "fix_s1_input_test",
            "dir_name": "fix_s1_input",
            "dataset_dir_name": "Source1",
            "sha256": "ddba28e1593986013d10880678d2d7715af8d2ee1cfa11ae7bcea4d50c30f9e0",
        },
        # Output configuration
        "output": {
            "archive_name": "fix_s1_output.tar.gz",
            "dir_prefix": "fix_s1_output_test",
            "dir_name": "fix_s1_pcpip_output",
            "dataset_dir_name": "Source1",
            "sha256": "a84788c2d5296c02e58c38c382c9b4019c414162a58021a7bfc7c5f20a38be2a",
        },
    },
}

# Configure a single Pooch registry for all test data
STARRYNIGHT_CACHE = pooch.create(
    path=pooch.os_cache("starrynight"),
    base_url="https://github.com/shntnu/starrynight/releases/download/v0.0.1/",
    registry={
        # Dynamically create registry from FIXTURE_CONFIGS
        config["input"]["archive_name"]: f"sha256:{config['input']['sha256']}"
        for fixture_id, config in FIXTURE_CONFIGS.items()
    }
    | {
        # Add output archives
        config["output"]["archive_name"]: f"sha256:{config['output']['sha256']}"
        for fixture_id, config in FIXTURE_CONFIGS.items()
    },
)


def _setup_input_dir(
    tmp_path_factory: pytest.TempPathFactory,
    fixture_id: str,
) -> dict[str, Path]:
    """Set up an input directory from a test archive.

    Args:
        tmp_path_factory: pytest fixture for creating temporary directories
        fixture_id: Identifier for the fixture configuration to use

    Returns:
        dict: Dictionary with base_dir and input_dir paths

    """
    # Get configuration for this fixture
    config = FIXTURE_CONFIGS.get(fixture_id)
    if not config:
        raise ValueError(f"Unknown fixture ID: {fixture_id}")

    input_config = config["input"]

    # Create a temporary directory
    base_dir = tmp_path_factory.mktemp(input_config["dir_prefix"])

    # Use pooch to download and extract in one step
    STARRYNIGHT_CACHE.fetch(
        input_config["archive_name"], processor=Untar(extract_dir=str(base_dir))
    )

    # Create paths to important directories
    input_dir = base_dir / input_config["dir_name"]

    # Essential check: did extraction work at all?
    assert input_dir.exists(), "Input test data not extracted correctly"

    # Check that at least one expected dataset directory exists
    dataset_dir = input_dir / input_config["dataset_dir_name"]
    assert dataset_dir.exists(), (
        f"Expected {input_config['dataset_dir_name']} directory not found in input data"
    )

    # Verify that image files exist in the input directory
    image_files = list(input_dir.glob("**/*.tiff"))
    if not image_files:
        # Try alternative extensions
        image_files = list(input_dir.glob("**/*.tif"))

    assert len(image_files) > 0, (
        f"No image files (*.tiff, *.tif) found in {input_config['dir_name']}"
    )

    return {"base_dir": base_dir, "input_dir": input_dir}


def _setup_output_dir(
    tmp_path_factory: pytest.TempPathFactory,
    fixture_id: str,
) -> dict[str, Path]:
    """Set up an output directory from a test archive.

    Args:
        tmp_path_factory: pytest fixture for creating temporary directories
        fixture_id: Identifier for the fixture configuration to use

    Returns:
        dict: Dictionary with paths to key directories

    """
    # Get configuration for this fixture
    config = FIXTURE_CONFIGS.get(fixture_id)
    if not config:
        raise ValueError(f"Unknown fixture ID: {fixture_id}")

    output_config = config["output"]

    # Create a temporary directory
    base_dir = tmp_path_factory.mktemp(output_config["dir_prefix"])

    # Use pooch to download and extract in one step
    STARRYNIGHT_CACHE.fetch(
        output_config["archive_name"],
        processor=Untar(extract_dir=str(base_dir)),
    )

    # Create paths to important directories
    output_dir = base_dir / output_config["dir_name"]
    workspace_dir = output_dir / output_config["dataset_dir_name"] / "workspace"
    load_data_csv_dir = workspace_dir / "load_data_csv"

    # Essential check: did extraction create the main output directory?
    assert output_dir.exists(), "Output test data not extracted correctly"
    assert workspace_dir.exists(), (
        f"Workspace directory not found in {output_config['dataset_dir_name']} output data"
    )

    # Verify that load_data_csv directory exists
    assert load_data_csv_dir.exists(), (
        f"load_data_csv directory not found in {output_config['dataset_dir_name']} workspace"
    )

    # Check for LoadData CSV files
    load_data_files = list(load_data_csv_dir.glob("load_data_*.csv"))
    assert len(load_data_files) > 0, (
        f"No LoadData CSV files found in {output_config['dataset_dir_name']} output data"
    )

    return {
        "base_dir": base_dir,
        "output_dir": output_dir,
        "workspace_dir": workspace_dir,
        "load_data_csv_dir": load_data_csv_dir,
    }


def _setup_workspace(
    tmp_path_factory: pytest.TempPathFactory, fixture_id: str
) -> dict[str, Path]:
    """Create a workspace directory structure for tests.

    Args:
        tmp_path_factory: pytest fixture for creating temporary directories
        fixture_id: Fixture identifier (e.g., 'fix_s1', 'fix_s2')

    Returns:
        dict: Dictionary with paths to key directories in the workspace

    """
    # Create workspace prefix from fixture_id
    workspace_prefix = f"{fixture_id}_workspace"

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


def _handle_generated_setup(
    workspace: dict[str, Path],
    input_dir: Path,
    fixture_id: str,
) -> dict[str, Path]:
    """Set up a StarryNight workflow environment using CLI commands.

    Args:
        workspace: Dictionary containing workspace directories
        input_dir: Path to input data directory
        fixture_id: Fixture identifier (e.g., 'fix_s1', 'fix_s2')

    Returns:
        dict: Dictionary with index_file and experiment_json_path

    """
    # Get configuration for this fixture
    config = FIXTURE_CONFIGS.get(fixture_id)
    if not config:
        raise ValueError(f"Unknown fixture ID: {fixture_id}")

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
    exp_init_data.update(config["channels"])

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
    # Validate the fixture ID
    if fixture_id not in FIXTURE_CONFIGS:
        raise ValueError(
            f"Unknown fixture ID: {fixture_id}. Must be one of: {', '.join(FIXTURE_CONFIGS.keys())}"
        )

    workspace_dir = workspace["workspace_dir"]

    # Use fixture-specific subdirectory for pregenerated files
    # Each fixture must have its own subdirectory under pregenerated_files
    fixtures_base_dir = Path(__file__).parent / "pregenerated_files"
    fixtures_dir = fixtures_base_dir / fixture_id

    # If fixture directory doesn't exist, fall back to pregenerated_files for backward compatibility
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


def _setup_starrynight(
    workspace: dict[str, Path],
    input_dir_fixture: dict[str, Path],
    fixture_id: str,
    mode: str,
) -> dict[str, Path]:
    """Set up the StarryNight workflow environment.

    Args:
        workspace: Dictionary containing workspace directories
        input_dir_fixture: Dict containing input directory information
        fixture_id: Fixture identifier (e.g., 'fix_s1', 'fix_s2')
        mode: Setup mode ("generated" or "pregenerated")

    Returns:
        dict: Dictionary containing index_file and experiment_json_path

    """
    # Validate the fixture ID
    if fixture_id not in FIXTURE_CONFIGS:
        raise ValueError(
            f"Unknown fixture ID: {fixture_id}. Must be one of: {', '.join(FIXTURE_CONFIGS.keys())}"
        )

    # Execute the appropriate setup based on mode parameter
    if mode == "generated":
        return _handle_generated_setup(
            workspace, input_dir_fixture["input_dir"], fixture_id
        )
    elif mode == "pregenerated":
        return _handle_pregenerated_setup(workspace, fixture_id)
    else:
        raise ValueError(f"Unknown mode: {mode}")
