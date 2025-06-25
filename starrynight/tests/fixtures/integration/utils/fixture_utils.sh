#!/bin/bash

# Fixture Utils
#
# Utility scripts for creating, manipulating, and validating test fixtures.
#
# Purpose
#
# These utilities help manage the test fixture requirements by:
#
# 1. Creating test fixture datasets from larger production data
# 2. Validating data integrity of LoadData CSV files and referenced file paths
# 3. Optimizing disk usage through compression techniques for large image files
#
# Components
#
# - create_starrynight_download_list.py: Creates download and S3 copy lists for test fixtures
# - loaddata_filter.py: Filters CellProfiler LoadData CSV files to create smaller datasets
# - loaddata_validate.py: Validates paths in LoadData CSVs and checks if referenced files exist
# - loaddata_postprocess.py: Updates paths, headers, and identifiers in LoadData CSV files
#
# Prerequisites:
# - s5cmd: Download management tool - https://github.com/peak/s5cmd
# - ImageMagick: Required for image compression (commands: magick, identify)
# - GNU Parallel: Required for parallel processing
# - UV: Python package management and script execution
# - Git: For repository operations

###########################################################
# SECTION 1: SETUP AND CONFIGURATION
###########################################################

# Common variables used across all steps
FIXTURE_ID="l1"  # Change this for different fixtures: s1, s2, l1

# Define filter parameters based on FIXTURE_ID
# IMPORTANT: These must align with the configuration in create_starrynight_download_list.py
case "${FIXTURE_ID}" in
    "s1"|"s2")
        FILTER_PLATE="Plate1"
        FILTER_WELLS="WellA1,WellA2,WellB1"
        FILTER_SITES="0,1,2,3"
        FILTER_CYCLES="1,2,3"
        ;;
    "l1")
        FILTER_PLATE="Plate1"
        FILTER_WELLS="WellA1"
        FILTER_SITES=""  # Empty means no site filtering (all sites)
        FILTER_CYCLES="1,2,3"
        ;;
    *)
        echo "Unknown FIXTURE_ID: ${FIXTURE_ID}"
        exit 1
        ;;
esac

STARRYNIGHT_REPO_REL="$(git rev-parse --show-toplevel)" &&
SCRATCH_DIR="${STARRYNIGHT_REPO_REL}/scratch"

# Derived paths
FIX_INPUT_DIR="${SCRATCH_DIR}/fix_${FIXTURE_ID}_input"
FIX_OUTPUT_DIR="${SCRATCH_DIR}/fix_${FIXTURE_ID}_pcpip_output"
ARCHIVE_DIR="${STARRYNIGHT_REPO_REL}/starrynight/tests/fixtures/archives"
FIXTURE_UTILS_DIR="${STARRYNIGHT_REPO_REL}/starrynight/tests/fixtures/integration/utils"

# NOTE: LOAD_DATA_DIR is dataset-specific and should be updated for each fixture
LOAD_DATA_DIR="${FIX_OUTPUT_DIR}/Source1/workspace/load_data_csv/Batch1/Plate1"
LOAD_DATA_DIR_TRIMMED="${LOAD_DATA_DIR}_trimmed"

# Define source and target paths for path replacement
# Note: SOURCE_PATH and TARGET_PATH are dataset-specific and should be updated for each fixture
SOURCE_PATH="/home/ubuntu/bucket/projects/AMD_screening/20231011_batch_1/"
TARGET_PATH="${FIX_OUTPUT_DIR}/Source1/Batch1/"

# Set required environment variables for S3 access
# export BUCKET="your-source-bucket"
# export PROJECT="your-project-path"
# export BATCH="your-batch-name"
# export DEST_BUCKET="your-destination-bucket"

###########################################################
# SECTION 2: DATA ACQUISITION
###########################################################

# Note: The create_starrynight_download_list.py script provides configurable parameters to specify what subset of data to download:
#  - FIXTURE_ID: Choose the fixture type (s1, s2, l1)
#  - WELLS: Select which wells to include (default: ["A1", "A2", "B1"])
#  - SITES: Select which sites per well to include (default: [0, 1, 2, 3])
#  - CYCLES: Select which SBS cycles to include (default: range(1, 4))
#  - PLATE: Select which plate to use (default: "Plate1")
#
# Important: The script is currently tailored to work with a specific dataset format/structure.
# To use with other datasets that have different organization or naming conventions,
# code modifications would be needed beyond just changing the configuration parameters.

# Run create_starrynight_download_list.py script to create download lists
uv run create_starrynight_download_list.py

# Backup existing scratch directory if it exists
if [ -d "${SCRATCH_DIR}" ]; then
    mv ${SCRATCH_DIR} ${SCRATCH_DIR}_archive
fi

# Create scratch directory structure
mkdir -p ${SCRATCH_DIR}

# Copy the download list, change directory, and download files
cp ./scratch/download_list.txt ${SCRATCH_DIR}/download_list.txt &&
cd ${SCRATCH_DIR}/ &&
s5cmd run download_list.txt &&
echo "Downloads completed. Verify files were downloaded successfully." &&
cd -

###########################################################
# SECTION 3: DATA COMPRESSION
###########################################################
# Function to compress file only if not already JPEG compressed
cat > compress_if_needed.sh <<'EOF'
#!/usr/bin/env bash
if ! identify -format "%C" "$1" | grep -q JPEG; then
  echo "Compressing $1"
  magick "$1" -compress jpeg -quality 80 "$1"
else
  echo "$1 is already JPEG compressed"
fi
EOF
chmod +x compress_if_needed.sh

find "${FIX_INPUT_DIR}" -type f -name '*.tiff' \
  | parallel ./compress_if_needed.sh {}

# Compress TIFF files in the output directory only if needed
find "${FIX_OUTPUT_DIR}" -type f -name '*.tiff' \
  | parallel ./compress_if_needed.sh {}

rm compress_if_needed.sh

###########################################################
# SECTION 4: DATA FILTERING AND PROCESSING
###########################################################
# Create the trimmed directory if it doesn't exist
mkdir -p ${LOAD_DATA_DIR_TRIMMED}

# Filter LoadData CSVs (now we need to iterate over files and call the script for each one)
cd ${FIXTURE_UTILS_DIR}
for csv_file in ${LOAD_DATA_DIR}/*.csv; do
    if [ -f "$csv_file" ]; then
        filename=$(basename "$csv_file")
        echo "----------------------------------------"
        echo "Filtering $filename..."

        # Build command dynamically, only adding non-empty filters
        cmd="uv run loaddata_filter.py --input-csv \"$csv_file\" --output-csv \"${LOAD_DATA_DIR_TRIMMED}/${filename}\""

        [ -n "${FILTER_PLATE}" ] && cmd="${cmd} --plate ${FILTER_PLATE}"
        [ -n "${FILTER_WELLS}" ] && cmd="${cmd} --well ${FILTER_WELLS}"
        [ -n "${FILTER_SITES}" ] && cmd="${cmd} --site ${FILTER_SITES}"
        [ -n "${FILTER_CYCLES}" ] && cmd="${cmd} --cycle ${FILTER_CYCLES}"

        # Execute the command
        eval ${cmd}

        echo "----------------------------------------"
    fi
done

# Post-process LoadData CSVs (now we need to iterate over files and call the script for each one)
cd ${FIXTURE_UTILS_DIR}
for csv_file in ${LOAD_DATA_DIR_TRIMMED}/*.csv; do
    if [ -f "$csv_file" ]; then
        filename=$(basename "$csv_file")
        echo "----------------------------------------"
        echo "Post-processing $filename..."

        uv run loaddata_postprocess.py \
            --input-csv "$csv_file" \
            --output-csv "$csv_file" \
            --source-path "$SOURCE_PATH" \
            --target-path "$TARGET_PATH"
        echo "----------------------------------------"
    fi
done

# Note: The loaddata_postprocess.py script will update the values of some FileName_X columns.
# This means that it will now be out of sync with the actual file paths in the images directory in the FIX_INPUT_DIR.
# Therefore, the paths in FIX_INPUT_DIR need to be updated to match the new values in the FileName_X columns.
# W have not yet implemented this.

###########################################################
# SECTION 5: DATA VALIDATION
###########################################################
# Soft link images directory so it can be found when validating
ln -s ${FIX_INPUT_DIR}/Source1/Batch1/images ${FIX_OUTPUT_DIR}/Source1/Batch1/

# Create a temporary directory for missing files reports
TEMP_MISSING_DIR="${LOAD_DATA_DIR_TRIMMED}/temp_missing_files"
mkdir -p "${TEMP_MISSING_DIR}"

# Validate all CSV files in the trimmed directory
# Note: This will generate a missing files report for each CSV file in the LOAD_DATA_DIR_TRIMMED directory.
# Given the renaming of the FileName_X indicated in SECTION 4, we should expect to see missing files for the renamed columns.

cd ${FIXTURE_UTILS_DIR}
for csv_file in ${LOAD_DATA_DIR_TRIMMED}/*.csv; do
    if [ -f "$csv_file" ]; then
        filename=$(basename "$csv_file")
        echo "----------------------------------------"
        echo "Validating $filename..."

        # Generate a temporary missing files report name
        temp_missing_file="${TEMP_MISSING_DIR}/missing_files_$(basename "$csv_file" .csv).csv"

        uv run loaddata_validate.py \
            --input-csv "$csv_file" \
            --base-path "${FIX_OUTPUT_DIR}" \
            --output-file "$temp_missing_file"
        echo "----------------------------------------"
    fi
done

# Remove the temporary directory
rm -rf "${TEMP_MISSING_DIR}"

# Drop the soft link
rm ${FIX_OUTPUT_DIR}/Source1/Batch1/images

###########################################################
# SECTION 6: ARCHIVE CREATION
###########################################################
# Set archive name
OUTPUT_ARCHIVE_NAME="fix_${FIXTURE_ID}_output.tar.gz"
INPUT_ARCHIVE_NAME="fix_${FIXTURE_ID}_input.tar.gz"

# Create directory for archives if it doesn't exist
mkdir -p ${ARCHIVE_DIR}

# Create the output archive
tar -czf ${ARCHIVE_DIR}/${OUTPUT_ARCHIVE_NAME} -C ${SCRATCH_DIR} "${LOAD_DATA_DIR_TRIMMED#${SCRATCH_DIR}/}"

# Generate SHA256 checksum for output archive
cd ${ARCHIVE_DIR} &&
sha256sum ${OUTPUT_ARCHIVE_NAME} > ${OUTPUT_ARCHIVE_NAME}.sha256 &&
cd -

echo "Output archive created: ${ARCHIVE_DIR}/${OUTPUT_ARCHIVE_NAME}"
echo "Verify with: cd ${ARCHIVE_DIR} && sha256sum -c ${OUTPUT_ARCHIVE_NAME}.sha256"

# View the structure of the output archive
tar -tvf ${ARCHIVE_DIR}/${OUTPUT_ARCHIVE_NAME}

# Create the input archive
tar -czf ${ARCHIVE_DIR}/${INPUT_ARCHIVE_NAME} --exclude="*pipelines*" -C ${SCRATCH_DIR} "${FIX_INPUT_DIR#${SCRATCH_DIR}/}"

# Generate SHA256 checksum for input archive
cd ${ARCHIVE_DIR} &&
sha256sum ${INPUT_ARCHIVE_NAME} > ${INPUT_ARCHIVE_NAME}.sha256 &&
cd -

echo "Input archive created: ${ARCHIVE_DIR}/${INPUT_ARCHIVE_NAME}"
echo "Verify with: cd ${ARCHIVE_DIR} && sha256sum -c ${INPUT_ARCHIVE_NAME}.sha256"

# View the structure of the input archive
tar -tvf ${ARCHIVE_DIR}/${INPUT_ARCHIVE_NAME}
