# Stitch Images Fixtures

This directory contains test images for the stitching functionality in StarryNight.

## Files

- Various `.tif` files (1.tif, 2.tif, etc.): Individual tiles for stitching tests
- `Fused-with compute overlap.tif`, `Fused-without compute.tif`, `fused.tiff`: Expected results after stitching
- `tile_config.txt`, `tile_config.registered.txt`: Configuration files for the stitching process

## Purpose

These small sample images are used to verify that the stitching algorithms work correctly. They provide a consistent set of inputs for testing the image stitching functionality without requiring large image datasets.

## Usage

These files are primarily used in stitching-related tests, such as in `/starrynight/tests/utils/test_stitching.py`. The tests verify that:

1. Individual tiles can be correctly stitched together
2. The stitching algorithm produces expected output
3. Configuration files are properly parsed and utilized

## Image Properties

The test images are intentionally small to keep test execution fast while still providing sufficient complexity for testing stitching algorithms.
