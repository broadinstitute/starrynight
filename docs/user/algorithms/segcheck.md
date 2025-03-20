# Segmentation Check (segcheck.py) - Technical Documentation

This document provides a detailed explanation of the segmentation check algorithm implementation in the StarryNight project.

## Overview

The `segcheck.py` module implements an algorithm for validating cell segmentation quality in microscopy images. It performs cell and nuclei segmentation, and generates visualizations that allow researchers to assess segmentation quality before proceeding with full analysis. The module helps identify problematic areas, confluent regions, and overall segmentation performance.

The module follows StarryNight's standard three-tier architecture:
1. Load data generation (creating CSVs for CellProfiler's LoadData module)
2. CellProfiler pipeline generation (programmatically constructing a .cppipe file)
3. Pipeline execution (handled elsewhere)

## Dependencies

The module relies on several key libraries:
- **CellProfiler**: Core image processing functionality through modules like `IdentifyPrimaryObjects`, `IdentifySecondaryObjects`, `MaskImage`, `GrayToColor`, `OverlayOutlines`, and `SaveImages`
- **Polars**: Data manipulation through DataFrames
- **CloudPath**: Path abstraction for local and cloud storage compatibility
- **CellProfiler Core**: Additional functionality for loading data and executing pipelines

## Key Components

### 1. Load Data Generation

#### Main Functions

- `write_loaddata`: Writes CSV headers and data rows for CellProfiler's LoadData module
- `write_loaddata_csv_by_batch_plate`: Writes load data CSV files organized by batch and plate
- `write_loaddata_csv_by_batch_plate_cycle`: Writes load data CSV files organized by batch, plate, and cycle
- `gen_segcheck_load_data_by_batch_plate`: Main entry point for load data generation

#### Data Organization

- Data is organized hierarchically by `batch`, `plate`, and optionally `cycle`
- Each CSV contains metadata columns (Batch, Plate, Site, Well, Cycle)
- File information focuses specifically on nuclei and cell channels required for segmentation
- A sampling approach (10% by default) is used to reduce computation for large datasets

### 2. CellProfiler Pipeline Generation

#### Main Functions

- `generate_segcheck_pipeline`: Creates a CellProfiler pipeline for segmentation validation
- `gen_segcheck_cppipe_by_batch_plate`: Writes pipeline files for each batch/plate combination

#### Pipeline Structure

The pipeline creates a sequence of modules that:

1. **LoadData**: Loads corrected images specified in the CSV file
2. **IdentifyPrimaryObjects (ConfluentRegions)**: Identifies large confluent regions in the nuclei channel
   - Uses Otsu thresholding with a correction factor of 0.5
   - Size range: 500-5000 pixels
   - Intensity-based declumping without watershed
3. **MaskImage**: Creates masked versions of all channels using the identified confluent regions
   - Inverted mask to focus on non-confluent areas
   - Applied to each channel in the dataset
4. **IdentifyPrimaryObjects (Nuclei)**: Identifies nuclei in the nuclei channel
   - Uses Otsu thresholding
   - Size range: 10-80 pixels
   - Shape-based declumping and watershed
5. **IdentifySecondaryObjects (Cells)**: Expands from nuclei to identify cell boundaries
   - Uses intensity watershed on the masked cell channel
   - Otsu three-class thresholding with background assignment
   - Threshold correction factor of 0.7
6. **RescaleIntensity**: Normalizes image intensities for visualization
   - Applied to each masked channel
   - Sets consistent intensity range for display
7. **GrayToColor**: Combines channels into an RGB visualization
   - Nuclei channel in red and blue (appears magenta)
   - Cell channel in green
8. **OverlayOutlines**: Adds object outlines to the color image
   - Nuclei outlines in blue
   - Cell outlines in white
   - Confluent region outlines in orange
9. **SaveImages**: Saves the overlay visualization for quality assessment
10. **ExportToSpreadsheet**: Exports segmentation metrics for quantitative evaluation

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
  - Three-class Otsu with background assignment to middle intensity

- **Visualization**:
  - RGB color scheme with nuclei in magenta, cells in green
  - Three different outlines in contrasting colors
  - 16-bit TIFF format for high-quality assessment

#### File Naming and Organization

- Input files are expected to follow the pattern: `[Batch]_[Plate]_Well_[Well]_Site_[Site]_Corr[Channel].tiff`
- Output visualization files follow similar naming with "_OrigOverlay" suffix
- Measurement files are prefixed with "Segcheck_"
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
     - Identify nuclei and cell channels
     - Generate a CSV file with paths to corrected images
     - Write to the output directory

3. **Pipeline Generation**:
   - For each generated CSV file:
     - Create a CellProfiler pipeline
     - Configure modules for segmentation and visualization
     - Set up visualization and measurement export
     - Save the pipeline to a .cppipe file

4. **Pipeline Execution**:
   - Pipelines are executed separately (not covered in this module)
   - Overlay visualizations are saved as TIFF files
   - Segmentation measurements are saved as CSV files

## Key Classes and Resources

- **PCPIndex**: Manages image metadata and hierarchy
- **CellProfilerContext**: Context manager for CellProfiler resources
- **CellProfiler Modules**:
  - `IdentifyPrimaryObjects`: Used for both confluent region and nuclei detection
  - `IdentifySecondaryObjects`: Used for cell detection
  - `MaskImage`: Creates masked versions of channels using identified regions
  - `RescaleIntensity`: Normalizes image intensities for visualization
  - `GrayToColor`: Creates RGB visualizations from grayscale channels
  - `OverlayOutlines`: Adds colored outlines to visualizations
  - `SaveImages`: Saves visualization images
  - `ExportToSpreadsheet`: Exports segmentation metrics

## Technical Implementation Notes

1. **Sampling Strategy**:
   - The algorithm processes a subset (10%) of available sites
   - This reduces computational load while providing sufficient data for quality assessment
   - Only applies sampling when the dataset contains more than 10 images

2. **Visualization Focus**:
   - Unlike the pre-segmentation check, segcheck puts significant emphasis on visualization
   - Creates color-coded overlays showing all detected objects simultaneously
   - These visualizations are crucial for manually assessing segmentation quality

3. **RGB Composition**:
   - Uses the nuclei channel in both red and blue color channels (creating magenta)
   - Uses the cell channel for green
   - This color scheme provides good contrast between nuclei and cell boundaries

4. **Multi-level Quality Assessment**:
   - Identifies and visualizes three levels of objects: confluent regions, nuclei, and cells
   - This hierarchy helps identify different types of segmentation problems:
     - Large confluent regions where individual cells can't be separated
     - Issues with nuclei detection, which affects downstream cell segmentation
     - Problems with cell boundary detection

## Conclusion

The segmentation check module provides a critical quality control step in the StarryNight workflow. By leveraging CellProfiler's segmentation and visualization capabilities, it identifies cells, nuclei, and confluent regions and presents them in an easy-to-assess visualization. This allows researchers to validate segmentation quality before proceeding with full analysis, potentially saving significant time by identifying problematic images or segmentation issues early in the workflow.
