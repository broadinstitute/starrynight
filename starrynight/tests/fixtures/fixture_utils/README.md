# Fixture Utils

Utility scripts for creating, manipulating, and validating test fixtures.

## Purpose

These utilities help manage the test fixture requirements by:

1. **Creating test fixture datasets** from larger production data
2. **Validating data integrity** of LoadData CSV files and referenced file paths
3. **Optimizing disk usage** through compression techniques for large image files

## Components

- `create_starrynight_download_list.py`: Creates download and S3 copy lists for test fixtures (fix_s1, fix_s2, fix_l1) from AWS S3 buckets
- `filter_loaddata_csv.py`: Filters CellProfiler LoadData CSV files to create smaller datasets
- `validate_loaddata_paths.py`: Validates paths in LoadData CSVs and checks if referenced files exist
- `postprocess_loaddata_csv.py`: Updates paths, headers, and identifiers in LoadData CSV files

## Typical Workflow

1. Create download lists using `create_starrynight_download_list.py`
2. Download files from S3
3. Filter LoadData CSV files using `filter_loaddata_csv.py`
4. Validate paths using `validate_loaddata_paths.py`
5. Compress files using image compression tools
6. Create archives for distribution using standard tar and sha256sum commands

## Usage Examples

The following examples demonstrate a complete workflow. Set these common variables once at the start of your workflow:

```sh
# Common variables used across all steps
FIXTURE_ID="s1"  # Change this for different fixtures: s1, s2, l1
STARRYNIGHT_REPO_REL="$(git rev-parse --show-toplevel)"
SCRATCH_DIR="${STARRYNIGHT_REPO_REL}/scratch"

# Derived paths
FIX_INPUT_DIR="${SCRATCH_DIR}/fix_${FIXTURE_ID}_input"
FIX_OUTPUT_DIR="${SCRATCH_DIR}/fix_${FIXTURE_ID}_pcpip_output"
LOAD_DATA_DIR="${FIX_OUTPUT_DIR}/Source1/workspace/load_data_csv/Batch1/Plate1"
LOAD_DATA_DIR_TRIMMED="${LOAD_DATA_DIR}_trimmed"
ARCHIVE_DIR="${STARRYNIGHT_REPO_REL}/starrynight/tests/fixtures/archives"
```

### Creating Download Lists

`create_starrynight_download_list.py` creates two files:

- `download_list.txt`: Commands to download from S3 to local
- `s3_copy_list.txt`: Commands to copy from one S3 bucket to another

The script supports different fixture types (s1, s2, l1) through a `FIXTURE_ID` variable at the top of the script.

```sh
# Set required environment variables for S3 access
export BUCKET="your-source-bucket"
export PROJECT="your-project-path"
export BATCH="your-batch-name"
export DEST_BUCKET="your-destination-bucket"

# Run the script
uv run create_starrynight_download_list.py
```

### Download the files

These commands download the test fixture files from AWS S3 using the previously generated download list.

```sh
# Backup existing scratch directory if it exists
if [ -d "${SCRATCH_DIR}" ]; then
    mv ${SCRATCH_DIR} ${SCRATCH_DIR}_archive
fi

# Create scratch directory structure
mkdir -p ${SCRATCH_DIR}

# Copy the download list to scratch directory
cp ./scratch/download_list.txt ${SCRATCH_DIR}/

# Change to scratch directory
cd ${SCRATCH_DIR}/../

# Download files using s5cmd (fast S3 command line client)
# Install s5cmd first if not available: https://github.com/peak/s5cmd
s5cmd run download_list.txt

# Verify download completion
echo "Downloads completed. Verify files were downloaded successfully."

cd -
```

### Compressing Files

```sh
# Compress TIFF and CSV files to reduce disk usage

# Compress TIFF files in both directories
find ${FIX_INPUT_DIR}  -type f -name "*.tiff" | parallel 'magick {} -compress jpeg -quality 80 {}'
find ${FIX_OUTPUT_DIR} -type f -name "*.tiff" | parallel 'magick {} -compress jpeg -quality 80 {}'

# Compress CSV files in output directory
find ${FIX_OUTPUT_DIR} -type f -name "*.csv" | parallel 'gzip -9 {}'
```

### Filtering LoadData CSVs

```sh
# IMPORTANT: The arguments below must align with the configuration in create_starrynight_download_list.py
# Ensure these values match the PLATE, WELLS, SITES, and CYCLES variables in that script

uv run filter_loaddata_csv.py \
    ${LOAD_DATA_DIR} \
    ${LOAD_DATA_DIR_TRIMMED} \
    --plate Plate1 \
    --well WellA1,WellA2,WellB1 \
    --site 0,1,2,3 \
    --cycle 1,2,3
```

#### Post-processing LoadData CSVs

After filtering, use the `postprocess_loaddata_csv.py` script to handle all post-processing tasks:

```sh
# Run all post-processing steps on the filtered CSVs:
# 1. Update file paths to match the local environment
# 2. Rename Metadata_SBSCycle to Metadata_Cycle
# 3. Remove the "Well" prefix from Metadata_Well values
uv run postprocess_loaddata_csv.py \
    --input-dir ${LOAD_DATA_DIR_TRIMMED} \
    --fixture-id ${FIXTURE_ID} \
    --update-paths \
    --update-headers \
    --clean-wells
```

This script will:
- Automatically determine the repository's absolute path using git
- Update all file paths in the CSVs from the original S3 paths to local paths
- Rename the `Metadata_SBSCycle` header to `Metadata_Cycle` if it exists
- Remove "Well" prefix from values in the `Metadata_Well` column (e.g., "WellA1" becomes "A1")

For more options and details, run `uv run postprocess_loaddata_csv.py --help`

### Validating LoadData Paths

```sh
# Soft link images directory so it can be found when validating
ln -s ${FIX_INPUT_DIR}/Source1/Batch1/images ${FIX_OUTPUT_DIR}/Source1/Batch1/

# Validate all pipeline CSVs in parallel
parallel uv run validate_loaddata_paths.py ${LOAD_DATA_DIR_TRIMMED}/load_data_pipeline{}.csv ::: 1 2 3 5 6 7 9
```

This will:

1. Check if files referenced in the CSV exist
2. Output a summary of missing files
3. Create a `missing_files.csv` if any files are missing

### Creating Fixture Archives

Use standard Unix commands to create tar.gz archives with SHA256 checksums for fixture data distribution:

```sh
# Set archive name
ARCHIVE_NAME="fix_${FIXTURE_ID}_output.tar.gz"

# Create directory for archives if it doesn't exist
mkdir -p ${ARCHIVE_DIR}

# Create the archive
cd $(dirname ${LOAD_DATA_DIR_TRIMMED})
tar -czf ${ARCHIVE_DIR}/${ARCHIVE_NAME} $(basename ${LOAD_DATA_DIR_TRIMMED})
cd -

# Generate SHA256 checksum
cd ${ARCHIVE_DIR}
sha256sum ${ARCHIVE_NAME} > ${ARCHIVE_NAME}.sha256
cd -

echo "Archive created: ${ARCHIVE_DIR}/${ARCHIVE_NAME}"
echo "Checksum saved: ${ARCHIVE_DIR}/${ARCHIVE_NAME}.sha256"
```

The outputs can be verified later using:

```sh
# Verify the archive integrity
cd ${ARCHIVE_DIR}
sha256sum -c ${ARCHIVE_NAME}.sha256
```
