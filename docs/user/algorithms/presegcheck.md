# Pre-Segmentation Check (presegcheck.py) - Technical Documentation

This document provides a detailed explanation of the pre-segmentation check algorithm implementation in the StarryNight project.

## Overview

The `presegcheck.py` module implements an algorithm for assessing image quality and segmentation feasibility prior to full image analysis. It identifies confluent regions, nuclei, and cells to evaluate whether images are suitable for downstream segmentation and analysis.

The module follows StarryNight's standard three-tier architecture:
1. Load data generation (creating CSVs for CellProfiler's LoadData module)
2. CellProfiler pipeline generation (programmatically constructing a .cppipe file)
3. Pipeline execution (handled elsewhere)

## Dependencies

The module relies on several key libraries:
- **CellProfiler**: Core image processing functionality through modules like `IdentifyPrimaryObjects`, `IdentifySecondaryObjects`, `MaskImage`, and `ExportToSpreadsheet`
- **Polars**: Data manipulation through DataFrames
- **CloudPath**: Path abstraction for local and cloud storage compatibility
- **CellProfiler Core**: Additional functionality for loading data and executing pipelines

## Key Components

### 1. Load Data Generation

#### Main Functions

- `write_loaddata`: Writes CSV headers and data rows for CellProfiler's LoadData module
- `write_loaddata_csv_by_batch_plate`: Writes load data CSV files organized by batch and plate
- `write_loaddata_csv_by_batch_plate_cycle`: Writes load data CSV files organized by batch, plate, and cycle
- `gen_pre_segcheck_load_data_by_batch_plate`: Main entry point for load data generation

#### Data Organization

- Data is organized hierarchically by `batch`, `plate`, and optionally `cycle`
- Each CSV contains metadata columns (Batch, Plate, Site, Well, Cycle) and file information for corrected images
- A sampling approach (10% by default) is used to reduce computation for large datasets
- The CSV structure includes FileName and PathName columns for each channel

### 2. CellProfiler Pipeline Generation

#### Main Functions

- `generate_pre_segcheck_pipeline`: Creates a CellProfiler pipeline for pre-segmentation checks
- `gen_pre_segcheck_cppipe_by_batch_plate`: Writes pipeline files for each batch/plate combination

#### Pipeline Structure

The pipeline creates a sequence of modules that:

1. **LoadData**: Loads corrected images specified in the CSV file
2. **IdentifyPrimaryObjects (ConfluentRegions)**: Identifies large confluent regions in the nuclei channel
   - Uses Otsu thresholding with a correction factor of 0.5
   - Size range: 500-5000 pixels
   - Intensity-based declumping without watershed
3. **MaskImage**: Creates masked versions of all channels using the identified confluent regions
   - Inverted mask to focus on non-confluent areas
   - Applied to all channels in the dataset
4. **IdentifyPrimaryObjects (Nuclei)**: Identifies nuclei in the nuclei channel
   - Uses Otsu thresholding
   - Size range: 10-80 pixels
   - Shape-based declumping and watershed
5. **IdentifySecondaryObjects (Cells)**: Expands from nuclei to identify cell boundaries
   - Uses intensity watershed on the masked cell channel
   - Otsu three-class thresholding with background assignment
   - Threshold correction factor of 0.7
6. **ExportToSpreadsheet**: Exports object counts and measurements for quality assessment

### Technical Details

#### Key Parameters

- **Confluent Region Detection**:
  - Size range: 500-5000 pixels
  - Threshold correction factor: 0.5
  - Fill holes during declumping

- **Nuclei Detection**:
  - Size range: 10-80 pixels
  - Smoothing filter size: 8
  - Maxima suppression size: 8.0
  - Shape-based declumping and watershed

- **Cell Detection**:
  - Method: Intensity watershed
  - Threshold correction factor: 0.7
  - Three-class Otsu with background assignment

#### File Naming and Organization

- Input files are expected to follow the pattern: `[Batch]_[Plate]_Well_[Well]_Site_[Site]_Corr[Channel].tiff`
- Output CSV files are named with the prefix "PreSegcheck_"
- Pipeline files are named to match their corresponding load data files

#### SBS vs. Non-SBS Images

The module handles two types of image sets:
- **Non-SBS images**: Standard images organized by batch and plate
- **SBS images**: Sequential (cycle-based) images organized by batch, plate, and cycle

## Workflow

1. **Data Preparation**:
   - Read the index file containing image metadata
   - Filter for relevant images (SBS or non-SBS)
   - Sample a subset (10%) of sites to reduce computational load
   - Group images by hierarchy (batch/plate/cycle)

2. **Load Data Generation**:
   - For each batch/plate combination (or batch/plate/cycle for SBS):
     - Identify available channels
     - Generate a CSV file with paths to corrected images
     - Write to the output directory

3. **Pipeline Generation**:
   - For each generated CSV file:
     - Create a CellProfiler pipeline
     - Configure modules for confluent region detection
     - Configure modules for nuclei and cell identification
     - Set up measurement export
     - Save the pipeline to a .cppipe file

4. **Pipeline Execution**:
   - Pipelines are executed separately (not covered in this module)
   - Measurements are saved as CSV files with the prefix "PreSegcheck_"
   - These measurements can be used to assess segmentation feasibility

## Key Classes and Resources

- **PCPIndex**: Manages image metadata and hierarchy
- **CellProfilerContext**: Context manager for CellProfiler resources
- **CellProfiler Modules**:
  - `IdentifyPrimaryObjects`: Used for both confluent region and nuclei detection
  - `IdentifySecondaryObjects`: Used for cell detection
  - `MaskImage`: Creates masked versions of channels using identified regions
  - `ExportToSpreadsheet`: Exports measurements for quality assessment
- **Data Utilities**:
  - `gen_image_hierarchy`: Generates hierarchical organization of images
  - `get_channels_by_batch_plate`: Extracts channel information for a batch/plate
  - `get_cycles_by_batch_plate`: Extracts cycle information for a batch/plate

## Technical Implementation Notes

1. **Sampling Strategy**:
   - The algorithm processes a subset (10%) of available sites
   - This reduces computational load while providing sufficient data for quality assessment
   - Only applies sampling when the dataset contains more than 10 images

2. **Masking Approach**:
   - Confluent regions are identified and excluded via masking
   - This focuses cell detection on areas with well-separated cells
   - The masking is applied with inversion to focus on non-confluent areas

3. **Different Channel Roles**:
   - The nuclei channel (typically DAPI) is used for both confluent region and nuclei detection
   - A separate cell channel is used for cell boundary detection
   - Both channels must be specified when generating the pipeline

4. **Hierarchy-Aware Processing**:
   - The algorithm handles different organizational hierarchies based on image type
   - For standard images: batch/plate organization
   - For SBS images: batch/plate/cycle organization

## Conclusion

The pre-segmentation check module provides a critical quality control step in the StarryNight workflow. By leveraging CellProfiler's segmentation capabilities, it identifies confluent regions, nuclei, and cells to assess whether images are suitable for downstream analysis. The resulting measurements help identify problematic images or samples that might need exclusion or special handling before proceeding to full analysis.
