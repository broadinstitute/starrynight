# Illumination Calculation (illum_calc.py) - Technical Documentation

This document provides a detailed explanation of the illumination calculation algorithm implementation in the StarryNight project.

## Overview

The `illum_calc.py` module implements an algorithm for calculating illumination correction functions for microscopy images. Illumination correction is a critical preprocessing step in microscopy image analysis that helps normalize uneven illumination patterns across images, improving downstream analysis.

The module follows StarryNight's standard three-tier architecture:
1. Load data generation
2. CellProfiler pipeline generation
3. Pipeline execution (handled elsewhere)

## Dependencies

The module relies on several key libraries:
- **CellProfiler**: Core image processing functionality through modules like `CorrectIlluminationCalculate`, `Resize`, and `SaveImages`
- **Polars**: Data manipulation through DataFrames
- **CloudPath**: Path abstraction for local and cloud storage compatibility
- **centrosome**: Background compensation functionality

## Key Components

### 1. Load Data Generation

#### Main Functions

- `write_loaddata`: Writes CSV headers and data rows for CellProfiler's LoadData module
- `write_loaddata_csv_by_batch_plate`: Writes load data CSV files organized by batch and plate
- `write_loaddata_csv_by_batch_plate_cycle`: Writes load data CSV files organized by batch, plate, and cycle
- `gen_illum_calc_load_data_by_batch_plate`: Main entry point for load data generation

#### Data Organization

- Data is organized hierarchically by `batch`, `plate`, and optionally `cycle`
- Each CSV contains metadata columns (Batch, Plate, Site, Well, Cycle) and file information (FileName, Frame, PathName) for each channel

### 2. CellProfiler Pipeline Generation

#### Main Functions

- `generate_illum_calculate_pipeline`: Creates a CellProfiler pipeline for illumination calculation
- `gen_illum_calculate_cppipe_by_batch_plate`: Writes pipeline files for each batch/plate combination

#### Pipeline Structure

For each channel, the pipeline creates a sequence of modules:
1. **LoadData**: Loads images based on the CSV specification
2. **Resize (downsampling)**: Reduces image size to improve processing speed (by factor 0.25)
3. **CorrectIlluminationCalculate**: Calculates the illumination function using median filtering
4. **Resize (upsampling)**: Increases illumination function size back to original (by factor 4)
5. **SaveImages**: Saves the calculated illumination functions as .npy files

### Technical Details

#### Illumination Calculation Parameters

The illumination calculation uses a median filter approach with these key parameters:
- Block size: 60
- Smoothing method: Median filter
- Object width: 10
- Smoothing filter size: 20
- Intensity choice: Regular

#### File Naming and Organization

- Illumination function files are named using batch, plate, and optional cycle information
- For example: `Batch1_PlateA_IllumDAPI.npy` or `Batch1_PlateA_01_IllumDAPI.npy` (for SBS images)

#### SBS vs. Non-SBS Images

The module handles two types of image sets:
- **Non-SBS images**: Standard images organized by batch and plate
- **SBS images**: Sequential (cycle-based) images organized by batch, plate, and cycle

## Workflow

1. **Data Preparation**:
   - Read the index file containing image metadata
   - Filter for relevant images (SBS or non-SBS)
   - Group images by hierarchy (batch/plate/cycle)

2. **Load Data Generation**:
   - For each batch/plate combination (or batch/plate/cycle for SBS):
     - Filter the relevant images
     - Generate a CSV file with image paths and metadata
     - Write to the output directory

3. **Pipeline Generation**:
   - For each generated CSV file:
     - Create a CellProfiler pipeline
     - Configure the LoadData module to read the CSV
     - Add image processing modules for each channel
     - Save the pipeline to a .cppipe file

4. **Execution**:
   - Pipelines are executed separately (not covered in this module)
   - Illumination functions are saved as .npy files

## Key Classes and Resources

- **PCPIndex**: Manages image metadata and hierarchy
- **CellProfilerContext**: Context manager for CellProfiler resources
- **Data Utilities**:
  - `gen_image_hierarchy`: Generates hierarchical organization of images
  - `get_channels_by_batch_plate`: Extracts channel information for a batch/plate
  - `get_cycles_by_batch_plate`: Extracts cycle information for a batch/plate

## Technical Implementation Notes

1. **Downsampling and Upsampling**:
   - Images are downsampled before illumination calculation to improve performance
   - The resulting illumination functions are upsampled to match the original image size

2. **Bilinear Interpolation**:
   - Used for both downsampling and upsampling to preserve smooth gradients

3. **File Storage**:
   - Illumination functions are saved as NumPy (.npy) files for efficient storage and loading

4. **Context Management**:
   - CellProfilerContext is used to manage resources and ensure proper cleanup

## Conclusion

The illumination calculation module provides a robust, scalable solution for generating illumination correction functions from microscopy images. By leveraging CellProfiler's image processing capabilities and StarryNight's hierarchical data organization, it enables efficient batch processing of large image datasets, supporting both standard and sequential (SBS) imaging protocols.
