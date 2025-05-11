"""Tests for fixture functionality."""

from pathlib import Path

import pytest

# Fixtures are automatically available from conftest.py


def test_fix_s1_fixtures(fix_s1_input_dir, fix_s1_workspace):
    """Test that our FIX-S1 test fixtures are working correctly."""
    # Verify that the fix_s1_input_dir fixture provides the expected paths
    assert fix_s1_input_dir["input_dir"].exists()
    assert fix_s1_input_dir["data_dir"].exists()

    # Verify that we can find image files in the data directory
    images = list(fix_s1_input_dir["data_dir"].glob("**/*.tiff"))
    assert len(images) > 0, "No test images found in the FIX-S1 input data"

    # Verify the fix_s1_workspace fixture creates the expected structure
    assert fix_s1_workspace["workspace_dir"].exists()
    assert fix_s1_workspace["index_dir"].exists()
    assert fix_s1_workspace["inventory_dir"].exists()
    assert fix_s1_workspace["loaddata_dir"].exists()
    assert fix_s1_workspace["cppipe_dir"].exists()
    assert fix_s1_workspace["illum_dir"].exists()

    # Verify we can write to these directories
    test_file = fix_s1_workspace["workspace_dir"] / "test_file.txt"
    test_file.write_text("Test content")
    assert test_file.exists()

    # Print the directory structure for debugging
    print(f"FIX-S1 input directory: {fix_s1_input_dir['input_dir']}")
    print(f"FIX-S1 workspace directory: {fix_s1_workspace['workspace_dir']}")

    # Print a few image paths
    print("FIX-S1 test images:")
    for img in images[:3]:  # Show the first 3 images
        print(f"  {img}")
