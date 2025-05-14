# Fixture Utils

Utility scripts for creating, manipulating, and validating test fixtures.

## Overview

This directory contains Python scripts and utilities to help manage test fixture requirements by:

1. Creating test fixture datasets from larger production data
2. Validating data integrity of LoadData CSV files and referenced file paths
3. Optimizing disk usage through compression techniques for large image files

## Available Scripts

- `create_starrynight_download_list.py`: Creates download and S3 copy lists for test fixtures
- `loaddata_filter.py`: Filters CellProfiler LoadData CSV files to create smaller datasets
- `loaddata_validate.py`: Validates paths in LoadData CSVs and checks if referenced files exist
- `loaddata_postprocess.py`: Updates paths, headers, and identifiers in LoadData CSV files

## Script Design

Each script is designed to process a single CSV file at a time with clearly defined input and output paths. The main shell script (`fixture_utils.sh`) handles file iteration and orchestrates the workflow.

### LoadData CSV Files

These utilities work with CellProfiler LoadData CSV files, which have:
- Row-based image references
- PathName_X/FileName_X column pairs that form file paths
- Metadata columns (Plate, Well, Site, Cycle)

## Workflow

The workflow typically follows these steps:

1. Generate download lists using `create_starrynight_download_list.py`
2. Filter data to specific wells/sites using `loaddata_filter.py`
3. Update file paths using `loaddata_postprocess.py`
4. Validate file existence using `loaddata_validate.py`
5. Create compressed archives for test fixtures

For detailed usage, see the executable shell script `fixture_utils.sh`, which contains the complete workflow implementation.
