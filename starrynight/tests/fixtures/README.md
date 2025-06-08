# Test Fixtures

Test data and utilities for the StarryNight project.

## Directory Structure

- `integration/`: Fixtures for integration tests
  - Contains configuration, setup, and utilities for workflow testing
- `stitch_images/`: Test images for unit tests of stitching functionality

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
   uv run pytest
   ```

### Example

```bash
# Use local fixtures from scratch directory
export STARRYNIGHT_TEST_FIXTURE_DIR=/Users/shsingh/Documents/GitHub/starrynight/scratch
uv run pytest starrynight/tests/integration/

# Or for a single test run
STARRYNIGHT_TEST_FIXTURE_DIR=/path/to/fixtures uv run pytest starrynight/tests/integration/test_getting_started_workflow.py
```

### Benefits

- **Speed**: No download/extraction overhead for large fixtures
- **Development**: Use custom or modified fixtures for testing
- **CI/CD**: Pre-stage fixtures on build servers for faster test runs

### Notes

- The local directory structure must match what would be extracted from the archives
- Validation checks ensure the expected files and directories exist
- If a fixture is not found locally, the system falls back to pooch download
