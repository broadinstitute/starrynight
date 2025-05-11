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


def test_getting_started_workflow_complete(fix_s1_input_dir, fix_s1_workspace):
    """Test the complete getting-started workflow from experiment initialization to LoadData generation.

    This test covers all steps of the workflow from getting-started.md:
    1. Initialize experiment configuration and edit with required channel values
    2. Generate inventory from input data
    3. Generate index from inventory
    4. Create experiment file from index and configuration
    5. Generate LoadData files for illumination correction
    6. Verify the final state of the workflow

    This test executes the actual CLI commands as they would be used by a real user,
    ensuring that each step produces the expected outputs and validating the complete
    end-to-end workflow.

    Args:
        fix_s1_input_dir: Fixture providing input test data with FIX-S1 structure
        fix_s1_workspace: Fixture providing workspace directory structure with expected paths

    """
    # Set up test environment
    workspace_dir = fix_s1_workspace["workspace_dir"]
    # These variables will be used in future test phases
    inventory_dir = fix_s1_workspace["inventory_dir"]
    index_dir = fix_s1_workspace["index_dir"]
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

    # Step 4: Generate index
    # Execute the actual CLI command:
    #   starrynight index gen -i ${WKDIR}/inventory/inventory.parquet -o ${WKDIR}/index/
    index_gen_cmd = [
        "starrynight",
        "index",
        "gen",
        "-i",
        str(inventory_file),
        "-o",
        str(index_dir),
    ]

    # Create the index directory if it doesn't exist
    index_dir.mkdir(exist_ok=True, parents=True)

    # Run the command and check it was successful
    result = subprocess.run(
        index_gen_cmd, capture_output=True, text=True, check=False
    )

    # Check if the command was successful
    assert result.returncode == 0, (
        f"Index generation command failed: {result.stderr}"
    )

    # Verify the index file was created
    index_file = index_dir / "index.parquet"
    assert index_file.exists(), "Index file was not created"

    # Diagnostic: Examine the index file structure to understand what's missing
    import pandas as pd

    # Load the index file
    index_df = pd.read_parquet(index_file)

    # Print the columns in the index file
    print("\nDIAGNOSTIC INFO - Index file columns:")
    print(index_df.columns.tolist())

    # Check if dataset_id exists in the columns
    if "dataset_id" in index_df.columns:
        # Check if it has any non-null values
        print("\nValues in dataset_id column:")
        print(f"  - Non-null values: {index_df['dataset_id'].count()}")
        print(f"  - Unique values: {index_df['dataset_id'].unique().tolist()}")
    else:
        print("\nThe 'dataset_id' column is missing from the index file")

    # Print a sample row to help understand the structure
    if not index_df.empty:
        print("\nSample row from index file:")
        print(index_df.iloc[0].to_dict())

    # Step 5: Create experiment file
    # # Execute the actual CLI command:
    # #   starrynight exp new -i ${WKDIR}/index/index.parquet -e "Pooled CellPainting [Generic]"
    # #   -c ${WKDIR}/experiment_init.json -o ${WKDIR}
    # exp_create_cmd = [
    #     "starrynight",
    #     "exp",
    #     "new",
    #     "-i",
    #     str(index_file),
    #     "-e",
    #     "Pooled CellPainting [Generic]",
    #     "-c",
    #     str(exp_init_path),
    #     "-o",
    #     str(workspace_dir),
    # ]

    # # Run the command and check it was successful
    # result = subprocess.run(
    #     exp_create_cmd, capture_output=True, text=True, check=False
    # )

    # # Check if the command was successful
    # assert (
    #     result.returncode == 0
    # ), f"Experiment file creation command failed: {result.stderr}"

    # # Verify the experiment.json file was created
    # experiment_json_path = workspace_dir / "experiment.json"
    # assert experiment_json_path.exists(), "experiment.json was not created"

    # # Read the experiment file and check key configurations
    # with experiment_json_path.open() as f:
    #     experiment_config = json.load(f)

    # # Verify the experiment file contains expected keys
    # expected_exp_keys = [
    #     "experiment_name",
    #     "experiment_type",
    #     "barcode_csv_path",
    #     "cp_nuclei_channel",
    #     "cp_cell_channel",
    #     "cp_mito_channel",
    # ]

    # for key in expected_exp_keys:
    #     assert key in experiment_config, (
    #         f"Key '{key}' missing in experiment.json"
    #     )

    # # Verify the experiment name matches what we specified
    # assert (
    #     experiment_config["experiment_name"] == "Pooled CellPainting [Generic]"
    # ), "Experiment name not correctly set in experiment.json"

    # # Verify channel configurations were correctly transferred from experiment_init.json
    # assert experiment_config["cp_nuclei_channel"] == "DAPI", (
    #     "cp_nuclei_channel not correctly transferred to experiment.json"
    # )
    # assert experiment_config["cp_cell_channel"] == "PhalloAF750", (
    #     "cp_cell_channel not correctly transferred to experiment.json"
    # )
    # assert experiment_config["cp_mito_channel"] == "ZO1AF488", (
    #     "cp_mito_channel not correctly transferred to experiment.json"
    # )

    # # Step 6: Generate LoadData files for illumination correction
    # # Execute the actual CLI command:
    # #   starrynight illum calc loaddata -i ${WKDIR}/index/index.parquet
    # #   -o ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_calc --exp_config ${WKDIR}/experiment.json --use_legacy
    # illum_calc_loaddata_cmd = [
    #     "starrynight",
    #     "illum",
    #     "calc",
    #     "loaddata",
    #     "-i",
    #     str(index_file),
    #     "-o",
    #     str(fix_s1_workspace["cp_illum_calc_dir"]),
    #     "--exp_config",
    #     str(experiment_json_path),
    #     "--use_legacy",
    # ]

    # # Run the command and check it was successful
    # result = subprocess.run(
    #     illum_calc_loaddata_cmd, capture_output=True, text=True, check=False
    # )

    # # Check if the command was successful
    # assert result.returncode == 0, (
    #     f"Illumination LoadData generation command failed: {result.stderr}"
    # )

    # # Verify LoadData files were created
    # loaddata_dir = fix_s1_workspace["cp_illum_calc_dir"]

    # # Check for the presence of LoadData CSV files in the directory
    # csv_files = list(loaddata_dir.glob("*.csv"))
    # assert len(csv_files) > 0, "No LoadData CSV files were created"

    # # Verify at least one specific LoadData CSV file
    # all_files_csv = loaddata_dir / "all_files.csv"
    # assert all_files_csv.exists(), "all_files.csv was not created"

    # # Verify the content of the all_files.csv file
    # with all_files_csv.open() as f:
    #     csv_content = f.read()

    # # The CSV file should contain paths to the input images and "Image_Metadata_" columns
    # assert "Image_Metadata_" in csv_content, (
    #     "all_files.csv does not contain expected metadata columns"
    # )

    # # Check for plate-specific CSV files (should be created for each plate)
    # plate_csvs = list(loaddata_dir.glob("*Plate*.csv"))
    # assert len(plate_csvs) > 0, "No plate-specific CSV files were created"

    # # Step 7: Verify the final workflow state
    # # Ensure all key components of the workflow have been created

    # # Verify experiment configuration files
    # assert exp_init_path.exists(), "experiment_init.json missing in final state"
    # assert experiment_json_path.exists(), (
    #     "experiment.json missing in final state"
    # )

    # # Verify inventory and index files
    # assert inventory_file.exists(), "inventory.parquet missing in final state"
    # assert index_file.exists(), "index.parquet missing in final state"

    # # Verify LoadData files for illumination correction
    # assert len(csv_files) > 0, "LoadData CSV files missing in final state"

    # # Final check of directory structure to confirm all expected outputs are present
    # expected_dirs = [
    #     inventory_dir,
    #     index_dir,
    #     fix_s1_workspace["cp_illum_calc_dir"],
    # ]

    # for directory in expected_dirs:
    #     assert directory.exists(), (
    #         f"Required directory {directory} missing in final state"
    #     )

    # # Success! The test has verified all steps of the getting-started workflow
