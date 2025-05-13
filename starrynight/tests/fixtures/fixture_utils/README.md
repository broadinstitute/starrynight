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
- `create_fixture_archive.sh`: Creates compressed archives and checksums for fixture data

## Typical Workflow

1. Create download lists using `create_starrynight_download_list.py`
2. Download files from S3
3. Filter LoadData CSV files using `filter_loaddata_csv.py`
4. Validate paths using `validate_loaddata_paths.py`
5. Compress files using image compression tools
6. Create archives using `create_fixture_archive.sh`

## Usage Examples

### Creating Download Lists

`create_starrynight_download_list.py` creates two files:

- `download_list.txt`: Commands to download from S3 to local
- `s3_copy_list.txt`: Commands to copy from one S3 bucket to another

The script supports different fixture types (s1, s2, l1) through a `FIXTURE_ID` variable at the top of the script.

```sh
# Set required environment variables
export BUCKET="your-source-bucket"
export PROJECT="your-project-path"
export BATCH="your-batch-name"
export DEST_BUCKET="your-destination-bucket"

# Edit FIXTURE_ID in the script to select fixture type
# FIXTURE_ID = "s1"  # For fix_s1 fixture
# FIXTURE_ID = "s2"  # For fix_s2 fixture
# FIXTURE_ID = "l1"  # For fix_l1 fixture

# Run the script
uv run create_starrynight_download_list.py
```

### Download the files

These commands download the test fixture files from AWS S3 using the previously generated download list.

```sh
# Define repository paths
STARRYNIGHT_REPO_REL="$(git rev-parse --show-toplevel)"
SCRATCH_DIR=${STARRYNIGHT_REPO_REL}/scratch

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
# Set fixture type (same as in create_starrynight_download_list.py)
FIXTURE_ID="s1"

# Compress TIFF and CSV files to reduce disk usage

## Compress all TIFF files
# Define input and output directories
FIX_INPUT_DIR="${SCRATCH_DIR}/fix_${FIXTURE_ID}_input"
FIX_OUTPUT_DIR="${SCRATCH_DIR}/fix_${FIXTURE_ID}_pcpip_output"

# Compress TIFF files in both directories
find ${FIX_INPUT_DIR}  -type f -name "*.tiff" | parallel 'magick {} -compress jpeg -quality 80 {}'
find ${FIX_OUTPUT_DIR} -type f -name "*.tiff" | parallel 'magick {} -compress jpeg -quality 80 {}'

# Compress CSV files in output directory
find ${FIX_OUTPUT_DIR} -type f -name "*.csv" | parallel 'gzip -9 {}'
```

### Filtering LoadData CSVs

```sh
# Set fixture type (same as in create_starrynight_download_list.py)
FIXTURE_ID="s1"

STARRYNIGHT_REPO_REL="$(git rev-parse --show-toplevel)"
LOAD_DATA_DIR="${STARRYNIGHT_REPO_REL}/scratch/fix_${FIXTURE_ID}_pcpip_output/Source1/workspace/load_data_csv/Batch1/Plate1"
LOAD_DATA_DIR_TRIMMED=${LOAD_DATA_DIR}_trimmed

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
# Set fixture type (same as in create_starrynight_download_list.py)
FIXTURE_ID="s1"

STARRYNIGHT_REPO_REL="$(git rev-parse --show-toplevel)"
TRIMMED_LOAD_DATA_DIR="${STARRYNIGHT_REPO_REL}/scratch/fix_${FIXTURE_ID}_pcpip_output/Source1/workspace/load_data_csv/Batch1/Plate1_trimmed"

# Soft link images directory so it can be found when validating
ln -s ${STARRYNIGHT_REPO_REL}/scratch/fix_s1_input/Source1/Batch1/images ${STARRYNIGHT_REPO_REL}/scratch/fix_s1_pcpip_output/Source1/Batch1/

parallel uv run validate_loaddata_paths.py ${TRIMMED_LOAD_DATA_DIR}/load_data_pipeline{}.csv ::: 1 2 3 5 6 7 9
```

This will:

1. Check if files referenced in the CSV exist
2. Output a summary of missing files
3. Create a `missing_files.csv` if any files are missing

### Creating Fixture Archives

The `create_fixture_archive.sh` script creates compressed archives of test fixture data and generates checksums for validation and distribution.

```sh
# Archive the trimmed LoadData CSVs directory
FIXTURE_ID="s1"
ARCHIVE_DIR="${STARRYNIGHT_REPO_REL}/starrynight/tests/fixtures/archives"
SOURCE_DIR="${STARRYNIGHT_REPO_REL}/scratch/fix_${FIXTURE_ID}_pcpip_output/Source1/workspace/load_data_csv/Batch1/Plate1_trimmed"

# Create directory for archives if it doesn't exist
mkdir -p ${ARCHIVE_DIR}

# Create archive and SHA256 checksum
./create_fixture_archive.sh \
    ${SOURCE_DIR} \
    ${ARCHIVE_DIR} \
    "fix_${FIXTURE_ID}_loaddata_trimmed" \
    sha256
```

This will:

1. Create a `tar.gz` archive of the specified directory
2. Generate a checksum file using the specified algorithm (SHA256 or MD5)
3. Save both files to the output directory

The outputs can be verified later using:

```sh
# Verify the archive integrity
cd ${ARCHIVE_DIR}
sha256sum -c fix_${FIXTURE_ID}_loaddata_trimmed.tar.gz.sha256
```
