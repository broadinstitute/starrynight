"""Tests for fixture functionality."""

import json
from pathlib import Path

import pandas as pd
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


def test_fix_starrynight_basic_setup(fix_starrynight_basic_setup):
    """Test that the basic StarryNight workflow setup fixture works correctly.

    This test verifies that fix_starrynight_basic_setup properly executes the
    initial workflow steps 1-5 from the getting-started guide:
    1. Initialize experiment configuration
    2. Edit configuration with required channel values
    3. Generate inventory from input data
    4. Generate index from inventory
    5. Create experiment file from index and configuration
    """
    # Verify the fixture provides the expected dictionary structure
    assert isinstance(fix_starrynight_basic_setup, dict), (
        "Fixture should return a dictionary"
    )
    assert "index_file" in fix_starrynight_basic_setup, (
        "Missing index_file in fixture output"
    )
    assert "experiment_json_path" in fix_starrynight_basic_setup, (
        "Missing experiment_json_path in fixture output"
    )

    # Verify that the index file exists and is a valid parquet file
    index_file = fix_starrynight_basic_setup["index_file"]
    assert index_file.exists(), "Index file does not exist"
    assert index_file.suffix == ".parquet", "Index file is not a parquet file"

    # Verify the index file can be opened as a parquet file
    try:
        df = pd.read_parquet(index_file)
        assert len(df) > 0, "Index parquet file is empty"

        # Check for essential columns in the index
        essential_columns = [
            "dataset_id",
            "plate_id",
            "well_id",
            "site_id",
            "path",
            "extension",
        ]
        for col in essential_columns:
            assert col in df.columns, (
                f"Missing essential column '{col}' in index file"
            )

    except Exception as e:
        pytest.fail(f"Failed to read index parquet file: {e}")

    # Verify the experiment JSON file exists and contains valid JSON
    experiment_json_path = fix_starrynight_basic_setup["experiment_json_path"]
    assert experiment_json_path.exists(), "Experiment JSON file does not exist"

    # Verify the experiment JSON file contains the expected structure
    try:
        with experiment_json_path.open() as f:
            experiment_config = json.load(f)

        # Check for essential experiment config keys
        essential_keys = [
            "dataset_id",
            "index_path",
            "inventory_path",
            "cp_config",
            "sbs_config",
        ]
        for key in essential_keys:
            assert key in experiment_config, (
                f"Missing essential key '{key}' in experiment JSON"
            )

        # Verify that channel configurations were correctly set
        assert experiment_config["cp_config"]["nuclei_channel"] == "DAPI", (
            "nuclei_channel not correctly set in cp_config"
        )
        assert (
            experiment_config["cp_config"]["cell_channel"] == "PhalloAF750"
        ), "cell_channel not correctly set in cp_config"
        assert experiment_config["cp_config"]["mito_channel"] == "ZO1AF488", (
            "mito_channel not correctly set in cp_config"
        )

    except json.JSONDecodeError:
        pytest.fail("Experiment JSON file contains invalid JSON")
    except Exception as e:
        pytest.fail(f"Failed to validate experiment JSON: {e}")

    # Print some debug information
    print(f"Index file location: {index_file}")
    print(f"Experiment JSON location: {experiment_json_path}")
