#!/usr/bin/env python3

import itertools
from pathlib import Path

# Configuration
import os
import sys

# Get configuration from environment variables
BUCKET = os.environ.get("BUCKET")
PROJECT_S3 = os.environ.get("PROJECT")
BATCH_S3 = os.environ.get("BATCH")

# Check if all required environment variables are set
if not all([BUCKET, PROJECT_S3, BATCH_S3]):
    print("Error: Required environment variables not set.")
    print("Please set BUCKET, PROJECT, and BATCH environment variables.")
    sys.exit(1)

PROJECT_LOCAL = "Source1"
BATCH_LOCAL = "Batch1"

# Paths
LOCAL_INPUT_DIR = "./scratch/starrynight_example_input"
LOCAL_OUTPUT_DIR = "./scratch/starrynight_example_output_baseline"

LOCAL_PATH_IMAGES_INPUT = f"{LOCAL_INPUT_DIR}/{PROJECT_LOCAL}/{BATCH_LOCAL}"
LOCAL_PATH_IMAGES_OUTPUT = f"{LOCAL_OUTPUT_DIR}/{PROJECT_LOCAL}/{BATCH_LOCAL}"
LOCAL_PATH_WORKSPACE_INPUT = f"{LOCAL_INPUT_DIR}/{PROJECT_LOCAL}/workspace"
LOCAL_PATH_WORKSPACE_OUTPUT = f"{LOCAL_OUTPUT_DIR}/{PROJECT_LOCAL}/workspace"

S3_PATH_IMAGES = f"s3://{BUCKET}/projects/{PROJECT_S3}/{BATCH_S3}"
S3_PATH_WORKSPACE = f"s3://{BUCKET}/projects/{PROJECT_S3}/workspace"

# New S3 destination bucket
S3_DEST_BUCKET = "s3://projects/2024_03_12_starrynight"
S3_DEST_INPUT_DIR = f"{S3_DEST_BUCKET}/starrynight_example_input"
S3_DEST_OUTPUT_DIR = f"{S3_DEST_BUCKET}/starrynight_example_output_baseline"
S3_DEST_IMAGES_INPUT = f"{S3_DEST_INPUT_DIR}/{PROJECT_LOCAL}/{BATCH_LOCAL}"
S3_DEST_IMAGES_OUTPUT = f"{S3_DEST_OUTPUT_DIR}/{PROJECT_LOCAL}/{BATCH_LOCAL}"
S3_DEST_WORKSPACE_INPUT = f"{S3_DEST_INPUT_DIR}/{PROJECT_LOCAL}/workspace"
S3_DEST_WORKSPACE_OUTPUT = f"{S3_DEST_OUTPUT_DIR}/{PROJECT_LOCAL}/workspace"

DOWNLOAD_LIST = "./scratch/download_list.txt"
S3_COPY_LIST = "./scratch/s3_copy_list.txt"

wells = ["A1", "A2", "B1"]
sites = [0, 1, 2, 3]

# Define offsets for each well
well_offsets = {
    "A1": 0,  # A1 starts at 0000
    "A2": 1025,  # A2 starts at 1025 (offset + 1)
    "B1": 3075,  # B1 starts at 3075 (offset + 1)
}


# Create necessary directories
def create_directories():
    # Base directories
    Path(DOWNLOAD_LIST).parent.mkdir(parents=True, exist_ok=True)

    # SBS image directories
    for cycle in range(1, 4):
        Path(f"{LOCAL_PATH_IMAGES_INPUT}/images/Plate1/20X_c{cycle}_SBS-{cycle}").mkdir(
            parents=True, exist_ok=True
        )

    # Cell Painting image directory
    Path(
        f"{LOCAL_PATH_IMAGES_INPUT}/images/Plate1/20X_CP_Plate1_20240319_122800_179"
    ).mkdir(parents=True, exist_ok=True)

    # Illumination correction directory
    Path(f"{LOCAL_PATH_IMAGES_OUTPUT}/illum/Plate1").mkdir(parents=True, exist_ok=True)

    # Workspace directory
    Path(f"{LOCAL_PATH_WORKSPACE_OUTPUT}/load_data_csv/${BATCH_LOCAL}/Plate1").mkdir(
        parents=True, exist_ok=True
    )

    # Other directories will be created as needed when generating the file list


def generate_download_list():
    # Initialize both files
    with (
        open(DOWNLOAD_LIST, "w") as download_file,
        open(S3_COPY_LIST, "w") as s3_copy_file,
    ):
        # SBS images
        for cycle in range(1, 4):
            for well in wells:
                for site in sites:
                    # Calculate sequence using offset + point value
                    seq_str = f"{well_offsets[well] + site:04d}"
                    # Format point as 4-digit string
                    site_str = f"{site:04d}"
                    s3_file = f"{S3_PATH_IMAGES}/images/Plate1/20X_c{cycle}_SBS-{cycle}/Well{well}_Point{well}_{site_str}_ChannelC,A,T,G,DAPI_Seq{seq_str}.ome.tiff"
                    local_dir = f"{LOCAL_PATH_IMAGES_INPUT}/images/Plate1/20X_c{cycle}_SBS-{cycle}/"
                    s3_dest_dir = f"{S3_DEST_IMAGES_INPUT}/images/Plate1/20X_c{cycle}_SBS-{cycle}/"
                    download_file.write(f"cp '{s3_file}' {local_dir}\n")
                    s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_dir}'\n")

        # Cell Painting images
        for well in wells:
            for site in sites:
                # Calculate sequence using offset + point value
                seq_str = f"{well_offsets[well] + site:04d}"
                # Format point as 4-digit string
                site_str = f"{site:04d}"
                s3_file = f"{S3_PATH_IMAGES}/images/Plate1/20X_CP_Plate1_20240319_122800_179/Well{well}_Point{well}_{site_str}_ChannelPhalloAF750,ZO1-AF488,DAPI_Seq{seq_str}.ome.tiff"
                local_dir = f"{LOCAL_PATH_IMAGES_INPUT}/images/Plate1/20X_CP_Plate1_20240319_122800_179/"
                s3_dest_dir = f"{S3_DEST_IMAGES_INPUT}/images/Plate1/20X_CP_Plate1_20240319_122800_179/"
                download_file.write(f"cp '{s3_file}' {local_dir}\n")
                s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_dir}'\n")

        # Illumination correction images
        for cycle, channel in itertools.product(
            range(1, 4), ["DNA", "A", "T", "G", "C"]
        ):
            s3_file = (
                f"{S3_PATH_IMAGES}/illum/Plate1/Plate1_Cycle{cycle}_Illum{channel}.npy"
            )
            local_dir = f"{LOCAL_PATH_IMAGES_OUTPUT}/illum/Plate1/"
            s3_dest_dir = f"{S3_DEST_IMAGES_OUTPUT}/illum/Plate1/"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_dir}'\n")

        for channel in ["DNA", "Phalloidin", "ZO1"]:
            s3_file = f"{S3_PATH_IMAGES}/illum/Plate1/Plate1_Illum{channel}.npy"
            local_dir = f"{LOCAL_PATH_IMAGES_OUTPUT}/illum/Plate1/"
            s3_dest_dir = f"{S3_DEST_IMAGES_OUTPUT}/illum/Plate1/"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_dir}'\n")

        # Cell Painting images: Illumination corrected
        for well, site, channel in itertools.product(
            wells, [0, 1], ["DNA", "Phalloidin", "ZO1"]
        ):
            local_dir = f"{LOCAL_PATH_IMAGES_OUTPUT}/images_corrected/painting/Plate1-Well{well}/"
            s3_dest_dir = (
                f"{S3_DEST_IMAGES_OUTPUT}/images_corrected/painting/Plate1-Well{well}/"
            )
            Path(local_dir).mkdir(parents=True, exist_ok=True)
            s3_file = f"{S3_PATH_IMAGES}/images_corrected/painting/Plate1-Well{well}/Plate_Plate1_Well_Well{well}_Site_{site}_Corr{channel}.tiff"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_dir}'\n")

        for well, csvfile in itertools.product(
            wells, ["Cells", "ConfluentRegions", "Experiment", "Image", "Nuclei"]
        ):
            s3_file = f"{S3_PATH_IMAGES}/images_corrected/painting/Plate1-Well{well}/PaintingIllumApplication_{csvfile}.csv"
            local_dir = f"{LOCAL_PATH_IMAGES_OUTPUT}/images_corrected/painting/Plate1-Well{well}/"
            s3_dest_dir = (
                f"{S3_DEST_IMAGES_OUTPUT}/images_corrected/painting/Plate1-Well{well}/"
            )
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_dir}'\n")

        # SBS images: Illumination aligned
        for well, site, cycle, channel in itertools.product(
            wells, sites, range(1, 4), ["A", "T", "G", "C", "DAPI"]
        ):
            local_dir = f"{LOCAL_PATH_IMAGES_OUTPUT}/images_aligned/barcoding/Plate1-Well{well}-{site}/"
            s3_dest_dir = f"{S3_DEST_IMAGES_OUTPUT}/images_aligned/barcoding/Plate1-Well{well}-{site}/"
            Path(local_dir).mkdir(parents=True, exist_ok=True)
            s3_file = f"{S3_PATH_IMAGES}/images_aligned/barcoding/Plate1-Well{well}-{site}/Plate_Plate1_Well_{well}_Site_{site}_Cycle0{cycle}_{channel}.tiff"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_dir}'\n")

        for well, site, csvfile in itertools.product(
            wells, sites, ["Experiment", "Image"]
        ):
            local_dir = f"{LOCAL_PATH_IMAGES_OUTPUT}/images_aligned/barcoding/Plate1-Well{well}-{site}/"
            s3_dest_dir = f"{S3_DEST_IMAGES_OUTPUT}/images_aligned/barcoding/Plate1-Well{well}-{site}/"
            s3_file = f"{S3_PATH_IMAGES}/images_aligned/barcoding/Plate1-Well{well}-{site}/BarcodingApplication_{csvfile}.csv"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_dir}'\n")

        # SBS images: Illumination corrected
        for well, site, cycle, channel in itertools.product(
            wells, sites, range(1, 4), ["A", "T", "G", "C"]
        ):
            local_dir = f"{LOCAL_PATH_IMAGES_OUTPUT}/images_corrected/barcoding/Plate1-Well{well}-{site}/"
            s3_dest_dir = f"{S3_DEST_IMAGES_OUTPUT}/images_corrected/barcoding/Plate1-Well{well}-{site}/"
            Path(local_dir).mkdir(parents=True, exist_ok=True)
            s3_file = f"{S3_PATH_IMAGES}/images_corrected/barcoding/Plate1-Well{well}-{site}/Plate_Plate1_Well_{well}_Site_{site}_Cycle0{cycle}_{channel}.tiff"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_dir}'\n")

        # DAPI is present only in the first cycle
        for well, site in itertools.product(wells, sites):
            local_dir = f"{LOCAL_PATH_IMAGES_OUTPUT}/images_corrected/barcoding/Plate1-Well{well}-{site}/"
            s3_dest_dir = f"{S3_DEST_IMAGES_OUTPUT}/images_corrected/barcoding/Plate1-Well{well}-{site}/"
            Path(local_dir).mkdir(parents=True, exist_ok=True)
            s3_file = f"{S3_PATH_IMAGES}/images_corrected/barcoding/Plate1-Well{well}-{site}/Plate_Plate1_Well_{well}_Site_{site}_Cycle01_DAPI.tiff"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_dir}'\n")

        for well, site, csvfile in itertools.product(
            wells, sites, ["BarcodeFoci", "PreFoci", "Experiment", "Image", "Nuclei"]
        ):
            local_dir = f"{LOCAL_PATH_IMAGES_OUTPUT}/images_corrected/barcoding/Plate1-Well{well}-{site}/"
            s3_dest_dir = f"{S3_DEST_IMAGES_OUTPUT}/images_corrected/barcoding/Plate1-Well{well}-{site}/"
            s3_file = f"{S3_PATH_IMAGES}/images_corrected/barcoding/Plate1-Well{well}-{site}/BarcodePreprocessing_{csvfile}.csv"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_dir}'\n")

        # Segmentation images
        for well in wells:
            local_dir = f"{LOCAL_PATH_IMAGES_OUTPUT}/images_segmentation/Plate1/"
            s3_dest_dir = f"{S3_DEST_IMAGES_OUTPUT}/images_segmentation/Plate1/"
            Path(local_dir).mkdir(parents=True, exist_ok=True)
            s3_file = f"{S3_PATH_IMAGES}/images_segmentation/Plate1/Plate_Plate1_Well_Well{well}_Site_0_CorrDNA_SegmentCheck.png"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_dir}'\n")

        for csvfile in [
            "Experiment",
            "Image",
            "Nuclei",
            "Cells",
            "PreCells",
            "ConfluentRegions",
        ]:
            local_dir = f"{LOCAL_PATH_IMAGES_OUTPUT}/images_segmentation/Plate1/"
            s3_dest_dir = f"{S3_DEST_IMAGES_OUTPUT}/images_segmentation/Plate1/"
            s3_file = f"{S3_PATH_IMAGES}/images_segmentation/Plate1/SegmentationCheck_{csvfile}.csv"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_dir}'\n")

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
        for well, site in itertools.product(wells, sites):
            # Create the directory
            local_dir = f"{LOCAL_PATH_WORKSPACE_OUTPUT}/analysis/{BATCH_S3}/Plate1-Well{well}-{site}/"
            s3_dest_dir = f"{S3_DEST_WORKSPACE_OUTPUT}/analysis/{BATCH_S3}/Plate1-Well{well}-{site}/"
            Path(local_dir).mkdir(parents=True, exist_ok=True)

            # Add CSV files - get these from the analysisfix folder
            for csv_file in analysis_csv_files:
                s3_file = f"{S3_PATH_WORKSPACE}/analysisfix/{BATCH_S3}/Plate1-Well{well}-{site}/{csv_file}"
                download_file.write(f"cp '{s3_file}' {local_dir}\n")
                s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_dir}'\n")

            # Add segmentation mask TIFF files - get these from the analysis folder
            for object_type in ["Cells", "Cytoplasm", "Nuclei"]:
                mask_dir = f"{local_dir}segmentation_masks/"
                s3_dest_mask_dir = f"{s3_dest_dir}segmentation_masks/"
                Path(mask_dir).mkdir(parents=True, exist_ok=True)
                s3_file = f"{S3_PATH_WORKSPACE}/analysis/{BATCH_S3}/Plate1-Well{well}-{site}/segmentation_masks/Plate_Plate1_Well_Well{well}_Site_{site}_{object_type}_Objects.tiff"
                download_file.write(f"cp '{s3_file}' {mask_dir}\n")
                s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_mask_dir}'\n")

            # Add overlay PNG files - get these from the analysis folder
            for overlay_type in ["Overlay", "SpotOverlay"]:
                s3_file = f"{S3_PATH_WORKSPACE}/analysis/{BATCH_S3}/Plate1-Well{well}-{site}/Plate_Plate1_Well_Well{well}_Site_{site}_CorrDNA_{overlay_type}.png"
                download_file.write(f"cp '{s3_file}' {local_dir}\n")
                s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_dir}'\n")

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
        local_dir = f"{LOCAL_PATH_WORKSPACE_OUTPUT}/load_data_csv/{BATCH_LOCAL}/Plate1/"
        s3_dest_dir = f"{S3_DEST_WORKSPACE_OUTPUT}/load_data_csv/{BATCH_LOCAL}/Plate1/"
        Path(local_dir).mkdir(parents=True, exist_ok=True)

        # Add load data CSV files
        for csv_file in load_data_csvs:
            s3_file = f"{S3_PATH_WORKSPACE}/load_data_csv/{BATCH_S3}/Plate1/{csv_file}"
            download_file.write(f"cp '{s3_file}' {local_dir}\n")
            s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_dir}'\n")

        # Metadata files
        # Create metadata directory
        metadata_dir = f"{LOCAL_PATH_WORKSPACE_INPUT}/metadata/"
        s3_dest_metadata_dir = f"{S3_DEST_WORKSPACE_INPUT}/metadata/"
        Path(metadata_dir).mkdir(parents=True, exist_ok=True)

        # Add Barcodes.csv file
        s3_file = f"{S3_PATH_WORKSPACE}/metadata/{BATCH_S3}/Barcodes.csv"
        download_file.write(f"cp '{s3_file}' {metadata_dir}\n")
        s3_copy_file.write(f"aws s3 cp '{s3_file}' '{s3_dest_metadata_dir}'\n")


def main():
    print("Creating directories and generating download and S3 copy lists")
    create_directories()
    generate_download_list()
    print(f"Download list created at {DOWNLOAD_LIST}")
    print(f"S3-to-S3 copy list created at {S3_COPY_LIST}")
    print("Review the files and run the download/copy commands to transfer the files.")


if __name__ == "__main__":
    main()
