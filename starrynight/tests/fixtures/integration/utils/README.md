# Fixture Creation Utils

Tools for creating test fixtures from production microscopy data. These scripts download, filter, and package subsets of data for integration testing.

## Available Fixtures

**FIX-S1 and FIX-S2** (Remote fixtures)

- Wells: A1, A2, B1
- Sites per well: 4 (sites 0-3)
- Total images: ~100
- Size: ~5GB each
- Usage: Downloaded from GitHub releases

**FIX-L1** (Local-only fixture)

- Wells: A1 only
- Sites per well: 1025 (sites 0-1024)
- Total images: ~5000
- Size: ~500GB
- Usage: Must exist locally, never uploaded

## Quick Start: Creating FIX-L1

⚠️ **WARNING**: FIX-L1 requires ~500GB disk space and several hours to create.

### Prerequisites

```bash
# Required tools
- s5cmd (for S3 downloads)
- ImageMagick (for compression)
- GNU Parallel
- uv (Python environment)

# Environment variables
export BUCKET="your-source-bucket"
export PROJECT="your-project-path"
export BATCH="your-batch-name"
export DEST_BUCKET="your-destination-bucket"
```

### Step-by-Step Process

1.  **Verify Configuration** (scripts are pre-configured for FIX-L1):

   ```bash
   cd starrynight/tests/fixtures/integration/utils

   # Check create_starrynight_download_list.py has:
   # FIXTURE_ID = "l1"
   # WELLS = ["A1"]
   # SITES = list(range(0, 1025))

   # Check fixture_utils.sh has:
   # FIXTURE_ID="l1"
   # Filter parameters are automatically configured:
   # - Wells: WellA1
   # - Sites: (all sites - no filtering)
   # - Cycles: 1,2,3
   ```

2.  **Run Fixture Creation** (⚠️ MANUAL PROCESS):

   ```bash
   # DO NOT run fixture_utils.sh directly!
   # Open it and run each section manually:

   # SECTION 1: Review configuration
   # SECTION 2: Generate download lists and download (~2-3 hours)
   # SECTION 3: Compress images (~1-2 hours)
   # SECTION 4: Filter LoadData CSVs
   # SECTION 5: Validate file references
   # SECTION 6: Skip for local-only fixtures
   ```

3.  **Critical Manual Adjustments**:

   ```bash
   # In fixture_utils.sh, update these dataset-specific variables in SECTION 1:
   LOAD_DATA_DIR="${FIX_OUTPUT_DIR}/Source1/workspace/load_data_csv/Batch1/Plate1"
   SOURCE_PATH="/home/ubuntu/bucket/projects/AMD_screening/20231011_batch_1/"
   TARGET_PATH="${FIX_OUTPUT_DIR}/Source1/Batch1/"
   ```

4.  **Deploy to Test Environment**:

   ```bash
   export STARRYNIGHT_TEST_FIXTURE_DIR=/path/to/test/fixtures

   # Move completed fixtures (not archives)
   mv scratch/fix_l1_input $STARRYNIGHT_TEST_FIXTURE_DIR/
   mv scratch/fix_l1_pcpip_output $STARRYNIGHT_TEST_FIXTURE_DIR/
   ```

## Creating Other Fixtures

### Small Remote Fixtures (S1, S2)

1.  Edit configuration in both scripts:

   ```python
   # create_starrynight_download_list.py
   FIXTURE_ID = "s1"  # or "s2"
   WELLS = ["A1", "A2", "B1"]
   SITES = [0, 1, 2, 3]
   ```

2.  Update fixture_utils.sh to match:

   ```bash
   FIXTURE_ID="s1"  # or "s2"
   # Filter configuration is now automatic based on FIXTURE_ID
   # The script will use the appropriate filters for s1/s2
   ```

3.  Run sections manually, then upload archives to GitHub release

### Custom Fixtures

Modify the configuration parameters as needed:

- Different wells: Change `WELLS` list
- Different site count: Adjust `SITES` range
- Different cycles: Modify `CYCLES` range

## Script Reference

**fixture_utils.sh**

- Purpose: Main workflow orchestrator
- Key parameters: FIXTURE_ID, SOURCE_PATH, TARGET_PATH
- Auto-configures filter parameters based on FIXTURE_ID (no manual filter editing needed)

**create_starrynight_download_list.py**

- Purpose: Generate S3 download lists
- Key parameters: FIXTURE_ID, WELLS, SITES, CYCLES

**loaddata_filter.py**

- Purpose: Filter CSV by metadata
- Key parameters: --well, --site, --cycle

**loaddata_postprocess.py**

- Purpose: Fix paths and naming
- Key parameters: --source-path, --target-path

**loaddata_validate.py**

- Purpose: Check file references
- Key parameters: --base-path

## Troubleshooting

- **Downloads failing**: Check S3 credentials and bucket permissions
- **Out of space**: FIX-L1 needs ~500GB free space
- **Missing files**: Review SOURCE_PATH and TARGET_PATH settings
- **Tests not finding fixtures**: Verify STARRYNIGHT_TEST_FIXTURE_DIR is set

For complete fixture testing instructions, see [../README.md](../README.md).
