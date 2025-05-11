"""Tests for fixture functionality."""

from pathlib import Path

import pytest

# Fixtures are automatically available from conftest.py


def test_fix_s1_input_fixtures(fix_s1_input_dir, fix_s1_workspace):
    """Test that our FIX-S1 input test fixtures are working correctly."""
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
    assert fix_s1_workspace["inventory_inv_dir"].exists()
    assert fix_s1_workspace["cp_illum_calc_dir"].exists()
    assert fix_s1_workspace["cp_illum_apply_dir"].exists()
    assert fix_s1_workspace["sbs_illum_calc_dir"].exists()
    assert fix_s1_workspace["sbs_illum_apply_dir"].exists()
    assert fix_s1_workspace["experiment_json"].exists()
    assert fix_s1_workspace["experiment_init_json"].exists()

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


def test_fix_s1_output_fixtures(fix_s1_output_dir):
    """Test that our FIX-S1 output test fixtures are working correctly."""
    # Verify that the fix_s1_output_dir fixture provides the expected paths
    assert fix_s1_output_dir["output_dir"].exists()
    assert fix_s1_output_dir["workspace_dir"].exists()
    assert fix_s1_output_dir["load_data_csv_dir"].exists()

    # Check for load data CSV files
    load_data_files = list(
        fix_s1_output_dir["load_data_csv_dir"].glob("**/load_data_*.csv")
    )
    assert len(load_data_files) > 0, (
        "No LoadData CSV files found in the output data"
    )

    # Print the directory structure for debugging
    print(f"FIX-S1 output directory: {fix_s1_output_dir['output_dir']}")
    print(f"FIX-S1 output workspace: {fix_s1_output_dir['workspace_dir']}")

    # Print a few LoadData CSV file paths
    print("FIX-S1 LoadData CSV files:")
    for csv_file in load_data_files[:3]:  # Show the first 3 files
        print(f"  {csv_file}")
