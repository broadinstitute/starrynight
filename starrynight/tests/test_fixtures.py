"""Tests for fixture functionality."""

import json
from pathlib import Path

import pandas as pd
import pytest

# Fixtures are automatically available from conftest.py

# Note on fixture relationships:
# - fix_starrynight_basic_setup: Runs CLI workflow to generate test files (slow but validates CLI)
# - fix_starrynight_pregenerated_setup: Copies pre-generated files (fast, for downstream tests)
# Both fixtures provide the same output contract but serve different testing purposes.


def test_fix_s1_input_dir(fix_s1_input_dir):
    """Test that the FIX-S1 input directory fixture is working correctly.

    Note: Basic existence checks are already performed in the fixture itself.
    This test focuses on validating functional aspects and contents.
    """
    # Verify that we can find image files in the input directory
    images = list(fix_s1_input_dir["input_dir"].glob("**/*.tiff"))
    assert len(images) > 0, "No test images found in the FIX-S1 input data"

    # Verify structure - should contain source folders
    source_dirs = [
        d
        for d in fix_s1_input_dir["input_dir"].iterdir()
        if d.is_dir() and d.name.startswith("Source")
    ]
    assert len(source_dirs) > 0, "No Source directories found in input data"

    # Print the directory structure for debugging
    print(f"FIX-S1 input directory: {fix_s1_input_dir['input_dir']}")

    # Print a few image paths
    print("FIX-S1 test images:")
    for img in (
        images[:3] if len(images) >= 3 else images
    ):  # Show up to 3 images
        print(f"  {img}")


def test_fix_s1_workspace(fix_s1_workspace):
    """Test that the FIX-S1 workspace fixture is working correctly.

    Note: The fixture already ensures directory creation.
    This test focuses on functional validation of the workspace.
    """
    # Verify all keys are present in the returned dictionary
    expected_keys = [
        "workspace_dir",
        "index_dir",
        "inventory_dir",
        "inventory_inv_dir",
        "cp_illum_calc_dir",
        "cp_illum_apply_dir",
        "sbs_illum_calc_dir",
        "sbs_illum_apply_dir",
        "experiment_json",
        "experiment_init_json",
    ]
    for key in expected_keys:
        assert key in fix_s1_workspace, (
            f"Missing '{key}' in workspace fixture output"
        )

    # Verify we can write to these directories (functional test)
    test_file = fix_s1_workspace["workspace_dir"] / "test_file.txt"
    test_file.write_text("Test content")
    assert test_file.exists()

    # Print the directory structure for debugging
    print(f"FIX-S1 workspace directory: {fix_s1_workspace['workspace_dir']}")


def test_fix_s1_output_dir(fix_s1_output_dir):
    """Test that the FIX-S1 output directory fixture is working correctly.

    Note: Basic existence checks are already performed in the fixture itself.
    This test focuses on validating functional aspects and contents.
    """
    # Verify all keys are present in the returned dictionary
    expected_keys = [
        "base_dir",
        "output_dir",
        "workspace_dir",
        "load_data_csv_dir",
    ]
    for key in expected_keys:
        assert key in fix_s1_output_dir, (
            f"Missing '{key}' in output fixture output"
        )

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


@pytest.mark.parametrize(
    "fixture_name",
    ["fix_starrynight_basic_setup", "fix_starrynight_pregenerated_setup"],
)
def test_starrynight_setup_fixtures(fixture_name, request):
    """Test both workflow setup fixtures with identical validation logic.

    Both fixtures provide the exact same output contract (index.parquet and experiment.json files),
    but they generate these files differently:

    - fix_starrynight_basic_setup: Runs the actual CLI commands to generate files (slow but validates CLI)
    - fix_starrynight_pregenerated_setup: Copies pre-generated files for faster testing

    This test uses parameterization to run identical validation on both fixtures,
    ensuring they both provide output that meets the same requirements.
    """
    # Get the fixture from the name
    setup_fixture = request.getfixturevalue(fixture_name)

    # Validate fixture structure
    assert isinstance(setup_fixture, dict), "Fixture should return a dictionary"
    assert "index_file" in setup_fixture, "Missing index_file in fixture output"
    assert "experiment_json_path" in setup_fixture, (
        "Missing experiment_json_path in fixture output"
    )

    # Get paths from fixture
    index_file = setup_fixture["index_file"]
    experiment_json_path = setup_fixture["experiment_json_path"]
    assert index_file.suffix == ".parquet", "Index file is not a parquet file"

    # Validate index.parquet file
    try:
        # Open and validate parquet file
        df = pd.read_parquet(index_file)
        assert len(df) > 0, "Index parquet file is empty"

        # Check for essential columns
        essential_columns = [
            "dataset_id",
            "plate_id",
            "well_id",
            "site_id",
            "extension",
            "is_sbs_image",
            "is_image",
            "channel_dict",
        ]
        for col in essential_columns:
            assert col in df.columns, (
                f"Missing essential column '{col}' in index file"
            )

    except Exception as e:
        pytest.fail(f"Failed to validate index parquet file: {e}")

    # Validate experiment.json file
    try:
        with experiment_json_path.open() as f:
            experiment_config = json.load(f)

        # Check for essential sections
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

    # Verify data type coverage - check both SBS and CP images exist
    sbs_images = df[df["is_sbs_image"]]
    cp_images = df[(~df["is_sbs_image"]) & df["is_image"]]
    assert len(sbs_images) > 0, "No SBS images found in index"
    assert len(cp_images) > 0, "No CP (non-SBS) images found in index"

    # Verify well/site structure - check for multiple wells and sites
    unique_wells = df["well_id"].nunique()
    assert unique_wells >= 2, f"Expected multiple wells, found {unique_wells}"

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

    # Print some debug information
    print(f"Fixture: {fixture_name}")
    print(f"Index file location: {index_file}")
    print(f"Experiment JSON location: {experiment_json_path}")
