# StarryNight Fixture Management Guide

## 1. Overview

StarryNight test fixtures provide standardized test environments for consistent, repeatable testing. Our centralized configuration approach ensures that fixture definitions, generation, and usage remain synchronized.

Key components:
- **constants.py**: Single source of truth for fixture configurations
- **conftest.py**: Defines pytest fixtures that make test data available
- **pregenerated_files/**: Contains pre-generated files for faster test runs
- **integration/constants.py**: Defines fixture compatibility with test workflows

## 2. End-to-End Fixture Creation Process

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ 1. Data Prep    │     │ 2. Configuration │     │ 3. Registration │
│                 │     │                  │     │                 │
│ - Create tar.gz │────▶│ - Update        │────▶│ - Add fixture   │
│ - Generate SHA  │     │   constants.py   │     │   to conftest.py│
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ 6. Use in Tests │     │ 5. Integration  │     │ 4. Pregeneration│
│                 │     │                  │     │                 │
│ - Run tests with│◀────│ - Update        │◀────│ - Update        │
│   new fixture   │     │   compatibility  │     │   regenerate.py │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## 3. Step-by-Step Workflow

### A. Initial Fixture Preparation

1. **Prepare test data** using utils scripts:

```bash
# Filter a dataset to create smaller test data
python -m starrynight.tests.fixtures.utils.loaddata_filter \
    --input /path/to/original.csv \
    --output /path/to/new_fixture/filtered.csv \
    --filter "Well='A01',Site='1'"

# Update paths in the filtered data
python -m starrynight.tests.fixtures.utils.loaddata_postprocess \
    --input /path/to/new_fixture/filtered.csv \
    --output /path/to/new_fixture/processed.csv \
    --update-paths

# Validate the processed data
python -m starrynight.tests.fixtures.utils.loaddata_validate \
    --input /path/to/new_fixture/processed.csv
```

2. **Create archives and calculate hashes**:

```bash
# Create input archive
tar -czf fix_new_input.tar.gz -C /path/to/new_fixture input/

# Create output archive (if applicable)
tar -czf fix_new_output.tar.gz -C /path/to/new_fixture output/

# Generate SHA256 hashes
sha256sum fix_new_input.tar.gz > fix_new_input.tar.gz.sha256
sha256sum fix_new_output.tar.gz > fix_new_output.tar.gz.sha256
```

3. **Upload archives** to the designated release location.

4. **Update constants.py** with the new fixture configuration:

```python
# Add to FIXTURE_CONFIGS in constants.py
"fix_new": {
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
        "archive_name": "fix_new_input.tar.gz",
        "dir_prefix": "fix_new_input_test",
        "dir_name": "fix_new_input",
        "dataset_dir_name": "Source1",
        "sha256": "a1b2c3d4e5f6...",  # From fix_new_input.tar.gz.sha256
    },
    # Output configuration
    "output": {
        "archive_name": "fix_new_output.tar.gz",
        "dir_prefix": "fix_new_output_test",
        "dir_name": "fix_new_pcpip_output",
        "dataset_dir_name": "Source1",
        "sha256": "f6e5d4c3b2a1...",  # From fix_new_output.tar.gz.sha256
    },
}
```

### B. Fixture Registration in conftest.py

Add the following fixture wrapper functions to `conftest.py`:

```python
@pytest.fixture(scope="module")
def fix_new_input_dir(tmp_path_factory):
    """Fixture that provides a temporary directory with extracted FIX-NEW input data."""
    result = _setup_input_dir(tmp_path_factory, "fix_new")
    yield result
    # Cleanup is handled automatically by pytest's tmp_path_factory

@pytest.fixture(scope="module")
def fix_new_output_dir(tmp_path_factory):
    """Fixture that provides a temporary directory with extracted FIX-NEW output data."""
    result = _setup_output_dir(tmp_path_factory, "fix_new")
    yield result
    # Cleanup is handled automatically by pytest's tmp_path_factory

@pytest.fixture(scope="function")
def fix_new_workspace(tmp_path_factory):
    """Fixture that creates a workspace directory structure for FIX-NEW tests."""
    return _setup_workspace(tmp_path_factory, "fix_new")

@pytest.fixture(scope="function")
def fix_new_starrynight_generated(fix_new_workspace, fix_new_input_dir):
    """Fixture for FIX-NEW setup with generated files (via CLI)."""
    return _setup_starrynight(
        fix_new_workspace, fix_new_input_dir, "fix_new", "generated"
    )

@pytest.fixture(scope="function")
def fix_new_starrynight_pregenerated(fix_new_workspace, fix_new_input_dir):
    """Fixture for FIX-NEW setup with pre-generated files."""
    return _setup_starrynight(
        fix_new_workspace, fix_new_input_dir, "fix_new", "pregenerated"
    )
```

### C. Pregenerated Files Setup

1. **Update regenerate.py** to include your new fixture:

```python
@pytest.mark.parametrize(
    "fixture_id",
    [
        "fix_s1",
        "fix_s2",
        "fix_new",  # Add your new fixture here
    ],
)
```

2. **Create directory structure**:

```bash
mkdir -p pregenerated_files/fix_new
```

3. **Run regenerate.py** to populate fixture files:

```bash
# Run the regeneration script for your specific fixture
REGENERATE_FIXTURES=1 uv run pytest -xvs fixtures/pregenerated_files/regenerate.py::test_generate_pregenerated_files_files[fix_new]
```

4. **Verify** the generated files exist:
   - `pregenerated_files/fix_new/experiment.json`
   - `pregenerated_files/fix_new/index.parquet`

### D. Integration with Workflow Tests

1. **Update integration/constants.py** to include your fixture in `FIXTURE_COMPATIBILITY`:

```python
# Add your fixture to compatible tests
FIXTURE_COMPATIBILITY = {
    "cp_illum_calc": ["fix_s1", "fix_s2", "fix_new"],
    "cp_illum_apply": ["fix_s1", "fix_s2", "fix_new"],
    "cp_segmentation_check": ["fix_s1", "fix_s2", "fix_new"],
    "sbs_illum_calc": ["fix_s1", "fix_s2", "fix_new"],
    "sbs_illum_apply": ["fix_s1", "fix_s2", "fix_new"],
    "sbs_preprocessing": ["fix_s1", "fix_s2", "fix_new"],
    "analysis": ["fix_s1", "fix_s2", "fix_new"],
}
```

2. **Verify fixture compatibility** with a test run:

```bash
# Run a specific test with your new fixture
uv run pytest -v tests/integration/test_getting_started_workflow.py::test_complete_workflow[fix_new-generated-cp_illum_calc]
```

Your fixture is now ready for use in tests. You can reference it directly using the fixture names:

```python
# Example: Using your new fixture in a test
def test_with_new_fixture(fix_new_starrynight_pregenerated):
    # Test code using the fixture
    ...
```
