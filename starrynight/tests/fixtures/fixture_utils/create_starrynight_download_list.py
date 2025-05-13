#!/usr/bin/env python3

# FIXME: Ensure that the folder created is workspace/analysis/Batch1 and not workspace/analysis/20...
import itertools
import os
import sys
from pathlib import Path

# Fixture configuration - change this for different fixture types (s1, s2, l1)
FIXTURE_ID = "s1"

# Configuration

# Get configuration from environment variables
BUCKET = os.environ.get("BUCKET")
PROJECT_S3 = os.environ.get("PROJECT")
BATCH_S3 = os.environ.get("BATCH")
DEST_BUCKET = os.environ.get("DEST_BUCKET")

# Check if all required environment variables are set
if not all([BUCKET, PROJECT_S3, BATCH_S3, DEST_BUCKET]):
    print("Error: Required environment variables not set.")
    print(
        "Please set BUCKET, PROJECT, BATCH, and DEST_BUCKET environment variables."
    )
    sys.exit(1)

PROJECT_LOCAL = "Source1"
BATCH_LOCAL = "Batch1"

# Define sample constants
WELLS = ["A1", "A2", "B1"]
SITES = [0, 1, 2, 3]
CYCLES = range(1, 4)  # SBS cycles (1, 2, 3)
PLATE = "Plate1"
PLATE_FOLDER_SUFFIX = "20240319_122800_179"

# Define offsets for each well
WELL_OFFSETS = {
    "A1": 0,  # A1 starts at 0000
    "A2": 1025,  # A2 starts at 1025 (offset + 1)
    "B1": 3075,  # B1 starts at 3075 (offset + 1)
}

# Paths
LOCAL_INPUT_DIR = f"./scratch/fix_{FIXTURE_ID}_input"
LOCAL_OUTPUT_DIR = f"./scratch/fix_{FIXTURE_ID}_pcpip_output"

LOCAL_PATH_IMAGES_INPUT = f"{LOCAL_INPUT_DIR}/{PROJECT_LOCAL}/{BATCH_LOCAL}"
LOCAL_PATH_IMAGES_OUTPUT = f"{LOCAL_OUTPUT_DIR}/{PROJECT_LOCAL}/{BATCH_LOCAL}"
LOCAL_PATH_WORKSPACE_INPUT = f"{LOCAL_INPUT_DIR}/{PROJECT_LOCAL}/workspace"
LOCAL_PATH_WORKSPACE_OUTPUT = f"{LOCAL_OUTPUT_DIR}/{PROJECT_LOCAL}/workspace"

S3_PATH_IMAGES = f"s3://{BUCKET}/projects/{PROJECT_S3}/{BATCH_S3}"
S3_PATH_WORKSPACE = f"s3://{BUCKET}/projects/{PROJECT_S3}/workspace"

# New S3 destination bucket
S3_DEST_BUCKET = f"s3://{DEST_BUCKET}"
S3_DEST_INPUT_DIR = (
    f"{S3_DEST_BUCKET}/projects/2024_03_12_starrynight/fix_{FIXTURE_ID}_input"
)
S3_DEST_OUTPUT_DIR = f"{S3_DEST_BUCKET}/projects/2024_03_12_starrynight/fix_{FIXTURE_ID}_pcpip_output"
S3_DEST_IMAGES_INPUT = f"{S3_DEST_INPUT_DIR}/{PROJECT_LOCAL}/{BATCH_LOCAL}"
S3_DEST_IMAGES_OUTPUT = f"{S3_DEST_OUTPUT_DIR}/{PROJECT_LOCAL}/{BATCH_LOCAL}"
S3_DEST_WORKSPACE_INPUT = f"{S3_DEST_INPUT_DIR}/{PROJECT_LOCAL}/workspace"
S3_DEST_WORKSPACE_OUTPUT = f"{S3_DEST_OUTPUT_DIR}/{PROJECT_LOCAL}/workspace"

DOWNLOAD_LIST = "./scratch/download_list.txt"
S3_COPY_LIST = "./scratch/s3_copy_list.txt"


# Create necessary directories
def create_directories():
    # Base directories
    Path(DOWNLOAD_LIST).parent.mkdir(parents=True, exist_ok=True)

    # SBS image directories
    for cycle in CYCLES:
        Path(
            f"{LOCAL_PATH_IMAGES_INPUT}/images/{PLATE}/20X_c{cycle}_SBS-{cycle}"
        ).mkdir(parents=True, exist_ok=True)

    # Cell Painting image directory
    Path(
        f"{LOCAL_PATH_IMAGES_INPUT}/images/{PLATE}/20X_CP_{PLATE}_{PLATE_FOLDER_SUFFIX}"
    ).mkdir(parents=True, exist_ok=True)

    # Illumination correction directory
    Path(f"{LOCAL_PATH_IMAGES_OUTPUT}/illum/{PLATE}").mkdir(
        parents=True, exist_ok=True
    )

    # Workspace directory
    Path(
        f"{LOCAL_PATH_WORKSPACE_OUTPUT}/load_data_csv/${BATCH_LOCAL}/{PLATE}"
    ).mkdir(parents=True, exist_ok=True)

    # Other directories will be created as needed when generating the file list


def get_paths(relative_path, is_input=True, is_image=True):
    """Generate local and S3 destination paths from a relative path.

    Args:
        relative_path (str): The relative path to append to base paths
        is_input (bool): Whether to use input or output base paths
        is_image (bool): Whether to use image or workspace base paths

    Returns:
        tuple: (local_dir, s3_dest_dir)

    """
    if is_image:
        local_base = (
            LOCAL_PATH_IMAGES_INPUT if is_input else LOCAL_PATH_IMAGES_OUTPUT
        )
        s3_base = S3_DEST_IMAGES_INPUT if is_input else S3_DEST_IMAGES_OUTPUT
    else:
        local_base = (
            LOCAL_PATH_WORKSPACE_INPUT
            if is_input
            else LOCAL_PATH_WORKSPACE_OUTPUT
        )
        s3_base = (
            S3_DEST_WORKSPACE_INPUT if is_input else S3_DEST_WORKSPACE_OUTPUT
        )

    local_dir = f"{local_base}/{relative_path}"
    s3_dest_dir = f"{s3_base}/{relative_path}"

    # Ensure local directory exists
    Path(local_dir).mkdir(parents=True, exist_ok=True)

    return local_dir, s3_dest_dir


def generate_download_list():
    # Initialize both files
    with (
        Path.open()(DOWNLOAD_LIST, "w") as download_file,
        Path.open()(S3_COPY_LIST, "w") as s3_copy_file,
    ):
        # SBS images
        for cycle in CYCLES:
            for well in WELLS:
                for site in SITES:
                    # Calculate sequence using offset + point value
                    seq_str = f"{WELL_OFFSETS[well] + site:04d}"
                    # Format point as 4-digit string
                    site_str = f"{site:04d}"
                    relative_path = f"images/{PLATE}/20X_c{cycle}_SBS-{cycle}/"
                    local_dir, s3_dest_dir = get_paths(
                        relative_path, is_input=True, is_image=True
                    )
                    s3_file = f"{S3_PATH_IMAGES}/{relative_path}Well{well}_Point{well}_{site_str}_ChannelC,A,T,G,DAPI_Seq{seq_str}.ome.tiff"
                    download_file.write(f"cp '{s3_file}' {local_dir}\n")
                    s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_dir}'\n")

        # Cell Painting images
        for well in WELLS:
            for site in SITES:
                # Calculate sequence using offset + point value
                seq_str = f"{WELL_OFFSETS[well] + site:04d}"
                # Format point as 4-digit string
                site_str = f"{site:04d}"
                relative_path = (
                    f"images/{PLATE}/20X_CP_{PLATE}_{PLATE_FOLDER_SUFFIX}/"
                )
                local_dir, s3_dest_dir = get_paths(
                    relative_path, is_input=True, is_image=True
                )
                s3_file = f"{S3_PATH_IMAGES}/{relative_path}Well{well}_Point{well}_{site_str}_ChannelPhalloAF750,ZO1-AF488,DAPI_Seq{seq_str}.ome.tiff"
                download_file.write(f"cp '{s3_file}' {local_dir}\n")
                s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_dir}'\n")

        # Illumination correction images
        for cycle, channel in itertools.product(
            CYCLES, ["DNA", "A", "T", "G", "C"]
        ):
            relative_path = f"illum/{PLATE}/"
            local_dir, s3_dest_dir = get_paths(
                relative_path, is_input=False, is_image=True
            )
            s3_file = f"{S3_PATH_IMAGES}/{relative_path}{PLATE}_Cycle{cycle}_Illum{channel}.npy"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_dir}'\n")

        for channel in ["DNA", "Phalloidin", "ZO1"]:
            relative_path = f"illum/{PLATE}/"
            local_dir, s3_dest_dir = get_paths(
                relative_path, is_input=False, is_image=True
            )
            s3_file = (
                f"{S3_PATH_IMAGES}/{relative_path}{PLATE}_Illum{channel}.npy"
            )
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_dir}'\n")

        # Cell Painting images: Illumination corrected
        for well, site, channel in itertools.product(
            WELLS, [0, 1], ["DNA", "Phalloidin", "ZO1"]
        ):
            relative_path = f"images_corrected/painting/{PLATE}-Well{well}/"
            local_dir, s3_dest_dir = get_paths(
                relative_path, is_input=False, is_image=True
            )
            s3_file = f"{S3_PATH_IMAGES}/{relative_path}Plate_{PLATE}_Well_Well{well}_Site_{site}_Corr{channel}.tiff"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_dir}'\n")

        for well, csvfile in itertools.product(
            WELLS,
            ["Cells", "ConfluentRegions", "Experiment", "Image", "Nuclei"],
        ):
            relative_path = f"images_corrected/painting/{PLATE}-Well{well}/"
            local_dir, s3_dest_dir = get_paths(
                relative_path, is_input=False, is_image=True
            )
            s3_file = f"{S3_PATH_IMAGES}/{relative_path}PaintingIllumApplication_{csvfile}.csv"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_dir}'\n")

        # SBS images: Illumination aligned
        for well, site, cycle, channel in itertools.product(
            WELLS, SITES, CYCLES, ["A", "T", "G", "C", "DAPI"]
        ):
            relative_path = (
                f"images_aligned/barcoding/{PLATE}-Well{well}-{site}/"
            )
            local_dir, s3_dest_dir = get_paths(
                relative_path, is_input=False, is_image=True
            )
            s3_file = f"{S3_PATH_IMAGES}/{relative_path}Plate_{PLATE}_Well_{well}_Site_{site}_Cycle0{cycle}_{channel}.tiff"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_dir}'\n")

        for well, site, csvfile in itertools.product(
            WELLS, SITES, ["Experiment", "Image"]
        ):
            relative_path = (
                f"images_aligned/barcoding/{PLATE}-Well{well}-{site}/"
            )
            local_dir, s3_dest_dir = get_paths(
                relative_path, is_input=False, is_image=True
            )
            s3_file = f"{S3_PATH_IMAGES}/{relative_path}BarcodingApplication_{csvfile}.csv"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_dir}'\n")

        # SBS images: Illumination corrected
        for well, site, cycle, channel in itertools.product(
            WELLS, SITES, CYCLES, ["A", "T", "G", "C"]
        ):
            relative_path = (
                f"images_corrected/barcoding/{PLATE}-Well{well}-{site}/"
            )
            local_dir, s3_dest_dir = get_paths(
                relative_path, is_input=False, is_image=True
            )
            s3_file = f"{S3_PATH_IMAGES}/{relative_path}Plate_{PLATE}_Well_{well}_Site_{site}_Cycle0{cycle}_{channel}.tiff"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_dir}'\n")

        # DAPI is present only in the first cycle
        for well, site in itertools.product(WELLS, SITES):
            relative_path = (
                f"images_corrected/barcoding/{PLATE}-Well{well}-{site}/"
            )
            local_dir, s3_dest_dir = get_paths(
                relative_path, is_input=False, is_image=True
            )
            s3_file = f"{S3_PATH_IMAGES}/{relative_path}Plate_{PLATE}_Well_{well}_Site_{site}_Cycle01_DAPI.tiff"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_dir}'\n")

        for well, site, csvfile in itertools.product(
            WELLS,
            SITES,
            ["BarcodeFoci", "PreFoci", "Experiment", "Image", "Nuclei"],
        ):
            relative_path = (
                f"images_corrected/barcoding/{PLATE}-Well{well}-{site}/"
            )
            local_dir, s3_dest_dir = get_paths(
                relative_path, is_input=False, is_image=True
            )
            s3_file = f"{S3_PATH_IMAGES}/{relative_path}BarcodePreprocessing_{csvfile}.csv"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_dir}'\n")

        # Segmentation images
        for well in WELLS:
            relative_path = f"images_segmentation/{PLATE}-Well{well}/"
            local_dir, s3_dest_dir = get_paths(
                relative_path, is_input=False, is_image=True
            )
            relative_path = f"images_segmentation/{PLATE}/"
            s3_file = f"{S3_PATH_IMAGES}/{relative_path}Plate_{PLATE}_Well_Well{well}_Site_0_CorrDNA_SegmentCheck.png"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_dir}'\n")

        for csvfile in [
            "Experiment",
            "Image",
            "Nuclei",
            "Cells",
            "PreCells",
            "ConfluentRegions",
        ]:
            relative_path = f"images_segmentation/{PLATE}-Well{well}/"
            local_dir, s3_dest_dir = get_paths(
                relative_path, is_input=False, is_image=True
            )
            relative_path = f"images_segmentation/{PLATE}/"
            s3_file = f"{S3_PATH_IMAGES}/{relative_path}SegmentationCheck_{csvfile}.csv"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_dir}'\n")

        # Analysis files
        # Define CSV and image files based on the YAML structure
        analysis_csv_files = [
            "BarcodeFoci.csv",
            "Cells.csv",
            "ConfluentRegions.csv",
            "Cytoplasm.csv",
            "Experiment.csv",
            "Foci.csv",
            "Foci_NonCellEdge.csv",
            "Foci_PreMask.csv",
            "Image.csv",
            "Nuclei.csv",
            "PreCells.csv",
            "RelateObjects.csv",
            "Resize_Foci.csv",
        ]

        # Add analysis files per well and site
        for well, site in itertools.product(WELLS, SITES):
            # Create the directory
            relative_path = f"analysis/{BATCH_S3}/{PLATE}-Well{well}-{site}/"
            local_dir, s3_dest_dir = get_paths(
                relative_path, is_input=False, is_image=False
            )

            # Add CSV files - get these from the analysisfix folder
            for csv_file in analysis_csv_files:
                s3_file = f"{S3_PATH_WORKSPACE}/analysisfix/{BATCH_S3}/{PLATE}-Well{well}-{site}/{csv_file}"
                download_file.write(f"cp '{s3_file}' {local_dir}\n")
                s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_dir}'\n")

            # Add segmentation mask TIFF files - get these from the analysis folder
            for object_type in ["Cells", "Cytoplasm", "Nuclei"]:
                relative_mask_path = f"{relative_path}segmentation_masks/"
                mask_dir, s3_dest_mask_dir = get_paths(
                    relative_mask_path, is_input=False, is_image=False
                )
                s3_file = f"{S3_PATH_WORKSPACE}/analysis/{BATCH_S3}/{PLATE}-Well{well}-{site}/segmentation_masks/Plate_{PLATE}_Well_Well{well}_Site_{site}_{object_type}_Objects.tiff"
                download_file.write(f"cp '{s3_file}' {mask_dir}\n")
                s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_mask_dir}'\n")

            # Add overlay PNG files - get these from the analysis folder
            for overlay_type in ["Overlay", "SpotOverlay"]:
                s3_file = f"{S3_PATH_WORKSPACE}/analysis/{BATCH_S3}/{PLATE}-Well{well}-{site}/Plate_{PLATE}_Well_Well{well}_Site_{site}_CorrDNA_{overlay_type}.png"
                download_file.write(f"cp '{s3_file}' {local_dir}\n")
                s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_dir}'\n")

        # Load Data CSV files
        load_data_csvs = [
            "load_data_pipeline1.csv",
            "load_data_pipeline2.csv",
            "load_data_pipeline3.csv",
            "load_data_pipeline5.csv",
            "load_data_pipeline6.csv",
            "load_data_pipeline7.csv",
            "load_data_pipeline9.csv",
        ]

        # Create load data directory
        relative_path = f"load_data_csv/{BATCH_LOCAL}/{PLATE}/"
        local_dir, s3_dest_dir = get_paths(
            relative_path, is_input=False, is_image=False
        )

        # Add load data CSV files
        for csv_file in load_data_csvs:
            s3_file = f"{S3_PATH_WORKSPACE}/load_data_csv/{BATCH_S3}/{PLATE}/{csv_file}"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_dir}'\n")

        # Metadata files
        # Create metadata directory
        relative_path = "metadata/"
        metadata_dir, s3_dest_metadata_dir = get_paths(
            relative_path, is_input=True, is_image=False
        )

        # Add Barcodes.csv file
        s3_file = f"{S3_PATH_WORKSPACE}/metadata/{BATCH_S3}/Barcodes.csv"
        download_file.write(f"cp '{s3_file}' {metadata_dir}\n")
        s3_copy_file.write(f"cp '{s3_file}' '{s3_dest_metadata_dir}'\n")

        # Add pipeline files
        relative_path = "pipelines/"
        # Pipeline directory structure and files
        pipeline_subfolders = {
            "1_CP_Illum": ["1_CP_Illum.cppipe", "1_Illum_Plate1_Plate2.cppipe"],
            "2_CP_Apply_Illum": [
                "2_CP_Apply_Illum.cppipe",
                "2_CP_Apply_Illum_Plate3_Plate4.cppipe",
            ],
            "3_CP_SegmentationCheck": [
                "3_CP_SegmentationCheck_Plate1_Plate2.cppipe",
                "3_CP_SegmentationCheck_Plate3_Plate4.cppipe",
            ],
            "5_BC_Illum": ["5_BC_Illum.cppipe", "5_BC_Illum_byWell.cppipe"],
            "6_BC_Apply_Illum": ["6_BC_Apply_Illum.cppipe"],
            "7_BC_Preprocess": [
                "7_BC_Preprocess.cppipe",
                "7_BC_Preprocess_2.cppipe",
                "7_BC_Preprocess_2strict.cppipe",
                "7_BC_Preprocess_3.cppipe",
                "7_BC_Preprocess_4.cppipe",
            ],
            "9_Analysis": [
                "9_Analysis.cppipe",
                "9_Analysis_Plate1_Plate2.cppipe",
                "9_Analysis_Rerun.cppipe",
                "9_Analysis_foci.cppipe",
            ],
        }

        # Create pipeline directory structure and download the files
        for subfolder, files in pipeline_subfolders.items():
            subfolder_path = f"{relative_path}{BATCH_LOCAL}/{subfolder}"
            subfolder_dir, s3_dest_subfolder_dir = get_paths(
                subfolder_path, is_input=True, is_image=False
            )

            for pipeline_file in files:
                # S3 path has all files in the base directory (not in subfolders)
                s3_file = (
                    f"{S3_PATH_WORKSPACE}/pipelines/{BATCH_S3}/{pipeline_file}"
                )
                download_file.write(f"cp '{s3_file}' {subfolder_dir}/\n")
                s3_copy_file.write(
                    f"cp '{s3_file}' '{s3_dest_subfolder_dir}/'\n"
                )


def main():
    print("Creating directories and generating download and S3 copy lists")
    create_directories()
    generate_download_list()
    print(f"Download list created at {DOWNLOAD_LIST}")
    print(f"S3-to-S3 copy list created at {S3_COPY_LIST}")
    print(
        "Review the files and run the download/copy commands to transfer the files."
    )


if __name__ == "__main__":
    main()
