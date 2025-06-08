# StarryNight Integration Test Fixtures Guide

## Overview

This guide describes how to create and manage fixtures for integration tests in the StarryNight project. Integration test fixtures provide standardized environments for testing complete workflows and CLI commands. These fixtures use a centralized configuration approach to ensure consistency across all integration tests.

Key components:
- **constants.py**: Single source of truth for fixture configurations
- **fixture_setup.py**: Core fixture loading logic with local/remote support
- **../../conftest.py**: Defines pytest fixtures that make test data available
- **pregenerated_files/**: Contains pre-generated files for faster test runs
- **../../integration/constants.py**: Defines fixture compatibility with test workflows

## Using Local Fixtures

By default, test fixtures are downloaded and cached using pooch. For large datasets or faster test runs, you can use local unarchived fixtures by setting the `STARRYNIGHT_TEST_FIXTURE_DIR` environment variable.

### Setup

1. Set the environment variable to point to your local fixture directory:
   ```bash
   export STARRYNIGHT_TEST_FIXTURE_DIR=/path/to/your/fixtures
   ```

2. Ensure your local fixture directory contains the expected subdirectories:
   - `fix_s1_input/` - Input data for fix_s1 tests
   - `fix_s1_pcpip_output/` - Output data for fix_s1 tests
   - (Additional fixtures as needed)

3. Run tests as usual:
   ```bash
   uv run pytest starrynight/tests/
   ```

### Example

```bash
# Use local fixtures from scratch directory
export STARRYNIGHT_TEST_FIXTURE_DIR=/Users/shsingh/Documents/GitHub/starrynight/scratch
uv run pytest starrynight/tests/integration/

# Or for a single test run
STARRYNIGHT_TEST_FIXTURE_DIR=/path/to/fixtures uv run pytest starrynight/tests/integration/test_getting_started_workflow.py
```

### Notes

- The local directory structure must match what would be extracted from the archives
- Validation checks ensure the expected files and directories exist
- If a fixture is not found locally, the system falls back to pooch download

## Understanding fixture_setup.py

### Key Functions

1. **`_get_fixture_from_local_or_pooch()`**
   - Main orchestrator function
   - Parameters:
     - `fixture_id`: Which fixture to load (e.g., "fix_s1")
     - `fixture_type`: "input" or "output"
     - `validate_func`: Function to validate directory structure
     - `build_paths_func`: Function to build return dictionary
   - Returns: Dictionary with paths (e.g., `{"base_dir": Path, "input_dir": Path}`)

2. **`_setup_input_dir()` and `_setup_output_dir()`**
   - High-level functions called by pytest fixtures
   - Delegate to `_get_fixture_from_local_or_pooch()` with appropriate validators

3. **Validation Functions**
   - `_validate_input_dir()`: Ensures dataset directory and image files exist
   - `_validate_output_dir()`: Ensures workspace and LoadData CSV files exist

4. **Path Building Functions**
   - `_build_input_paths()`: Returns `{"base_dir", "input_dir"}`
   - `_build_output_paths()`: Returns `{"base_dir", "output_dir", "workspace_dir", "load_data_csv_dir"}`

### Adding New Fixture Types

To add a new fixture type (e.g., "model" fixtures):

Currently, the fixture system supports two main types:
- `input`: Raw microscopy data and metadata for processing
- `output`: Reference results from previous pipeline runs (LoadData CSVs, workspace structure)

These generic types work well for the current testing needs, but you might want to add more specific fixture types in the future (e.g., "model" for trained models, "reference" for benchmark datasets, "config" for different experimental setups).

```python
def _validate_model_dir(model_dir: Path, model_config: dict) -> None:
    """Validate model directory structure."""
    # Add your validation logic
    pass

def _build_model_paths(base_dir: Path, model_config: dict) -> dict[str, Path]:
    """Build paths for model fixtures."""
    model_dir = base_dir / model_config["dir_name"]
    return {"base_dir": base_dir, "model_dir": model_dir}

def _setup_model_dir(tmp_path_factory, fixture_id: str) -> dict[str, Path]:
    """Set up model directory from local or remote source."""
    return _get_fixture_from_local_or_pooch(
        tmp_path_factory,
        fixture_id,
        "model",  # Add "model" config to FIXTURE_CONFIGS
        _validate_model_dir,
        _build_model_paths,
    )
```

## Step-by-Step Workflow

### Prepare test data using utils scripts

The `fixture_utils.sh` script in the `utils/` directory automates the fixture creation process. It downloads required data, filters datasets to manageable sizes, updates file paths for the test environment, validates data integrity, and handles archive creation with checksums.

> **IMPORTANT**: You should manually inspect and edit `fixture_utils.sh` before running it, as it contains hardcoded paths and lacks robust error checking. Edit the FIXTURE_ID variable (currently set to "s1") and other configuration variables at the top of the script to match your requirements.

For fixture preparation (assuming we're creating a fixture called "NEW"), the script produces:

- Filtered datasets with only required wells and sites
- LoadData CSV files with updated paths appropriate for testing
- Input and output archives with SHA256 checksums

The archives created will be:
- `fix_NEW_input.tar.gz` and `fix_NEW_input.tar.gz.sha256`
- `fix_NEW_output.tar.gz` and `fix_NEW_output.tar.gz.sha256`

###  Upload archives

Upload to the designated release location

### Update constants.py with the new fixture configuration

```python
# Add to FIXTURE_CONFIGS in constants.py
"fix_NEW": {
    # Channel configurations; this will vary across datasets
    "channels": {
        "cp_nuclei_channel": "DAPI",
        "cp_cell_channel": "PhalloAF750",
        "cp_mito_channel": "ZO1AF488",
        "sbs_nuclei_channel": "DAPI",
        "sbs_cell_channel": "PhalloAF750",
        "sbs_mito_channel": "ZO1AF488",
        "cp_custom_channel_map": {
            "DAPI": "DNA",
            "ZO1AF488": "ZO1",
            "PhalloAF750": "Phalloidin",
        },
        "sbs_custom_channel_map": {
            "DAPI": "DNA",
            "A": "A",
            "T": "T",
            "G": "G",
            "C": "C",
        }
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

This step is ONLY needed in the following cases:
- When creating a new fixture
- When input data paths have changed
- When `FIXTURE_CONFIGS` in `constants.py` has been updated affecting input configurations

Skip this entire section when only updating output archives.

First, update `regenerate.py` to include your new fixture:

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

Next, run `regenerate.py` to populate fixture files:

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
