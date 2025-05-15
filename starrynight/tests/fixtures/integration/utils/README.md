# Fixture Utils

Utility scripts for creating and validating test fixture data.

## Available Scripts

- `create_starrynight_download_list.py`: Creates download and S3 copy lists for test fixtures
- `loaddata_filter.py`: Filters CellProfiler LoadData CSV files to create smaller datasets
- `loaddata_postprocess.py`: Updates paths, headers, and identifiers in LoadData CSV files
- `loaddata_validate.py`: Validates paths in LoadData CSVs and checks if referenced files exist

## Role in Fixture Workflow

These utilities handle the data preparation phase (steps 1-2) of the fixture creation workflow:
- Preparing filtered datasets
- Creating archive files
- Generating SHA256 hashes

For complete fixture management instructions, see [../README.md](../README.md).
