"""Regenerates fixture files for faster test execution.

Usage:
    REGENERATE_FIXTURES=1 uv run pytest -xvs fixtures/integration/pregenerated_files/regenerate.py::test_generate_pregenerated_files_files[fix_s1]

"""

import os
import shutil
from pathlib import Path

import pytest


@pytest.mark.skipif(
    os.getenv("REGENERATE_FIXTURES") != "1",
    reason="Only run manually to regenerate fixtures; set REGENERATE_FIXTURES=1 to run",
)
@pytest.mark.parametrize(
    "fixture_id",
    [
        "fix_s1",
        "fix_s2",
    ],
)
def test_generate_pregenerated_files_files(fixture_id, request):
    """Generate experiment.json and index.parquet files for the pregenerated_files fixture.

    This test uses the fix_starrynight_setup fixture with the "generated" parameter
    to create fresh copies of these files and save them to the fixtures/pregenerated_files
    directory.

    Run with:
    pytest fixtures/pregenerated_files/regenerate.py::test_generate_pregenerated_files_files[fix_s1]
    """
    # Get the fixture dynamically
    setup_fixture = request.getfixturevalue(
        fixture_id + "_starrynight_generated"
    )

    # Get file paths from the fixture
    index_file = setup_fixture["index_file"]
    experiment_json_path = setup_fixture["experiment_json_path"]

    # Get the target directory (where this file is located)
    target_dir = Path(__file__).parent

    # Copy the files to the current directory
    shutil.copy2(index_file, target_dir / fixture_id / "index.parquet")
    shutil.copy2(
        experiment_json_path, target_dir / fixture_id / "experiment.json"
    )

    print(f"Files copied to: {target_dir}")
    print(f"Fixture ID: {fixture_id}")
    print("- index.parquet")
    print("- experiment.json")
