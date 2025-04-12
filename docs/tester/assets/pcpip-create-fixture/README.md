# pcpip-create-fixture

Tools for creating and manipulating test fixtures for PCPIP workflow.

<https://github.com/broadinstitute/starrynight/tree/main/docs/tester/assets/pcpip-create-fixture>

## Components

- `create_starrynight_download_list.py`: Creates download and S3 copy lists for test fixtures from AWS S3 buckets
- `compress_starrynight_example.sh`: Compresses TIFF and CSV files to reduce disk usage
- `filter_loaddata_csv.py`: Filters CellProfiler LoadData CSV files to create smaller datasets
- `validate_loaddata_paths.py`: Validates paths in LoadData CSVs and checks if referenced files exist

## Workflow

The typical workflow for creating test fixtures is:

1. Create download lists using `create_starrynight_download_list.py`
2. Download files from S3
3. Filter LoadData CSV files using `filter_loaddata_csv.py`
4. Validate paths using `validate_loaddata_paths.py`
5. Compress files using `compress_starrynight_example.sh`

## Usage Examples

### Creating Download Lists

`create_starrynight_download_list.py` creates two files:

- `download_list.txt`: Commands to download from S3 to local
- `s3_copy_list.txt`: Commands to copy from one S3 bucket to another

```sh
# Set required environment variables
export BUCKET="your-source-bucket"
export PROJECT="your-project-path"
export BATCH="your-batch-name"
export DEST_BUCKET="your-destination-bucket"

# Run the script
python create_starrynight_download_list.py
```

### Download the files

These commands download the test fixture files from AWS S3 using the previously generated download list.

```sh
# Define repository paths
STARRYNIGHT_REPO_REL="../../../.."
SCRATCH_DIR=${STARRYNIGHT_REPO_REL}/scratch

# Backup existing scratch directory if it exists
if [ -d "${SCRATCH_DIR}" ]; then
    mv ${SCRATCH_DIR} ${SCRATCH_DIR}_archive
fi

# Create scratch directory structure
mkdir -p ${SCRATCH_DIR}

# Copy the download list to scratch directory
cp download_list.txt ${SCRATCH_DIR}/

# Change to scratch directory
cd ${SCRATCH_DIR}

# Download files using s5cmd (fast S3 command line client)
# Install s5cmd first if not available: https://github.com/peak/s5cmd
s5cmd run download_list.txt

# Verify download completion
echo "Downloads completed. Verify files were downloaded successfully."
```

### Compressing Files

```sh
# Compress TIFF and CSV files to reduce disk usage
./compress_starrynight_example.sh
```

### Filtering LoadData CSVs

```sh
STARRYNIGHT_REPO_REL="../../../.."
LOAD_DATA_DIR="${STARRYNIGHT_REPO_REL}/scratch/pcpip_example_output/Source1/workspace/load_data_csv/Batch1/Plate1"
LOAD_DATA_DIR_TRIMMED=${LOAD_DATA_DIR}_trimmed

./filter_loaddata_csv.py \
    ${LOAD_DATA_DIR} \
    ${LOAD_DATA_DIR_TRIMMED} \
    --plate Plate1 \
    --well WellA1,WellA2,WellB1 \
    --site 0,1 \
    --cycle 1,2,3
```

#### Updating Paths in Filtered CSVs

After filtering, you may need to update paths in the CSV files:

```sh
# Update this
STARRYNIGHT_REPO=/Users/shsingh/Documents/GitHub/starrynight
BASE_DIR=${STARRYNIGHT_REPO}/scratch/pcpip_example_output

# Replace path in all trimmed CSV files
find ${LOAD_DATA_DIR_TRIMMED} \
    -name "*.csv" \
    -exec sed -i.bak "s|/home/ubuntu/bucket/projects/AMD_screening/20231011_batch_1/|${BASE_DIR}/Source1/Batch1/|g" {} \; -exec rm {}.bak \;
```

### Validating LoadData Paths

```sh
STARRYNIGHT_REPO_REL="../../../.."
TRIMMED_LOAD_DATA_DIR="${STARRYNIGHT_REPO_REL}/scratch/pcpip_example_output/Source1/workspace/load_data_csv/Batch1/Plate1_trimmed"
parallel python validate_loaddata_paths.py ${TRIMMED_LOAD_DATA_DIR}/load_data_pipeline{}.csv ::: 1 2 3 5 6 7 9
```

This will:

1. Check if files referenced in the CSV exist
2. Output a summary of missing files
3. Create a `missing_files.csv` if any files are missing
