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
# - loaddata_utils.py: Processes LoadData CSV files (filter, validate, and postprocess)
#   - filter: Filters CellProfiler LoadData CSV files to create smaller datasets
#   - validate: Validates paths in LoadData CSVs and checks if referenced files exist
#   - postprocess: Updates paths, headers, and identifiers in LoadData CSV files
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

# IMPORTANT: The arguments below must align with the configuration in create_starrynight_download_list.py
# Ensure these values match the PLATE, WELLS, SITES, and CYCLES variables in that script
cd ${FIXTURE_UTILS_DIR} &&
uv run loaddata_utils.py filter \
    ${LOAD_DATA_DIR} \
    ${LOAD_DATA_DIR_TRIMMED} \
    --plate Plate1 \
    --well WellA1,WellA2,WellB1 \
    --site 0,1,2,3 \
    --cycle 1,2,3

# Run all post-processing steps on the filtered CSVs:
# 1. Update file paths to match the local environment
# 2. Rename Metadata_SBSCycle to Metadata_Cycle
# 3. Remove the "Well" prefix from Metadata_Well values
cd ${FIXTURE_UTILS_DIR} &&
uv run loaddata_utils.py postprocess \
    --input-dir ${LOAD_DATA_DIR_TRIMMED} \
    --fixture-id ${FIXTURE_ID} \
    --update-paths \
    --update-headers \
    --clean-wells

# Soft link images directory so it can be found when validating
ln -s ${FIX_INPUT_DIR}/Source1/Batch1/images ${FIX_OUTPUT_DIR}/Source1/Batch1/

# Validate all pipeline CSVs in parallel
parallel uv run loaddata_utils.py validate ${LOAD_DATA_DIR_TRIMMED}/load_data_pipeline{}.csv ::: 1 2 3 5 6 7 9

# Drop the soft link
rm ${FIX_OUTPUT_DIR}/Source1/Batch1/images

# Set archive name
ARCHIVE_NAME="fix_${FIXTURE_ID}_output.tar.gz"

# Create directory for archives if it doesn't exist
mkdir -p ${ARCHIVE_DIR}

# Create the archive
cd $(dirname ${LOAD_DATA_DIR_TRIMMED}) &&
tar -czf ${ARCHIVE_DIR}/${ARCHIVE_NAME} $(basename ${LOAD_DATA_DIR_TRIMMED}) &&
cd -

# Generate SHA256 checksum
cd ${ARCHIVE_DIR} &&
sha256sum ${ARCHIVE_NAME} > ${ARCHIVE_NAME}.sha256 &&
cd -

echo "Archive created: ${ARCHIVE_DIR}/${ARCHIVE_NAME}"
echo "Verify with: cd ${ARCHIVE_DIR} && sha256sum -c ${ARCHIVE_NAME}.sha256"
