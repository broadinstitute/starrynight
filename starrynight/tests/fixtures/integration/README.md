# StarryNight Integration Test Fixtures Guide

## Overview

This guide describes how to create and manage fixtures for integration tests in the StarryNight project. Integration test fixtures provide standardized environments for testing complete workflows and CLI commands. These fixtures use a centralized configuration approach to ensure consistency across all integration tests.

Key components:
- **constants.py**: Single source of truth for fixture configurations
- **../../conftest.py**: Defines pytest fixtures that make test data available
- **pregenerated_files/**: Contains pre-generated files for faster test runs
- **../../integration/constants.py**: Defines fixture compatibility with test workflows

## Step-by-Step Workflow

### Prepare test data using utils scripts

```bash
# Filter a dataset to create smaller test data
python -m starrynight.tests.fixtures.integration.utils.loaddata_filter \
    --input-csv /path/to/original.csv \
    --output-csv /path/to/new_fixture/filtered.csv \
    --well A01 --site 1

# Update paths in the filtered data
python -m starrynight.tests.fixtures.integration.utils.loaddata_postprocess \
    --input-csv /path/to/new_fixture/filtered.csv \
    --output-csv /path/to/new_fixture/processed.csv \
    --source-path /original/path \
    --target-path /new/path

# Validate the processed data
python -m starrynight.tests.fixtures.integration.utils.loaddata_validate \
    --input-csv /path/to/new_fixture/processed.csv
```

### Create archives and calculate hashes

```bash
# Create input archive
tar -czf fix_NEW_input.tar.gz -C /path/to/new_fixture input/

# Create output archive (if applicable)
tar -czf fix_NEW_output.tar.gz -C /path/to/new_fixture output/

# Generate SHA256 hashes
sha256sum fix_NEW_input.tar.gz > fix_NEW_input.tar.gz.sha256
sha256sum fix_NEW_output.tar.gz > fix_NEW_output.tar.gz.sha256
```

###  Upload archives

Upload to the designated release location

### Update constants.py with the new fixture configuration

```python
# Add to FIXTURE_CONFIGS in constants.py
"fix_NEW": {
    # Channel configurations
    "channels": {
        "cp_nuclei_channel": "DAPI",
        "cp_cell_channel": "PhalloAF750",
        "cp_mito_channel": "ZO1AF488",
        "sbs_nuclei_channel": "DAPI",
        "sbs_cell_channel": "PhalloAF750",
        "sbs_mito_channel": "ZO1AF488",
    },
    # Input configuration
    "input": {
        "archive_name": "fix_NEW_input.tar.gz",
        "dir_prefix": "fix_NEW_input_test",
        "dir_name": "fix_NEW_input",
        "dataset_dir_name": "Source1",
        "sha256": "a1b2c3d4e5f6...",  # From fix_NEW_input.tar.gz.sha256
    },
    # Output configuration
    "output": {
        "archive_name": "fix_NEW_output.tar.gz",
        "dir_prefix": "fix_NEW_output_test",
        "dir_name": "fix_NEW_pcpip_output",
        "dataset_dir_name": "Source1",
        "sha256": "f6e5d4c3b2a1...",  # From fix_NEW_output.tar.gz.sha256
    },
}
```

### Register fixtures in conftest.py

Add the following fixture wrapper functions to `conftest.py`:

```python
@pytest.fixture(scope="module")
def fix_NEW_input_dir(tmp_path_factory):
    """Fixture that provides a temporary directory with extracted FIX-NEW input data."""
    result = _setup_input_dir(tmp_path_factory, "fix_NEW")
    yield result
    # Cleanup is handled automatically by pytest's tmp_path_factory

@pytest.fixture(scope="module")
def fix_NEW_output_dir(tmp_path_factory):
    """Fixture that provides a temporary directory with extracted FIX-NEW output data."""
    result = _setup_output_dir(tmp_path_factory, "fix_NEW")
    yield result
    # Cleanup is handled automatically by pytest's tmp_path_factory

@pytest.fixture(scope="function")
def fix_NEW_workspace(tmp_path_factory):
    """Fixture that creates a workspace directory structure for FIX-NEW tests."""
    return _setup_workspace(tmp_path_factory, "fix_NEW")

@pytest.fixture(scope="function")
def fix_NEW_starrynight_generated(fix_NEW_workspace, fix_NEW_input_dir):
    """Fixture for FIX-NEW setup with generated files (via CLI)."""
    return _setup_starrynight(
        fix_NEW_workspace, fix_NEW_input_dir, "fix_NEW", "generated"
    )

@pytest.fixture(scope="function")
def fix_NEW_starrynight_pregenerated(fix_NEW_workspace, fix_NEW_input_dir):
    """Fixture for FIX-NEW setup with pre-generated files."""
    return _setup_starrynight(
        fix_NEW_workspace, fix_NEW_input_dir, "fix_NEW", "pregenerated"
    )
```

### Set up pregenerated files

First, update regenerate.py to include your new fixture:

```python
@pytest.mark.parametrize(
    "fixture_id",
    [
        "fix_s1",
        "fix_s2",
        "fix_NEW",  # Add your new fixture here
    ],
)
```

Then create directory structure:

```bash
mkdir -p pregenerated_files/fix_NEW
```

Next, run regenerate.py to populate fixture files:

```bash
# Run the regeneration script for your specific fixture
REGENERATE_FIXTURES=1 uv run pytest -xvs fixtures/integration/pregenerated_files/regenerate.py::test_generate_pregenerated_files_files[fix_NEW]
```

Finally, verify the generated files exist:
   - `fixtures/integration/pregenerated_files/fix_NEW/experiment.json`
   - `fixtures/integration/pregenerated_files/fix_NEW/index.parquet`

### Update workflow tests

Update integration/constants.py to include your fixture in `FIXTURE_COMPATIBILITY`:

```python
# Add your fixture to compatible tests
FIXTURE_COMPATIBILITY = {
    "cp_illum_calc": ["fix_s1", "fix_s2", "fix_NEW"],
    "cp_illum_apply": ["fix_s1", "fix_s2", "fix_NEW"],
    "cp_segmentation_check": ["fix_s1", "fix_s2", "fix_NEW"],
    "sbs_illum_calc": ["fix_s1", "fix_s2", "fix_NEW"],
    "sbs_illum_apply": ["fix_s1", "fix_s2", "fix_NEW"],
    "sbs_preprocessing": ["fix_s1", "fix_s2", "fix_NEW"],
    "analysis": ["fix_s1", "fix_s2", "fix_NEW"],
}
```

### Verify fixture compatibility with a test run

```bash
# Run a specific test with your new fixture
uv run pytest -v tests/integration/test_getting_started_workflow.py::test_complete_workflow[fix_NEW-generated-cp_illum_calc]
```

Your fixture is now ready for use in tests. You can reference it directly using the fixture names:

```python
# Example: Using your new fixture in a test
def test_with_new_fixture(fix_NEW_starrynight_pregenerated):
    # Test code using the fixture
    ...
```
