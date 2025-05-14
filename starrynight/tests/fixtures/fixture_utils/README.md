# Fixture Utils

Utility scripts for creating, manipulating, and validating test fixtures.

## Overview

This directory contains Python scripts and utilities to help manage test fixture requirements.

For detailed usage, see the executable shell script `fixture_utils.sh`, which contains:

- Common variables and derived paths
- Detailed workflow steps
- Execution commands with error handling

The shell script is the primary reference for working with these utilities and includes all the
documentation previously in this README.

## Available Scripts

- `create_starrynight_download_list.py`: Creates download lists for test fixtures
- `loaddata_utils.py`: Consolidated utility for processing LoadData CSV files:
  - `filter`: Filters LoadData CSV files to create smaller datasets
  - `validate`: Validates paths in LoadData CSVs
  - `postprocess`: Updates paths, headers, and identifiers in CSVs
