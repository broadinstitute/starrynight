# Illumination Apply (illum_apply.py) - Technical Documentation

This document provides a detailed explanation of the illumination apply algorithm implementation in the StarryNight project.

## Overview

The `illum_apply.py` module implements an algorithm for applying previously calculated illumination correction functions to microscopy images. This process normalizes uneven illumination across images, ensuring consistent intensity profiles that improve downstream analysis accuracy.

The module follows StarryNight's standard three-tier architecture:
1. Load data generation
2. CellProfiler pipeline generation
3. Pipeline execution (handled elsewhere)

## Dependencies

The module relies on several key libraries:
- **CellProfiler**: Core image processing functionality through modules like `CorrectIlluminationApply` and `SaveImages`
- **Polars**: Data manipulation through DataFrames
- **CloudPath**: Path abstraction for local and cloud storage compatibility
- **centrosome**: Background compensation functionality with `MODE_AUTO`

## Key Components

### 1. Load Data Generation

#### Main Functions

- `write_loaddata`: Writes CSV headers and data rows for CellProfiler's LoadData module
- `write_loaddata_csv_by_batch_plate`: Writes load data CSV files organized by batch and plate
- `write_loaddata_csv_by_batch_plate_cycle`: Writes load data CSV files organized by batch, plate, and cycle
- `gen_illum_apply_load_data_by_batch_plate`: Main entry point for load data generation

#### Data Organization

- Data is organized hierarchically by `batch`, `plate`, and optionally `cycle`
- Each CSV contains metadata columns (Batch, Plate, Site, Well, Cycle) plus:
  - Original image paths and channel information
  - Illumination function paths for each channel
- The CSV links each input image with its corresponding illumination function

### 2. CellProfiler Pipeline Generation

#### Main Functions

- `generate_illum_apply_pipeline`: Creates a CellProfiler pipeline for illumination application
- `gen_illum_apply_cppipe_by_batch_plate`: Writes pipeline files for each batch/plate combination

#### Pipeline Structure

The pipeline consists of a sequence of modules that:
1. **LoadData**: Loads both original images and illumination functions using the CSV specification
2. **CorrectIlluminationApply**: Applies illumination correction to each channel using division method
3. **SaveImages**: Saves corrected images with appropriate names

### Technical Details

#### Illumination Application Method

- The module uses division-based correction (DOS_DIVIDE) to normalize illumination
- This divides the original image intensity by the illumination function values
- Division is preferred for fluorescence microscopy where illumination has a multiplicative effect

#### File Naming and Organization

- Corrected images are named following the pattern: `[Batch]_[Plate]_Well_[Well]_Site_[Site]_[Channel]Corr`
- For SBS images: `[Batch]_[Plate]_[Cycle]_Well_[Well]_Site_[Site]_[Channel]Corr`
- Images are saved as 16-bit TIFF files to preserve precision

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
     - Identify corresponding illumination function files
     - Generate a CSV file linking images with their illumination functions
     - Write to the output directory

3. **Pipeline Generation**:
   - For each generated CSV file:
     - Create a CellProfiler pipeline
     - Configure the LoadData module to read both images and illumination functions
     - Add CorrectIlluminationApply module for each channel
     - Configure SaveImages module for each corrected channel
     - Save the pipeline to a .cppipe file

4. **Execution**:
   - Pipelines are executed separately (not covered in this module)
   - Corrected images are saved as TIFF files

## Key Classes and Resources

- **PCPIndex**: Manages image metadata and hierarchy
- **CellProfilerContext**: Context manager for CellProfiler resources
- **Data Utilities**:
  - `gen_image_hierarchy`: Generates hierarchical organization of images
  - `get_channels_by_batch_plate`: Extracts channel information for a batch/plate
  - `get_cycles_by_batch_plate`: Extracts cycle information for a batch/plate

## Technical Implementation Notes

1. **File Organization**:
   - Output files are organized in a hierarchical directory structure (batch/plate/cycle)
   - The structure matches the input organization for easy traceability

2. **Efficient Processing**:
   - Images are processed in batch/plate groups for efficient parallel execution
   - This allows distribution across compute resources for large datasets

3. **Path Handling**:
   - `CloudPath` abstraction enables working with both local and cloud storage
   - Path resolution is handled carefully to ensure CellProfiler can access all files

4. **Context Management**:
   - CellProfilerContext is used to manage resources and ensure proper cleanup

## Conclusion

The illumination apply module provides an efficient system for applying illumination correction to microscopy images. By separating the illumination function calculation from its application, StarryNight enables a modular workflow where correction functions can be calculated once and applied to multiple image sets. The module handles both standard and sequential (SBS) imaging protocols, applying the appropriate illumination functions based on metadata.
