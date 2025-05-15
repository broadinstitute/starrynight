# Test Fixtures

Test data and utilities for the StarryNight project.

## Directory Structure

- `integration/`: Fixtures for integration tests
  - Contains configuration, setup, and utilities for workflow testing
- `stitch_images/`: Test images for unit tests of stitching functionality

## Fixture Types

### Integration Fixtures

The `integration/` directory contains a complete fixture system for testing StarryNight workflows:
- Configuration: `constants.py`
- Setup: `fixture_setup.py`
- Pre-generated files: `pregenerated_files/`
- Utilities: `utils/`

For complete documentation on integration fixtures, see [integration/README.md](integration/README.md).

### Unit Test Fixtures

The `stitch_images/` directory contains sample image data for testing stitching algorithms in isolation.
