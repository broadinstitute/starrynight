"""Global pytest fixtures and configuration.

Place shared test fixtures here to make them available to all tests.
"""

import os
import shutil
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
