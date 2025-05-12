"""Tests for fixture functionality."""

import json
from pathlib import Path

import pandas as pd
import pytest

# Fixtures are automatically available from conftest.py


def test_fix_s1_input_dir(fix_s1_input_dir):
    """Test that the FIX-S1 input directory fixture is working correctly."""
    # Verify that the fix_s1_input_dir fixture provides the expected paths
    assert fix_s1_input_dir["input_dir"].exists()
    assert fix_s1_input_dir["base_dir"].exists()

    # Verify that we can find image files in the input directory
    images = list(fix_s1_input_dir["input_dir"].glob("**/*.tiff"))
    assert len(images) > 0, "No test images found in the FIX-S1 input data"

    # Print the directory structure for debugging
    print(f"FIX-S1 input directory: {fix_s1_input_dir['input_dir']}")

    # Print a few image paths
    print("FIX-S1 test images:")
    for img in (
        images[:3] if len(images) >= 3 else images
    ):  # Show up to 3 images
        print(f"  {img}")


def test_fix_s1_workspace(fix_s1_workspace):
    """Test that the FIX-S1 workspace fixture is working correctly."""
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
    print(f"FIX-S1 workspace directory: {fix_s1_workspace['workspace_dir']}")


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


@pytest.mark.skip(reason="Skipping test_fix_starrynight_basic_setup")
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
            "is_sbs_image",
            "is_image",
            "channel_dict",
        ]
        for col in essential_columns:
            assert col in df.columns, (
                f"Missing essential column '{col}' in index file"
            )

        # Verify data type coverage - check both SBS and CP images exist
        sbs_images = df[df["is_sbs_image"]]
        cp_images = df[(~df["is_sbs_image"]) & df["is_image"]]
        assert len(sbs_images) > 0, "No SBS images found in index"
        assert len(cp_images) > 0, "No CP (non-SBS) images found in index"

        # Verify well/site structure - check for multiple wells and sites
        unique_wells = df["well_id"].nunique()
        assert unique_wells >= 2, (
            f"Expected multiple wells, found {unique_wells}"
        )

        # Get sites per well count to verify multi-site structure
        sites_per_well = df.groupby("well_id")["site_id"].nunique()
        assert sites_per_well.min() >= 2, "Expected multiple sites per well"

        # Verify channel patterns - SBS and CP should have different channels
        if "channel_dict" in df.columns:
            # Get sample channel patterns from each image type
            sbs_channels = sbs_images["channel_dict"].iloc[0]
            cp_channels = cp_images["channel_dict"].iloc[0]
            assert len(sbs_channels) > 0, "Empty SBS channel pattern"
            assert len(cp_channels) > 0, "Empty CP channel pattern"
            # SBS and CP should have different channel patterns
            assert set(sbs_channels) != set(cp_channels), (
                "SBS and CP should have different channel patterns"
            )

        # Verify file types - without hardcoding specific extensions
        images = df[df["is_image"]]
        image_extensions = set(images["extension"].unique())
        assert len(image_extensions) > 0, "No image file extensions found"
        assert all(
            ext in ["tiff", "tif", "png", "jpg", "jpeg", "ome.tiff", "ome.tif"]
            for ext in image_extensions
        ), f"Found unexpected image extensions: {image_extensions}"

        # Verify consistent batch, dataset and plate values
        assert df["dataset_id"].nunique() == 1, "Multiple dataset IDs found"
        assert df["batch_id"].nunique() == 1, "Multiple batch IDs found"

    except Exception as e:
        pytest.fail(f"Failed to validate index parquet file: {e}")

    # Verify the experiment JSON file exists and contains valid JSON
    experiment_json_path = fix_starrynight_basic_setup["experiment_json_path"]
    assert experiment_json_path.exists(), "Experiment JSON file does not exist"

    # Just verify the experiment JSON file is valid and has basic structure
    try:
        with experiment_json_path.open() as f:
            experiment_config = json.load(f)

        # Only check for top-level presence of config sections
        assert "cp_config" in experiment_config, (
            "Missing cp_config section in experiment JSON"
        )
        assert "sbs_config" in experiment_config, (
            "Missing sbs_config section in experiment JSON"
        )

    except json.JSONDecodeError:
        pytest.fail("Experiment JSON file contains invalid JSON")
    except Exception as e:
        pytest.fail(f"Failed to validate experiment JSON: {e}")

    # Print some debug information
    print(f"Index file location: {index_file}")
    print(f"Experiment JSON location: {experiment_json_path}")
