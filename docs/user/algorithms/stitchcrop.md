# Stitch and Crop (stitchcrop.py) - Technical Documentation

This document provides a detailed explanation of the stitch and crop algorithm implementation in the StarryNight project.

## Overview

The `stitchcrop.py` module implements an algorithm for stitching together multiple microscopy image tiles into a single composite image. This functionality is particularly important for experiments where multiple fields of view (FOVs) are captured for each well, which then need to be reconstructed into a complete, seamless image of the well.

Unlike most other StarryNight algorithms, this module primarily uses Fiji/ImageJ rather than CellProfiler for the core image processing. The module follows a modified three-tier architecture:
1. Load data generation (creating file lists for Fiji processing)
2. Fiji/ImageJ pipeline generation (programmatically constructing ImageJ commands)
3. Pipeline execution (utilizing ImageJ's Python bindings)

## Dependencies

The module relies on several key libraries:
- **ImageJ/Fiji**: Core image processing functionality through the `imagej` Python bridge
- **Polars**: Data manipulation through DataFrames
- **CloudPath**: Path abstraction for local and cloud storage compatibility
- **NumPy**: Array processing for image manipulation
- **StarryNight Utils**: Custom utilities including `ImagejContext` for Fiji integration

## Key Components

### 1. Load Data Generation

#### Main Functions

- `write_loaddata`: Writes CSV headers and data rows for organizing image paths
- `write_loaddata_csv_by_batch_plate_cycle`: Writes load data CSV files organized by batch, plate, and cycle
- `gen_align_load_data_by_batch_plate`: Main entry point for load data generation

#### Data Organization

- Data is organized hierarchically by `batch`, `plate`, and `cycle`
- Each CSV contains metadata columns (Batch, Plate, Site, Well) and file paths for multiple cycles and channels
- The CSV links together all images that need to be stitched for each well

### 2. Fiji/ImageJ Pipeline Generation

#### Main Functions

- `gen_tile_config`: Generates a TileConfiguration.txt file for Fiji's Grid/Collection Stitching plugin
- `get_row_config`: Provides predefined row configurations for different tile layouts
- `stitch_images_fiji`: Orchestrates the stitching process using Fiji's stitching plugin
- `call_grid_stitch_fiji`: Directly calls Fiji's Grid/Collection stitching plugin via PyImageJ

#### Stitching Configuration

Unlike CellProfiler pipelines in other modules, this module directly configures and calls Fiji's stitching functionality:

1. **Tile Configuration**: Creates a text file with position coordinates for each image tile
2. **Grid Layout Determination**: Uses predefined grid configurations based on the number of tiles
3. **Stitching Parameters**: Configures options like overlap percentage, fusion method, and displacement thresholds

### Technical Details

#### Stitching Parameters

- **Tile Overlap**: Default 10% overlap between adjacent tiles
- **Fusion Method**: Linear blending for seamless transitions
- **Regression Threshold**: 0.30 for feature matching
- **Displacement Thresholds**:
  - Max/avg displacement threshold: 2.50
  - Absolute displacement threshold: 3.50
- **Computation Parameters**: "Save computation time (but use more RAM)"
- **Output Type**: Keeps output virtual to minimize memory usage

#### Tile Layout Configuration

The module includes a comprehensive dictionary of predefined row configurations to handle different common tile layouts:
- Supports layouts with varying numbers of tiles per well (52, 88, 256, 293, 316, 320, 394, 1332, 1364, 1396)
- Each configuration specifies the number of tiles in each row to optimize coverage

#### Output File Organization

- Stitched images are saved in the output directory specified during function calls
- The default naming preserves batch, plate, well, and channel information

## Workflow

1. **Data Preparation**:
   - Read the index file containing image metadata
   - Filter for SBS images specifically
   - Group images by hierarchy (batch/plate/cycle)

2. **Load Data Organization**:
   - For each batch/plate combination:
     - Identify all cycles and channels
     - Generate CSV files organizing the tiles to be stitched
     - Write to the output directory

3. **Tile Configuration**:
   - Generate TileConfiguration.txt files containing:
     - Spatial dimensions information
     - File paths for each tile
     - Approximate x,y coordinates for each tile

4. **Grid Layout Determination**:
   - Determine the appropriate row configuration based on the number of tiles
   - Calculate approximate spatial relationships between tiles

5. **Stitching Execution**:
   - Call Fiji's Grid/Collection stitching plugin with the specified parameters
   - Process images using linear blending for seamless fusion
   - Save the resulting stitched image

## Key Classes and Resources

- **PCPIndex**: Manages image metadata and hierarchy
- **ImagejContext**: Context manager for Fiji/ImageJ resources
- **Data Utilities**:
  - `gen_image_hierarchy`: Generates hierarchical organization of images
  - `get_channels_by_batch_plate`: Extracts channel information for a batch/plate
  - `get_cycles_by_batch_plate`: Extracts cycle information for a batch/plate

## Technical Implementation Notes

1. **ImageJ/Fiji Integration**:
   - Uses PyImageJ to bridge Python and ImageJ functionality
   - Directly calls ImageJ plugins through the Python API
   - Parameters are passed as dictionaries to configure plugin behavior

2. **Tile Layout Strategy**:
   - Predefined row configurations optimize the layout for common use cases
   - The module supports various well layouts common in microscopy experiments
   - Row configuration is selected based on the total number of tiles per well

3. **Coordinate Calculation**:
   - Approximate tile coordinates are calculated based on image dimensions
   - The stitching algorithm refines these positions during execution
   - This approach balances initial accuracy with computational refinement

4. **Memory Management**:
   - Output is kept virtual to minimize RAM usage
   - Computation parameters are set to optimize for RAM usage over computation time
   - This approach is necessary as stitched images can be very large

## Conclusion

The stitch and crop module provides functionality for combining multiple microscopy image tiles into seamless composite images. By leveraging Fiji/ImageJ's powerful stitching capabilities through PyImageJ, it enables reconstruction of complete well images from multiple fields of view. The module's predefined layout configurations support a wide range of common microscopy experimental designs, making it adaptable to various imaging workflows.
