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
# Install s5cmd first if not available: https://github.com/peak/s5cmd

# Common variables used across all steps
FIXTURE_ID="s1"  # Change this for different fixtures: s1, s2, l1
STARRYNIGHT_REPO_REL="$(git rev-parse --show-toplevel)" &&
SCRATCH_DIR="${STARRYNIGHT_REPO_REL}/scratch"

# Derived paths
FIX_INPUT_DIR="${SCRATCH_DIR}/fix_${FIXTURE_ID}_input"
FIX_OUTPUT_DIR="${SCRATCH_DIR}/fix_${FIXTURE_ID}_pcpip_output"
LOAD_DATA_DIR="${FIX_OUTPUT_DIR}/Source1/workspace/load_data_csv/Batch1/Plate1"
LOAD_DATA_DIR_TRIMMED="${LOAD_DATA_DIR}_trimmed"
ARCHIVE_DIR="${STARRYNIGHT_REPO_REL}/starrynight/tests/fixtures/archives"
FIXTURE_UTILS_DIR="${STARRYNIGHT_REPO_REL}/starrynight/tests/fixtures/fixture_utils"

# Set required environment variables for S3 access
# export BUCKET="your-source-bucket"
# export PROJECT="your-project-path"
# export BATCH="your-batch-name"
# export DEST_BUCKET="your-destination-bucket"

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

# Create the trimmed directory if it doesn't exist
mkdir -p ${LOAD_DATA_DIR_TRIMMED}

# IMPORTANT: The arguments below must align with the configuration in create_starrynight_download_list.py
# Ensure these values match the PLATE, WELLS, SITES, and CYCLES variables in that script

# Filter LoadData CSVs (now we need to iterate over files and call the script for each one)
cd ${FIXTURE_UTILS_DIR}
for csv_file in ${LOAD_DATA_DIR}/*.csv; do
    if [ -f "$csv_file" ]; then
        filename=$(basename "$csv_file")
        echo "Filtering $filename..."

        uv run loaddata_filter.py \
            --input-csv "$csv_file" \
            --output-csv "${LOAD_DATA_DIR_TRIMMED}/${filename}" \
            --plate Plate1 \
            --well WellA1,WellA2,WellB1 \
            --site 0,1,2,3 \
            --cycle 1,2,3
    fi
done

# Define source and target paths for path replacement
SOURCE_PATH="/home/ubuntu/bucket/projects/AMD_screening/20231011_batch_1/"
TARGET_PATH="${FIX_OUTPUT_DIR}/Source1/Batch1/"

# Post-process LoadData CSVs (now we need to iterate over files and call the script for each one)
cd ${FIXTURE_UTILS_DIR}
for csv_file in ${LOAD_DATA_DIR_TRIMMED}/*.csv; do
    if [ -f "$csv_file" ]; then
        filename=$(basename "$csv_file")
        echo "Post-processing $filename..."

        uv run loaddata_postprocess.py \
            --input-csv "$csv_file" \
            --output-csv "$csv_file" \
            --source-path "$SOURCE_PATH" \
            --target-path "$TARGET_PATH"
    fi
done

# Soft link images directory so it can be found when validating
ln -s ${FIX_INPUT_DIR}/Source1/Batch1/images ${FIX_OUTPUT_DIR}/Source1/Batch1/

# Create a temporary directory for missing files reports
TEMP_MISSING_DIR="${LOAD_DATA_DIR_TRIMMED}/temp_missing_files"
mkdir -p "${TEMP_MISSING_DIR}"

# Validate all CSV files in the trimmed directory
cd ${FIXTURE_UTILS_DIR}
for csv_file in ${LOAD_DATA_DIR_TRIMMED}/*.csv; do
    if [ -f "$csv_file" ]; then
        filename=$(basename "$csv_file")
        echo "Validating $filename..."

        # Generate a temporary missing files report name
        temp_missing_file="${TEMP_MISSING_DIR}/missing_files_$(basename "$csv_file" .csv).csv"

        uv run loaddata_validate.py \
            --input-csv "$csv_file" \
            --base-path "${FIX_OUTPUT_DIR}" \
            --output-file "$temp_missing_file"
    fi
done

# Remove the temporary directory
rm -rf "${TEMP_MISSING_DIR}"

# Drop the soft link
rm ${FIX_OUTPUT_DIR}/Source1/Batch1/images

# Set archive name
OUTPUT_ARCHIVE_NAME="fix_${FIXTURE_ID}_output.tar.gz"
INPUT_ARCHIVE_NAME="fix_${FIXTURE_ID}_input.tar.gz"

# Create directory for archives if it doesn't exist
mkdir -p ${ARCHIVE_DIR}

# Create the output archive
cd $(dirname ${LOAD_DATA_DIR_TRIMMED}) &&
tar -czf ${ARCHIVE_DIR}/${OUTPUT_ARCHIVE_NAME} $(basename ${LOAD_DATA_DIR_TRIMMED}) &&
cd -

# Generate SHA256 checksum for output archive
cd ${ARCHIVE_DIR} &&
sha256sum ${OUTPUT_ARCHIVE_NAME} > ${OUTPUT_ARCHIVE_NAME}.sha256 &&
cd -

echo "Output archive created: ${ARCHIVE_DIR}/${OUTPUT_ARCHIVE_NAME}"
echo "Verify with: cd ${ARCHIVE_DIR} && sha256sum -c ${OUTPUT_ARCHIVE_NAME}.sha256"

# Create the input archive
cd $(dirname ${FIX_INPUT_DIR}) &&
tar -czf ${ARCHIVE_DIR}/${INPUT_ARCHIVE_NAME} --exclude="*pipelines*" $(basename ${FIX_INPUT_DIR}) &&
cd -

# Generate SHA256 checksum for input archive
cd ${ARCHIVE_DIR} &&
sha256sum ${INPUT_ARCHIVE_NAME} > ${INPUT_ARCHIVE_NAME}.sha256 &&
cd -

echo "Input archive created: ${ARCHIVE_DIR}/${INPUT_ARCHIVE_NAME}"
echo "Verify with: cd ${ARCHIVE_DIR} && sha256sum -c ${INPUT_ARCHIVE_NAME}.sha256"
