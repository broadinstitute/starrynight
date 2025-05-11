"""Global pytest fixtures and configuration.

Place shared test fixtures here to make them available to all tests.
"""

import shutil
import tarfile
import tempfile
from pathlib import Path

import pooch
import pytest


@pytest.fixture(scope="session")
def fix_s1_archive():
    """Fixture that downloads and caches the FIX-S1 test data archive.

    This fixture handles the input component of the standard FIX-S1 test fixture
    (small test fixture without stitchcrop and QC).

    Returns:
        str: Path to the downloaded archive file.

    """
    # Configure Pooch for test data management
    test_data = pooch.create(
        path=pooch.os_cache("starrynight"),
        base_url="https://github.com/shntnu/starrynight/releases/download/v0.0.1/",
        registry={
            "starrynight_test_data.tar.gz": "md5:d8e34bacf43453dfb9c65d9bf1162634"
        },
    )

    # Download and cache the test data
    archive_path = test_data.fetch("starrynight_test_data.tar.gz")

    # Verify the archive
    archive_path_obj = Path(archive_path)
    assert archive_path_obj.exists(), (
        "Test data archive not downloaded correctly"
    )
    assert tarfile.is_tarfile(archive_path_obj), (
        "Downloaded file is not a valid tar archive"
    )

    return archive_path


@pytest.fixture(scope="module")
def fix_s1_input_dir(tmp_path_factory, fix_s1_archive):
    """Fixture that provides a temporary directory with extracted FIX-S1 input data.

    This fixture handles the input component of the standard FIX-S1 test fixture
    (small test fixture without stitchcrop and QC).

    This fixture:
    1. Creates a temporary directory
    2. Extracts the FIX-S1 input data archive into it
    3. Yields a dictionary with paths to key directories
    4. Cleans up the temporary directory after the test is done

    Args:
        tmp_path_factory: pytest fixture for creating temporary directories
        fix_s1_archive: fixture providing the path to the FIX-S1 archive

    Returns:
        dict: Dictionary containing paths to key directories:
            - base_dir: The base temporary directory
            - input_dir: Path to the extracted starrynight_example_input directory
            - data_dir: Path to Source1/Batch1/images where the test images are located

    """
    # Create a temporary directory
    base_dir = tmp_path_factory.mktemp("starrynight_test")

    # Extract the archive
    with tarfile.open(fix_s1_archive, "r:gz") as tar:
        tar.extractall(path=base_dir)

    # Create paths to important directories
    input_dir = base_dir / "starrynight_example_input"
    data_dir = input_dir / "Source1" / "Batch1" / "images"

    # Verify the extraction worked correctly
    assert input_dir.exists(), "Test data not extracted correctly"
    assert data_dir.exists(), "Test data structure not as expected"

    yield {"base_dir": base_dir, "input_dir": input_dir, "data_dir": data_dir}

    # Cleanup is handled automatically by pytest's tmp_path_factory


@pytest.fixture(scope="function")
def fix_s1_workspace(tmp_path_factory):
    """Fixture that creates a workspace directory structure for FIX-S1 tests.

    This fixture creates a temporary directory with the structure needed for
    processing the FIX-S1 test fixture (small test fixture without stitchcrop and QC):

    - workspace/
      - index/
      - inventory/
      - cellprofiler/
        - loaddata/
          - cp/
            - illum/
              - illum_calc/
        - cppipe/
          - cp/
            - illum/
              - illum_calc/
      - illum/
        - cp/
          - illum_calc/

    Returns:
        dict: Dictionary with paths to key directories in the workspace

    """
    # Create base workspace directory
    workspace_dir = tmp_path_factory.mktemp("workspace")

    # Create subdirectories
    dir_structure = [
        "index",
        "inventory",
        "cellprofiler/loaddata/cp/illum/illum_calc",
        "cellprofiler/cppipe/cp/illum/illum_calc",
        "illum/cp/illum_calc",
    ]

    # Create each directory
    for dir_path in dir_structure:
        (workspace_dir / dir_path).mkdir(parents=True, exist_ok=True)

    # Return dictionary with paths
    return {
        "workspace_dir": workspace_dir,
        "index_dir": workspace_dir / "index",
        "inventory_dir": workspace_dir / "inventory",
        "loaddata_dir": workspace_dir
        / "cellprofiler"
        / "loaddata"
        / "cp"
        / "illum"
        / "illum_calc",
        "cppipe_dir": workspace_dir
        / "cellprofiler"
        / "cppipe"
        / "cp"
        / "illum"
        / "illum_calc",
        "illum_dir": workspace_dir / "illum" / "cp" / "illum_calc",
    }
