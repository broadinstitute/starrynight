# LoadData CSV Processing Requirements

This document outlines requirements for three Python scripts that process CellProfiler LoadData CSV files for test fixture creation.

## Important Design Note

Each script is designed to process a single CSV file at a time, with clearly defined input and output paths. Any batch processing or file iteration should be handled by external scripts or shell commands that call these Python scripts.

## Background for Developers

### What are LoadData CSV Files?

CellProfiler (a bioimage analysis tool) uses CSV files to locate and process image data. These files have a specific structure:

1. Each row represents an image to be processed
2. Column pairs like `PathName_X` and `FileName_X` point to image files
   - When joined, they form complete file paths: `PathName_DNA/FileName_DNA`
   - Multiple channel pairs can exist (DNA, Actin, Tubulin, etc.)
3. Metadata columns begin with `Metadata_` prefix:
   - `Metadata_Plate`: Identifies the plate (e.g., "Plate1")
   - `Metadata_Well`: Identifies the well (e.g., "WellA1", "WellB2")
   - `Metadata_Site`: Identifies imaging site (e.g., "0", "1", "2")
   - `Metadata_SBSCycle`: Identifies imaging cycle (e.g., "1", "2", "3")
4. Some column names include cycle information with format `_CycleNN_` (e.g., `_Cycle01_`)

### Project Context

We need to create small test fixtures from large production datasets. This involves:
- Filtering data to include only specific wells, sites, and cycles
- Adjusting file paths to work on different systems
- Verifying that all referenced files exist

## Script 1: loaddata_filter.py

**Purpose:** Filter a LoadData CSV file to create a smaller dataset with only specific metadata values.

### Requirements

1. **Command Line Interface:**
   - Required arguments:
     - `--input-csv`: Path to the input CSV file
     - `--output-csv`: Path where the filtered CSV will be saved
   - Optional flags for filtering criteria:
     - `--plate`: Comma-separated list of plate values to keep (e.g., "Plate1")
     - `--well`: Comma-separated list of well values to keep (e.g., "WellA1,WellA2,WellB1")
     - `--site`: Comma-separated list of site values to keep (e.g., "0,1,2,3")
     - `--cycle`: Comma-separated list of cycle values to keep (e.g., "1,2,3")

2. **Functionality:**
   - Read the specified CSV file
   - Filter rows to keep only those matching specified metadata values
   - Special handling for cycle filtering:
     - If `Metadata_SBSCycle` column exists, filter rows like other metadata
     - For CSVs with cycle info in column names, filter columns instead
   - Filter columns to remove cycle-specific columns that don't match specified cycles
     - Column names with patterns like `_Cycle01_`, `_Cycle02_` should only be kept if they match a specified cycle
   - Save filtered CSV to the specified output path
   - Report the reduction in size (rows and columns)

3. **Example Usage:**
   ```
   python loaddata_filter.py \
       --input-csv input.csv \
       --output-csv output.csv \
       --plate Plate1 \
       --well WellA1,WellA2,WellB1 \
       --site 0,1,2,3 \
       --cycle 1,2,3
   ```

## Script 2: loaddata_postprocess.py

**Purpose:** Update LoadData CSV files to work in a local testing environment.

### Requirements

1. **Command Line Interface:**
   - Required arguments:
     - `--input-csv`: Path to input CSV file
     - `--output-csv`: Path to save processed file
     - `--source-path`: Original path prefix to replace
     - `--target-path`: New path prefix to use

2. **Functionality:**
   - Process a single CSV file
   - All operations are performed automatically:
     - Replace absolute paths in the CSV content (using source and target paths)
     - Rename "Metadata_SBSCycle" column to "Metadata_Cycle"
     - Remove "Well" prefix from values in "Metadata_Well" column (e.g., "WellA1" → "A1")
   - Save processed file to specified output path
   - Report changes made to the file

3. **Example Usage:**
   ```
   python loaddata_postprocess.py \
       --input-csv /path/to/input.csv \
       --output-csv /path/to/output.csv \
       --source-path /original/path \
       --target-path /new/path
   ```

## Script 3: loaddata_validate.py

**Purpose:** Validate that all files referenced in a LoadData CSV file actually exist.

### Requirements

1. **Command Line Interface:**
   - Required argument:
     - `--input-csv`: Path to CSV file to validate
   - Optional arguments:
     - `--base-path`: Base path to prepend to file paths
     - `--output-file`: Path to save report of missing files (default: "missing_files.csv")

2. **Functionality:**
   - For the specified CSV file:
     - Find all column pairs following pattern `PathName_X` and `FileName_X`
     - Join these column values to create complete file paths
     - Add base path if specified
     - Check if each file exists
     - Report missing files
   - Generate a summary of:
     - Total files referenced
     - Number of missing files
   - If any files are missing, save a report to CSV

3. **Example Usage:**
   ```
   python loaddata_validate.py --input-csv input.csv --base-path /path/to/files
   ```

## Integration Requirements

These scripts will be used as part of a workflow in `fixture_utils.sh`:

1. First, `loaddata_filter.py` is run to create a smaller dataset
2. Then, `loaddata_postprocess.py` is run to update paths and metadata
3. Finally, `loaddata_validate.py` is run to verify file existence

The external shell script will handle file iteration and pass appropriate arguments to each Python script.

## Technical Guidelines

- Use Python 3.8+
- Use pathlib for all file path handling
- Use click for command-line interface implementation
- Follow functional programming principles
- Keep scripts simple and focused only on the task at hand
- For CSV processing, use pandas
- Do not implement extensive error handling beyond the minimum required
- Avoid over-engineering - these scripts are only for test fixture creation
- Report critical information with concise, formatted output
