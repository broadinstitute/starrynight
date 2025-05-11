# Test Fixtures

This directory contains files used by test fixtures for the StarryNight project.

## Directory Structure

- `basic_setup/`: Pre-generated files for quickly running LoadData tests
  - See [basic_setup/README.md](basic_setup/README.md) for details
- `stitch_images/`: Image files for testing the stitching functionality
  - Various `.tif` files for testing image stitching operations
  - `tile_config.*.txt`: Configuration files for stitching
- `test.cppipe`: Sample CellProfiler pipeline for testing

## Purpose & Usage

### stitch_images/

The images in `stitch_images/` are used for testing image stitching functionality. These are small sample images that can be used to verify that the stitching algorithms work correctly.

### test.cppipe

A sample CellProfiler pipeline file used for testing pipeline parsing and processing.

## Adding New Fixtures

When adding new fixtures:

1. Create a descriptive subdirectory if the fixtures form a logical group
2. Add a README.md in the subdirectory explaining their purpose and generation
3. Update this main README.md with a brief description and link to the subdirectory
4. Prefer small, focused test fixtures over large ones
5. For binary files, include information about their origin and purpose
