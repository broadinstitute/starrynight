# StarryNight Integration Test Fixtures Guide

## Quick Start: Adding a New Fixture

### 6-Step Checklist

1. **Choose fixture type and naming**:

- Pattern: `fix_{size}{number}` (e.g., `fix_s3`, `fix_l2`)
- Size: `s` = small (1-2 images), `l` = large (full plates)
- Decide: local-only (large/proprietary) or remote (shareable)

2.  **Update `fixtures/integration/constants.py`**:

   ```python
   "fix_l2": {
       "local_only": True,  # Set True for local-only fixtures
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
           "dir_name": "fix_l2_pcpip_output",  # MUST use _pcpip_output suffix!
           "dataset_dir_name": "Source1",
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

5.  **Update `test_getting_started_workflow.py`**:

   ```python
   @pytest.mark.parametrize("fixture_id", ["fix_s1", "fix_s2", "fix_l1", "fix_l2"])
   ```

6.  **Set up fixture data**:

- **Local-only**: Create directories under `$STARRYNIGHT_TEST_FIXTURE_DIR`
- **Remote**: Create archives, upload to GitHub release, add SHA256

### Common Pitfalls

⚠️ **MUST FIX**:

- Output dir MUST be named `{fixture}_pcpip_output` (not just `_output`)
- Must have `Source1/` subdirectory under both input and output
- Must update ALL 3 places: constants.py (both files) + parametrize decorator
- Local-only fixtures MUST have `"local_only": True`

## Overview

Test fixtures provide standardized data for integration tests. The system supports:

- **Remote fixtures** (fix_s1, fix_s2): Downloaded from GitHub releases, cached locally
- **Local-only fixtures** (fix_l1): Never downloaded, must exist locally

Key files:

- `fixtures/integration/constants.py` - Fixture configurations
- `conftest.py` - Pytest fixture definitions
- `integration/constants.py` - Test compatibility matrix
- `test_getting_started_workflow.py` - Main integration tests

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
cp -r /path/to/images/* $STARRYNIGHT_TEST_FIXTURE_DIR/fix_l1_input/Source1/
cp -r /path/to/output/* $STARRYNIGHT_TEST_FIXTURE_DIR/fix_l1_pcpip_output/Source1/
```

### For Remote Fixtures

1.  **Prepare data** (use `utils/fixture_utils.sh` as template)
2.  **Create archives**:

   ```bash
   tar -czf fix_s3_input.tar.gz fix_s3_input/
   tar -czf fix_s3_output.tar.gz fix_s3_pcpip_output/
   shasum -a 256 fix_s3_input.tar.gz > fix_s3_input.tar.gz.sha256
   shasum -a 256 fix_s3_output.tar.gz > fix_s3_output.tar.gz.sha256
   ```

3.  **Upload to GitHub release**
4.  **Add SHA256 to constants.py**

### For Pregenerated Files (Remote Fixtures Only)

Only needed when creating new fixtures or changing input data:

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
