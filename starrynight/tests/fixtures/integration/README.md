# StarryNight Integration Test Fixtures Guide

Test fixtures are standardized datasets that ensure our image processing workflows work correctly.
Each fixture must be configured in the test system before use.

**Flow**: Production Data → Filter/Package (`utils/`) → Configure Tests → Run Tests

## Overview

Test fixtures provide standardized data for integration tests. The system supports:

- **Remote fixtures** (fix_s1, fix_s2): Downloaded from GitHub releases, cached locally
- **Local-only fixtures** (fix_l1): Never downloaded, must exist locally

Key files:

- `fixtures/integration/constants.py` - Fixture configurations
- `conftest.py` - Pytest fixture definitions
- `integration/constants.py` - Test compatibility matrix
- `test_getting_started_workflow.py` - Main integration tests

## Before You Start

You'll need:

- Access to production microscopy data
- ~1-2 hours for full setup
- Understanding of which workflows you want to test

## Adding a New Fixture

### Phase 1: Create Fixture Data

0. **Create fixture data from production data** (see [`utils/README.md`](utils/README.md)):

- Use `fixture_utils.sh` to download, filter, and package data
- Creates both `fix_{id}_input` and `fix_{id}_pcpip_output` directories
- ⚠️ Output dir MUST be named `{fixture}_pcpip_output` (not just `_output`)

### Phase 2: Configure Test System

1. **Choose fixture type and naming**:

- Pattern: `fix_{size}{number}` (e.g., `fix_s3`, `fix_l2`)
- Size: `s` = small (1-2 images), `l` = large (full plates)
- Decide: local-only (large/proprietary) or remote (shareable)

2.  **Update `fixtures/integration/constants.py`**:

   ```python
   "fix_l2": {
       "local_only": True,  # ⚠️ MUST be True for local-only fixtures
       "channels": {
           "cp_nuclei_channel": "DAPI",
           "cp_cell_channel": "PhalloAF750",
           # ... (copy from similar fixture)
       },
       "input": {
           "dir_name": "fix_l2_input",
           "dataset_dir_name": "Source1",
           # For remote fixtures, also add:
           # "archive_name": "fix_l2_input.tar.gz",
           # "sha256": "abc123...",
           # "dir_prefix": "fix_l2_input_test",
       },
       "output": {
           "dir_name": "fix_l2_pcpip_output",
           "dataset_dir_name": "Source1",  # ⚠️ Must have Source1/ subdirectory
           # For remote fixtures, add archive fields like input
       },
   }
   ```

3.  **Add 5 pytest fixtures to `conftest.py`** (copy existing pattern):

   ```python
   @pytest.fixture(scope="module")
   def fix_l2_input_dir(tmp_path_factory):
       result = _setup_input_dir(tmp_path_factory, "fix_l2")
       yield result

   @pytest.fixture(scope="module")
   def fix_l2_output_dir(tmp_path_factory):
       result = _setup_output_dir(tmp_path_factory, "fix_l2")
       yield result

   @pytest.fixture(scope="function")
   def fix_l2_workspace(tmp_path_factory):
       return _setup_workspace(tmp_path_factory, "fix_l2")

   @pytest.fixture(scope="function")
   def fix_l2_starrynight_generated(fix_l2_workspace, fix_l2_input_dir):
       return _setup_starrynight(fix_l2_workspace, fix_l2_input_dir, "fix_l2", "generated")

   @pytest.fixture(scope="function")
   def fix_l2_starrynight_pregenerated(fix_l2_workspace, fix_l2_input_dir):
       return _setup_starrynight(fix_l2_workspace, fix_l2_input_dir, "fix_l2", "pregenerated")
   ```

4.  **Update `integration/constants.py`** - add to all workflows:

   ```python
   FIXTURE_COMPATIBILITY = {
       "cp_illum_calc": ["fix_s1", "fix_s2", "fix_l1", "fix_l2"],
       "cp_illum_apply": ["fix_s1", "fix_s2", "fix_l1", "fix_l2"],
       # ... add to all 7 workflows
   }
   ```

   ⚠️ Must update ALL 3 places: both constants.py files + parametrize decorator

5.  **Update `test_getting_started_workflow.py`**:

   ```python
   @pytest.mark.parametrize("fixture_id", ["fix_s1", "fix_s2", "fix_l1", "fix_l2"])
   ```

6.  **Deploy fixture data**:

- **Local-only**: Move to `$STARRYNIGHT_TEST_FIXTURE_DIR`
- **Remote**: Create archives, upload to GitHub release, add SHA256 to constants.py

## Fixture Types Explained

### Remote Fixtures (Default)

Use for small, shareable datasets:

```python
"fix_s3": {
    # No local_only flag
    "channels": { ... },
    "input": {
        "archive_name": "fix_s3_input.tar.gz",
        "sha256": "abc123...",  # Required for verification
        "dir_prefix": "fix_s3_input_test",
        "dir_name": "fix_s3_input",
        "dataset_dir_name": "Source1",
    },
}
```

### Local-Only Fixtures

Use for large or proprietary datasets:

```python
"fix_l1": {
    "local_only": True,  # Key difference!
    "channels": { ... },
    "input": {
        "dir_name": "fix_l1_input",  # Only these 2 fields needed
        "dataset_dir_name": "Source1",
    },
}
```

**Key differences**:

- No archive fields needed (no `archive_name`, `sha256`, `dir_prefix`)
- Tests skip automatically in CI (pregenerated mode)
- Fail immediately if `STARRYNIGHT_TEST_FIXTURE_DIR` not set

## Setting Up Fixture Data

### For Local-Only Fixtures

```bash
export STARRYNIGHT_TEST_FIXTURE_DIR=/path/to/fixtures
mkdir -p $STARRYNIGHT_TEST_FIXTURE_DIR/fix_l1_input/Source1
mkdir -p $STARRYNIGHT_TEST_FIXTURE_DIR/fix_l1_pcpip_output/Source1/workspace/load_data_csv

# Copy your data
cp -r /path/to/input/* $STARRYNIGHT_TEST_FIXTURE_DIR/fix_l1_input/Source1/
cp -r /path/to/output/* $STARRYNIGHT_TEST_FIXTURE_DIR/fix_l1_pcpip_output/Source1/
```

### For Remote Fixtures

1. **Find archives** (created by `fixture_utils.sh` in SECTION 6):

- Located in `starrynight/tests/fixtures/archives/`
- Already includes `.sha256` checksum files

2. **Upload to GitHub release**
3. **Add SHA256 to constants.py** (from the `.sha256` files)

### For Pregenerated Files (Remote Fixtures Only)

Pregenerated files (`experiment.json` and `index.parquet`) enable fast test mode (~2s instead of ~30s).
You need to create these files when:

- Setting up a new remote fixture for the first time
- Changing the input data of an existing fixture

To generate them:

1.  Add to `pregenerated_files/regenerate.py`:

   ```python
   @pytest.mark.parametrize("fixture_id", ["fix_s1", "fix_s2", "fix_s3"])  # Add here
   ```

2.  Generate files:

   ```bash
   mkdir -p fixtures/integration/pregenerated_files/fix_s3
   REGENERATE_FIXTURES=1 uv run pytest -xvs fixtures/integration/pregenerated_files/regenerate.py::test_generate_pregenerated_files_files[fix_s3]
   ```

## Testing Your Fixture

```bash
# Test specific fixture + workflow
uv run pytest -xvs tests/integration/test_getting_started_workflow.py::test_complete_workflow[cp_illum_calc-generated-fix_l2]

# Test all workflows with your fixture
uv run pytest -xvs tests/integration/test_getting_started_workflow.py -k "fix_l2"

# For local-only fixtures, set env var first
export STARRYNIGHT_TEST_FIXTURE_DIR=/path/to/fixtures
```

## Using Local Data for Faster Tests

Speed up tests by using local data instead of downloading:

```bash
export STARRYNIGHT_TEST_FIXTURE_DIR=/path/to/fixtures
# Directory must contain: fix_s1_input/, fix_s1_pcpip_output/, etc.
uv run pytest tests/integration/
```

The system checks local first, then falls back to downloading.

## Understanding Test Modes

- **generated**: Runs full CLI workflow (slower, ~30s)
- **pregenerated**: Uses pre-generated experiment.json and index.parquet (faster, ~2s)

Local-only fixtures only support "generated" mode - pregenerated tests are automatically skipped.

## Troubleshooting

### "Fixture not found" error

- Check `STARRYNIGHT_TEST_FIXTURE_DIR` is set and contains your fixture directories
- Verify directory names match exactly (e.g., `fix_l1_input`, not `fix_l1_input_test`)

### Tests skipped for local-only fixture

- This is expected in CI/pregenerated mode
- Local-only fixtures require `STARRYNIGHT_TEST_FIXTURE_DIR` to be set

### SHA256 mismatch for remote fixture

- Update the SHA256 in `constants.py` after creating new archives
- Or redownload if the archive was corrupted

### "Source1 directory not found"

- Ensure your fixture data has the `Source1/` subdirectory structure
- Both input and output directories need this structure
