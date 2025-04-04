# Create trimmed CSVs

Scripts for filtering CellProfiler LoadData CSV files to create smaller datasets for development and testing.

`filter_loaddata_csv.py` filters by metadata (wells, sites, plates, cycles):

```bash
STARRYNIGHT_REPO_REL="../../../.."
LOAD_DATA_DIR="${STARRYNIGHT_REPO_REL}/scratch/starrynight_example_output_baseline/Source1/workspace/load_data_csv/Batch1/Plate1"
LOAD_DATA_DIR_TRIMMED=${LOAD_DATA_DIR}_trimmed

./filter_loaddata_csv.py \
    ${LOAD_DATA_DIR} \
    ${LOAD_DATA_DIR_TRIMMED} \
    --plate Plate1 \
    --well WellA1,WellA2,WellB1 \
    --site 0,1 \
    --cycle 1,2,3
```

Replace absolute paths with relative paths:

```bash

# Update this
STARRYNIGHT_REPO=/Users/shsingh/Documents/GitHub/starrynight
BASE_DIR=${STARRYNIGHT_REPO}/scratch/starrynight_example_output_baseline

# Replace path in all trimmed CSV files
find ${LOAD_DATA_DIR_TRIMMED} \
    -name "*.csv" \
    -exec sed -i.bak "s|/home/ubuntu/bucket/projects/AMD_screening/20231011_batch_1/|${BASE_DIR}/Source1/Batch1/|g" {} \; -exec rm {}.bak \;
```

`validate_loaddata_paths.py` validates paths and checks if referenced files exist:

```bash
STARRYNIGHT_REPO_REL="../../../.."
TRIMMED_LOAD_DATA_DIR="${STARRYNIGHT_REPO_REL}/scratch/starrynight_example_output_baseline/Source1/workspace/load_data_csv/Batch1/Plate1_trimmed"
parallel python validate_loaddata_paths.py ${TRIMMED_LOAD_DATA_DIR}/load_data_pipeline{}.csv ::: 1 2 3 5 6 7 9
```
