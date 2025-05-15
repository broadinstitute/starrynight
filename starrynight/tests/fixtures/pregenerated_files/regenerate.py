"""Utility to generate the basic setup fixture files.

This file is used to regenerate the experiment.json and index.parquet files
in the pregenerated_files directory. It's skipped by default and should only be run
manually when you need to update these files.

Usage:
    REGENERATE_FIXTURES=1 uv run pytest -xvs fixtures/pregenerated_files/regenerate.py
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
    "fixture",
    [
        "fix_s1",
        # "fix_s2",
    ],
)
def test_generate_pregenerated_files_files(fixture, request):
    """Generate experiment.json and index.parquet files for the pregenerated_files fixture.

    This test uses the fix_starrynight_setup fixture with the "generated" parameter
    to create fresh copies of these files and save them to the fixtures/pregenerated_files
    directory.
    """
    # Get the fixture dynamically
    setup_fixture = request.getfixturevalue(fixture + "_starrynight_generated")

    # Get file paths from the fixture
    index_file = setup_fixture["index_file"]
    experiment_json_path = setup_fixture["experiment_json_path"]

    # Get the target directory (where this file is located)
    target_dir = Path(__file__).parent

    # Copy the files to the current directory
    shutil.copy2(index_file, target_dir / fixture / "index.parquet")
    shutil.copy2(experiment_json_path, target_dir / fixture / "experiment.json")

    print(f"Files copied to: {target_dir}")
    print("- index.parquet")
    print("- experiment.json")
