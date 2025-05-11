"""Test for the StarryNight getting-started workflow steps.

This test module verifies the core functionality of the StarryNight getting-started
workflow by executing the actual CLI commands and verifying their outputs.

The workflow is outlined in ../../../docs/user/getting-started.md

Current scope:
- Experiment configuration initialization and editing
- Inventory file generation

Future extensions:
- Index generation from inventory (parsing file paths)
- Experiment file creation from index and configuration
- LoadData CSV generation for illumination correction
- CellProfiler pipeline generation
- Illumination correction execution

Testing strategy:
This module executes each StarryNight CLI command directly to test the actual
functionality of the workflow. This strategy:
1. Ensures the CLI commands work as expected
2. Tests the complete end-to-end workflow as a user would experience it
3. Validates that each workflow step produces the expected outputs
4. Allows for incremental testing as the workflow gets extended

Each workflow step is executed in sequence with appropriate assertions to
verify the correctness of outputs. The test uses the FIX-S1 input and workspace
fixtures for consistent and reusable test data.
"""

import json
import subprocess
from pathlib import Path

import pytest


def test_getting_started_workflow_phase1(fix_s1_input_dir, fix_s1_workspace):
    """Phase 1 of testing the getting-started workflow: experiment init and inventory generation.

    This test focuses on the first two steps of the workflow from getting-started.md:
    1. Initialize experiment configuration and edit with required channel values
    2. Generate inventory from input data

    This is the first part of a modular testing approach for the complete workflow.
    Future tests will extend this to cover index generation, experiment file creation,
    and LoadData file generation for illumination correction.

    This test executes the actual CLI commands to:
    - Initialize the experiment configuration using 'starrynight exp init'
    - Generate the inventory using 'starrynight inventory gen'

    This approach tests the actual commands as they would be used by a real user,
    ensuring that the CLI commands work as expected and produce the correct outputs.

    Args:
        fix_s1_input_dir: Fixture providing input test data with FIX-S1 structure
        fix_s1_workspace: Fixture providing workspace directory structure with expected paths

    """
    # Set up test environment
    workspace_dir = fix_s1_workspace["workspace_dir"]
    inventory_dir = fix_s1_workspace["inventory_dir"]
    data_dir = fix_s1_input_dir["data_dir"]

    # Step 1: Initialize experiment configuration
    # Execute the actual CLI command:
    #   starrynight exp init -e "Pooled CellPainting [Generic]" -o ${WKDIR}
    exp_init_cmd = [
        "starrynight",
        "exp",
        "init",
        "-e",
        "Pooled CellPainting [Generic]",
        "-o",
        str(workspace_dir),
    ]

    # Run the command and check it was successful
    result = subprocess.run(
        exp_init_cmd, capture_output=True, text=True, check=False
    )

    # Check if the command was successful
    assert result.returncode == 0, (
        f"Experiment init command failed: {result.stderr}"
    )

    # Define expected config properties
    expected_config_keys = [
        "barcode_csv_path",
        "use_legacy",
        "cp_img_overlap_pct",
        "cp_img_frame_type",
        "cp_acquisition_order",
        "sbs_img_overlap_pct",
        "sbs_img_frame_type",
        "sbs_acquisition_order",
    ]

    # Verify experiment_init.json was created
    exp_init_path = workspace_dir / "experiment_init.json"
    assert exp_init_path.exists(), "experiment_init.json was not created"

    # Read the file and verify its contents
    with exp_init_path.open() as f:
        actual_config = json.load(f)

    # Verify the configuration has the expected keys
    for key in expected_config_keys:
        assert key in actual_config, (
            f"Key '{key}' missing in experiment_init.json"
        )

    # Step 2: Edit experiment_init.json as specified in the docs
    # In getting-started.md, the user is instructed to edit experiment_init.json
    # to add the required channel values for their experiment.
    # This step simulates the manual editing of the file by a user.
    with exp_init_path.open() as f:
        exp_init_data = json.load(f)

    # Update with required channel values specifically mentioned in getting-started.md
    # These values represent standard channel configurations for Cell Painting and SBS images
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
    # Execute the actual CLI command:
    #   starrynight inventory gen -d ${DATADIR} -o ${WKDIR}/inventory
    inventory_cmd = [
        "starrynight",
        "inventory",
        "gen",
        "-d",
        str(data_dir),
        "-o",
        str(inventory_dir),
    ]

    # Run the command and check it was successful
    result = subprocess.run(
        inventory_cmd, capture_output=True, text=True, check=False
    )

    # Check if the command was successful
    assert result.returncode == 0, (
        f"Inventory generation command failed: {result.stderr}"
    )

    # Verify the inventory file was created
    inventory_file = inventory_dir / "inventory.parquet"
    assert inventory_file.exists(), "Inventory file was not created"

    # Verify the inventory/inv directory exists (for temporary processing files)
    inv_dir = inventory_dir / "inv"
    assert inv_dir.exists(), "Inventory 'inv' subdirectory was not created"

    # === Roadmap for Future Test Extensions ===
    # The following steps would complete the getting-started.md workflow:
    #
    # Step 4: Generate index
    # - Execute "starrynight index gen -i ${WKDIR}/inventory/inventory.parquet -o ${WKDIR}/index/"
    # - Verify index.parquet in the ${WKDIR}/index/ directory
    #
    # Step 5: Create experiment file
    # - Execute "starrynight exp new -i ${WKDIR}/index/index.parquet -e "Pooled CellPainting [Generic]"
    #   -c ${WKDIR}/experiment_init.json -o ${WKDIR}"
    # - Verify experiment.json creation
    #
    # Step 6: Generate LoadData files for illumination correction
    # - Execute "starrynight illum calc loaddata -i ${WKDIR}/index/index.parquet
    #   -o ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_calc --exp_config ${WKDIR}/experiment.json --use_legacy"
    # - Verify LoadData CSV files
    #
    # Step 7: Verify the final workflow state
    # - LoadData files exist and contain expected content
    # - All file paths are correctly configured
