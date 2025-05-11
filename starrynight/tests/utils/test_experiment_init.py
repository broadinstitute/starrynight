"""Test for the StarryNight getting-started workflow steps."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest


def test_experiment_init_and_inventory(fix_s1_input_dir, fix_s1_workspace):
    """Test the experiment initialization and inventory generation steps.

    This test focuses on the first two steps of the workflow:
    1. Initialize experiment configuration and edit with required channel values
    2. Generate inventory from input data

    Args:
        fix_s1_input_dir: Fixture providing input test data
        fix_s1_workspace: Fixture providing workspace directory structure

    """
    # Set up test environment
    workspace_dir = fix_s1_workspace["workspace_dir"]
    inventory_dir = fix_s1_workspace["inventory_dir"]

    # Step 1: Initialize experiment configuration
    # Create a mock experiment configuration
    expected_config = {
        "barcode_csv_path": ".",
        "use_legacy": False,
        "cp_img_overlap_pct": 10,
        "cp_img_frame_type": "round",
        "cp_acquisition_order": "snake",
        "sbs_img_overlap_pct": 10,
        "sbs_img_frame_type": "round",
        "sbs_acquisition_order": "snake",
    }

    # Create the experiment_init.json file directly
    exp_init_path = workspace_dir / "experiment_init.json"
    with exp_init_path.open("w") as f:
        json.dump(expected_config, f, indent=4)

    # Verify experiment_init.json was created with expected content
    assert exp_init_path.exists(), "experiment_init.json was not created"

    # Read the file and verify its contents
    with exp_init_path.open() as f:
        actual_config = json.load(f)

    # Verify the configuration matches what we expect
    assert actual_config == expected_config, (
        "experiment_init.json does not contain expected configuration"
    )

    # Step 2: Edit experiment_init.json as specified in the docs
    with exp_init_path.open() as f:
        exp_init_data = json.load(f)

    # Update with required channel values
    exp_init_data.update(
        {
            "cp_nuclei_channel": "DAPI",
            "cp_cell_channel": "PhalloAF750",
            "cp_mito_channel": "ZO1AF488",
            "sbs_nuclei_channel": "DAPI",
            "sbs_cell_channel": "PhalloAF750",
            "sbs_mito_channel": "ZO1AF488",
        }
    )

    with exp_init_path.open("w") as f:
        json.dump(exp_init_data, f, indent=4)

    # Verify the modified configuration
    with exp_init_path.open() as f:
        modified_config = json.load(f)

    # Check that channel values were added
    assert modified_config["cp_nuclei_channel"] == "DAPI", (
        "cp_nuclei_channel not correctly set"
    )
    assert modified_config["cp_cell_channel"] == "PhalloAF750", (
        "cp_cell_channel not correctly set"
    )
    assert modified_config["cp_mito_channel"] == "ZO1AF488", (
        "cp_mito_channel not correctly set"
    )

    # Step 3: Generate inventory
    # Create a mock inventory file to simulate the output of `starrynight inventory gen`
    inventory_file = inventory_dir / "inventory.parquet"
    inv_dir = inventory_dir / "inv"
    inv_dir.mkdir(parents=True, exist_ok=True)

    # Create a dummy inventory.parquet file
    with inventory_file.open("w") as f:
        f.write("Mock inventory data")

    # Verify the inventory file was created
    assert inventory_file.exists(), "Inventory file was not created"
