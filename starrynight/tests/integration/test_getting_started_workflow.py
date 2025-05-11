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
import re
import subprocess
from pathlib import Path

import duckdb
import pandas as pd
import pytest


def test_getting_started_workflow_complete(  # noqa: C901
    fix_s1_input_dir, fix_s1_workspace, fix_s1_output_dir
):
    """Test the complete getting-started workflow from experiment initialization to LoadData generation.

    This test covers all steps of the workflow from getting-started.md:
    1. Initialize experiment configuration and edit with required channel values
    2. Generate inventory from input data
    3. Generate index from inventory
    4. Create experiment file from index and configuration
    5. Generate LoadData files for illumination correction
    6. Verify the final state of the workflow
    7. Validate the generated LoadData CSV matches the reference LoadData CSV

    This test executes the actual CLI commands as they would be used by a real user,
    ensuring that each step produces the expected outputs and validating the complete
    end-to-end workflow.

    Args:
        fix_s1_input_dir: Fixture providing input test data with FIX-S1 structure
        fix_s1_workspace: Fixture providing workspace directory structure with expected paths
        fix_s1_output_dir: Fixture providing reference output data for validation

    """
    # Set up test environment
    workspace_dir = fix_s1_workspace["workspace_dir"]
    # These variables will be used in future test phases
    inventory_dir = fix_s1_workspace["inventory_dir"]
    index_dir = fix_s1_workspace["index_dir"]
    input_dir = fix_s1_input_dir["input_dir"]

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
        str(input_dir),
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

    # Step 5: Create experiment file
    # Execute the actual CLI command:
    #   starrynight exp new -i ${WKDIR}/index/index.parquet -e "Pooled CellPainting [Generic]"
    #   -c ${WKDIR}/experiment_init.json -o ${WKDIR}
    exp_create_cmd = [
        "starrynight",
        "exp",
        "new",
        "-i",
        str(index_file),
        "-e",
        "Pooled CellPainting [Generic]",
        "-c",
        str(exp_init_path),
        "-o",
        str(workspace_dir),
    ]

    # Run the command and check it was successful
    result = subprocess.run(
        exp_create_cmd, capture_output=True, text=True, check=False
    )

    # Check if the command was successful
    assert result.returncode == 0, (
        f"Experiment file creation command failed: {result.stderr}"
    )

    # Verify the experiment.json file was created
    experiment_json_path = workspace_dir / "experiment.json"
    assert experiment_json_path.exists(), "experiment.json was not created"

    # Read the experiment file and check key configurations
    with experiment_json_path.open() as f:
        experiment_config = json.load(f)

    # Verify the experiment file contains expected keys (list a subset of keys)
    expected_exp_keys = [
        "dataset_id",
        "index_path",
        "inventory_path",
        "sbs_config",
        "cp_config",
        "use_legacy",
    ]

    for key in expected_exp_keys:
        assert key in experiment_config, (
            f"Key '{key}' missing in experiment.json"
        )

    # Verify channel configurations were correctly transferred from experiment_init.json
    assert experiment_config["cp_config"]["nuclei_channel"] == "DAPI", (
        "nuclei_channel not correctly set in cp_config"
    )
    assert experiment_config["cp_config"]["cell_channel"] == "PhalloAF750", (
        "cell_channel not correctly set in cp_config"
    )
    assert experiment_config["cp_config"]["mito_channel"] == "ZO1AF488", (
        "mito_channel not correctly set in cp_config"
    )

    # Step 6: Generate LoadData files for illumination correction
    # Execute the actual CLI command:
    #   starrynight illum calc loaddata -i ${WKDIR}/index/index.parquet
    #   -o ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_calc --exp_config ${WKDIR}/experiment.json --use_legacy
    illum_calc_loaddata_cmd = [
        "starrynight",
        "illum",
        "calc",
        "loaddata",
        "-i",
        str(index_file),
        "-o",
        str(fix_s1_workspace["cp_illum_calc_dir"]),
        "--exp_config",
        str(experiment_json_path),
        "--use_legacy",
    ]

    # Run the command and check it was successful
    result = subprocess.run(
        illum_calc_loaddata_cmd, capture_output=True, text=True, check=False
    )

    # Check if the command was successful
    assert result.returncode == 0, (
        f"Illumination LoadData generation command failed: {result.stderr}"
    )

    # Verify LoadData files were created
    loaddata_dir = fix_s1_workspace["cp_illum_calc_dir"]

    # Check for the presence of at least one LoadData CSV file in the directory
    csv_files = list(loaddata_dir.glob("*.csv"))
    assert len(csv_files) > 0, "No LoadData CSV files were created"

    # Check for plate-specific CSV files (should be created for each plate)
    plate_csvs = list(loaddata_dir.glob("*Plate*_illum_calc.csv"))
    assert len(plate_csvs) > 0, "No plate-specific CSV files were created"

    # Verify the content of a plate-specific CSV file
    plate_csv = plate_csvs[0]
    df = pd.read_csv(plate_csv)

    # The CSV file should contain required metadata columns
    required_columns = [
        "Metadata_Batch",
        "Metadata_Plate",
        "Metadata_Well",
        "Metadata_Site",
        "FileName_OrigPhalloidin",
        "FileName_OrigZO1",
        "FileName_OrigDNA",
        "PathName_OrigPhalloidin",
        "PathName_OrigZO1",
        "PathName_OrigDNA",
    ]
    for col in required_columns:
        assert col in df.columns, f"Required column '{col}' missing in CSV"

    # Step 7: Verify the final workflow state
    # Ensure all key components of the workflow have been created

    # Verify experiment configuration files
    assert exp_init_path.exists(), "experiment_init.json missing in final state"
    assert experiment_json_path.exists(), (
        "experiment.json missing in final state"
    )

    # Verify inventory and index files
    assert inventory_file.exists(), "inventory.parquet missing in final state"
    assert index_file.exists(), "index.parquet missing in final state"

    # Verify LoadData files for illumination correction
    assert len(csv_files) > 0, "LoadData CSV files missing in final state"
    assert len(plate_csvs) > 0, (
        "Plate-specific LoadData CSV files missing in final state"
    )

    # Final check of directory structure to confirm all expected outputs are present
    expected_dirs = [
        inventory_dir,
        index_dir,
        fix_s1_workspace["cp_illum_calc_dir"],
    ]

    for directory in expected_dirs:
        assert directory.exists(), (
            f"Required directory {directory} missing in final state"
        )

    # Success! The test has verified all steps of the getting-started workflow

    # Step 8: Validate the generated LoadData CSV against reference LoadData CSV
    # Define paths to the generated and reference CSV files
    generated_csv_path = plate_csvs[0]  # Use the first plate-specific CSV

    # Find the matching reference CSV in the fix_s1_output_dir
    ref_load_data_dir = fix_s1_output_dir["load_data_csv_dir"]
    ref_csv_path = list(
        ref_load_data_dir.glob("**/Plate1_trimmed/load_data_pipeline1.csv")
    )[0]

    # Load both CSV files with DuckDB using context manager for simplified validation
    # Collect all validation errors instead of stopping at first failure
    validation_errors = []

    try:
        # Use context manager for proper resource handling
        with duckdb.connect(":memory:") as conn:
            # Register CSV files as views using read_csv_auto for automatic type inference
            conn.execute(
                f"CREATE VIEW generated AS SELECT * FROM read_csv_auto('{str(generated_csv_path)}')"
            )
            conn.execute(
                f"CREATE VIEW reference AS SELECT * FROM read_csv_auto('{str(ref_csv_path)}')"
            )

            # 1. Verify channel frame assignments match between the CSVs
            ref_channels = conn.execute("""
                SELECT DISTINCT Frame_OrigDNA, Frame_OrigZO1, Frame_OrigPhalloidin
                FROM reference
                ORDER BY Frame_OrigDNA, Frame_OrigZO1, Frame_OrigPhalloidin
            """).fetchall()

            gen_channels = conn.execute("""
                SELECT DISTINCT Frame_OrigDNA, Frame_OrigZO1, Frame_OrigPhalloidin
                FROM generated
                ORDER BY Frame_OrigDNA, Frame_OrigZO1, Frame_OrigPhalloidin
            """).fetchall()

            if ref_channels != gen_channels:
                validation_errors.append(
                    f"Channel frame assignments don't match: Reference={ref_channels}, Generated={gen_channels}"
                )

            # 2. Verify all wells from reference exist in generated file
            ref_wells_rows = conn.execute(
                "SELECT DISTINCT Metadata_Well FROM reference"
            ).fetchall()
            gen_wells_rows = conn.execute(
                "SELECT DISTINCT Metadata_Well FROM generated"
            ).fetchall()

            # Convert to sets of values (extracting first column from each row)
            ref_wells = {row[0] for row in ref_wells_rows}
            gen_wells = {row[0] for row in gen_wells_rows}

            missing_wells = ref_wells - gen_wells
            if missing_wells:
                validation_errors.append(
                    f"Reference wells {missing_wells} not found in generated CSV. "
                    f"Reference values: {sorted(ref_wells)}, "
                    f"Generated values: {sorted(gen_wells)}"
                )

            # 2b. Verify all sites from reference exist in generated file
            ref_sites_rows = conn.execute(
                "SELECT DISTINCT Metadata_Site FROM reference"
            ).fetchall()
            gen_sites_rows = conn.execute(
                "SELECT DISTINCT Metadata_Site FROM generated"
            ).fetchall()

            # Convert to sets of values (extracting first column from each row)
            ref_sites = {row[0] for row in ref_sites_rows}
            gen_sites = {row[0] for row in gen_sites_rows}

            missing_sites = ref_sites - gen_sites
            if missing_sites:
                validation_errors.append(
                    f"Reference sites {missing_sites} not found in generated CSV. "
                    f"Reference values: {sorted(list(ref_sites))}, "
                    f"Generated values: {sorted(list(gen_sites))}"
                )

            # 3. Verify plate information matches
            ref_plates_rows = conn.execute(
                "SELECT DISTINCT Metadata_Plate FROM reference"
            ).fetchall()
            gen_plates_rows = conn.execute(
                "SELECT DISTINCT Metadata_Plate FROM generated"
            ).fetchall()

            # Convert to sets of values
            ref_plates = {row[0] for row in ref_plates_rows}
            gen_plates = {row[0] for row in gen_plates_rows}

            missing_plates = ref_plates - gen_plates
            if missing_plates:
                validation_errors.append(
                    f"Reference plates {missing_plates} not found in generated CSV. "
                    f"Reference values: {sorted(list(ref_plates))}, "
                    f"Generated values: {sorted(list(gen_plates))}"
                )

            # 4. Verify filename patterns
            filename_pattern_check = conn.execute("""
                SELECT COUNT(*) FROM generated
                WHERE FileName_OrigDNA NOT LIKE '%Channel%'
                OR FileName_OrigZO1 NOT LIKE '%Channel%'
                OR FileName_OrigPhalloidin NOT LIKE '%Channel%'
            """).fetchone()[0]

            if filename_pattern_check > 0:
                validation_errors.append(
                    f"Found {filename_pattern_check} filenames that don't match the expected pattern"
                )

            # After collecting all errors, report them if any exist
            if validation_errors:
                error_message = "\n".join(
                    [
                        f"Validation error {i + 1}: {error}"
                        for i, error in enumerate(validation_errors)
                    ]
                )
                pytest.fail(
                    f"CSV validation failed with {len(validation_errors)} error(s):\n{error_message}"
                )

    except duckdb.Error as e:
        pytest.fail(f"DuckDB error during CSV validation: {str(e)}")
