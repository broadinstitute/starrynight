# Test Fixtures

This directory contains files used by test fixtures for the StarryNight project.

## Directory Structure

- `basic_setup/`: Pre-generated files for quickly running LoadData tests
  - See [basic_setup/README.md](basic_setup/README.md) for details
- `stitch_images/`: Image files for testing the stitching functionality
  - See [stitch_images/README.md](stitch_images/README.md) for details

## Adding New Fixtures

When adding new fixtures:

1. Create a descriptive subdirectory if the fixtures form a logical group
2. Add a README.md in the subdirectory explaining their purpose and generation
3. Update this main README.md with a brief description and link to the subdirectory
4. Prefer small, focused test fixtures over large ones
5. For binary files, include information about their origin and purpose
