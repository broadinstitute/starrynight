"""Utility to generate the basic setup fixture files.

This file is used to regenerate the experiment.json and index.parquet files
in the basic_setup directory. It's skipped by default and should only be run
manually when you need to update these files.

Usage:
    REGENERATE_FIXTURES=1 uv run pytest -xvs fixtures/basic_setup/generate_fixtures.py
"""

import os
import shutil
from pathlib import Path

import pytest


@pytest.mark.skipif(
    os.getenv("REGENERATE_FIXTURES") != "1",
    reason="Only run manually to regenerate fixtures; set REGENERATE_FIXTURES=1 to run",
)
def test_generate_basic_setup_files(fix_starrynight_setup):
    """Generate experiment.json and index.parquet files for the basic_setup fixture.

    This test uses the fix_starrynight_setup fixture with the "generated" parameter
    to create fresh copies of these files and save them to the fixtures/basic_setup
    directory.
    """
    # Get file paths from the fixture
    index_file = fix_starrynight_setup["index_file"]
    experiment_json_path = fix_starrynight_setup["experiment_json_path"]

    # Get the target directory (where this file is located)
    target_dir = Path(__file__).parent

    # Copy the files to the current directory
    shutil.copy2(index_file, target_dir / "index.parquet")
    shutil.copy2(experiment_json_path, target_dir / "experiment.json")

    print(f"Files copied to: {target_dir}")
    print("- index.parquet")
    print("- experiment.json")


# Apply the "generated" parameter to the fixture
pytestmark = pytest.mark.parametrize(
    "fix_starrynight_setup", ["generated"], indirect=True
)
