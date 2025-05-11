"""Tests for fixture functionality."""

from pathlib import Path

import pytest

# Fixtures are automatically available from conftest.py


def test_test_data_fixtures(test_data_dir, test_workspace):
    """Test that our test data fixtures are working correctly."""
    # Verify that the test_data_dir fixture provides the expected paths
    assert test_data_dir["input_dir"].exists()
    assert test_data_dir["data_dir"].exists()

    # Verify that we can find image files in the data directory
    images = list(test_data_dir["data_dir"].glob("**/*.tiff"))
    assert len(images) > 0, "No test images found in the test data"

    # Verify the test_workspace fixture creates the expected structure
    assert test_workspace["workspace_dir"].exists()
    assert test_workspace["index_dir"].exists()
    assert test_workspace["inventory_dir"].exists()
    assert test_workspace["loaddata_dir"].exists()
    assert test_workspace["cppipe_dir"].exists()
    assert test_workspace["illum_dir"].exists()

    # Verify we can write to these directories
    test_file = test_workspace["workspace_dir"] / "test_file.txt"
    test_file.write_text("Test content")
    assert test_file.exists()

    # Print the directory structure for debugging
    print(f"Test data directory: {test_data_dir['input_dir']}")
    print(f"Test workspace directory: {test_workspace['workspace_dir']}")

    # Print a few image paths
    print("Test images:")
    for img in images[:3]:  # Show the first 3 images
        print(f"  {img}")
