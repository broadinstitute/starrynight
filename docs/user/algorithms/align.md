# Image Alignment (align.py) - Technical Documentation

This document provides a detailed explanation of the image alignment algorithm implementation in the StarryNight project.

## Overview

The `align.py` module implements an algorithm for registering images across different cycles in sequencing-based imaging (SBS) experiments. Accurate alignment is critical for applications like optical pooled screening, where cells must be precisely tracked across multiple imaging cycles.

The module follows StarryNight's standard three-tier architecture:
1. Load data generation
2. CellProfiler pipeline generation
3. Pipeline execution (handled elsewhere)

## Dependencies

The module relies on several key libraries:
- **CellProfiler**: Core image processing functionality through modules like `Align`, `MeasureColocalization`, and `FlagImage`
- **Polars**: Data manipulation through DataFrames
- **CloudPath**: Path abstraction for local and cloud storage compatibility
- **CellProfiler Core**: Advanced functionality including `cross_correlation` alignment methods

## Key Components

### 1. Load Data Generation

#### Main Functions

- `write_loaddata`: Writes CSV headers and data rows for CellProfiler's LoadData module
- `write_loaddata_csv_by_batch_plate_cycle`: Writes load data CSV files organized by batch, plate, and cycle
- `gen_align_load_data_by_batch_plate`: Main entry point for load data generation

#### Data Organization

- Data is organized hierarchically by `batch`, `plate`, and `cycle`
- Each CSV contains metadata columns (Batch, Plate, Site, Well, Cycle)
- File paths for corrected images from each cycle and channel are included
- Reference images (usually cycle 1) and target images (other cycles) are linked together

### 2. CellProfiler Pipeline Generation

#### Main Functions

- `generate_align_pipeline`: Creates a CellProfiler pipeline for image alignment
- `gen_align_cppipe_by_batch_plate`: Writes pipeline files for each batch/plate combination

#### Pipeline Structure

The pipeline creates a sequence of modules that:
1. **LoadData**: Loads images from all cycles and channels using the CSV specification
2. **Align**: Registers images from each cycle to the reference cycle (typically cycle 1) using cross-correlation
3. **MeasureColocalization**: Measures alignment quality between registered images
4. **FlagImage**: Identifies images that failed to align properly based on correlation thresholds
5. **SaveImages**: Saves aligned images for all channels and cycles
6. **ExportToSpreadsheet**: Exports alignment quality metrics for downstream QC

### Technical Details

#### Alignment Method

- The module uses cross-correlation-based alignment (M_CROSS_CORRELATION)
- Images maintain their original size after alignment (C_SAME_SIZE)
- Additional images are aligned "similarly" (A_SIMILARLY) following the reference channel

#### Quality Control

- Alignment quality is measured using correlation between reference and aligned images
- Images with correlation below 0.9 are flagged as potentially problematic
- These quality metrics are exported for downstream filtering

#### File Naming and Organization

- Aligned images are named following the pattern: `[Batch]_[Plate]_[Cycle]_Well_[Well]_Site_[Site]_Aligned[Channel]`
- Images are saved as TIFF files with 16-bit depth

## Workflow

1. **Data Preparation**:
   - Read the index file containing image metadata
   - Filter for SBS images specifically
   - Group images by hierarchy (batch/plate/cycle)

2. **Load Data Generation**:
   - For each batch/plate combination:
     - Identify all cycles and channels
     - Generate a CSV file linking reference images (cycle 1) with other cycle images
     - Write to the output directory

3. **Pipeline Generation**:
   - For each generated CSV file:
     - Create a CellProfiler pipeline
     - Configure the Align module to use the nuclei channel as the alignment reference
     - Add quality control measurements
     - Set up image saving for all aligned images
     - Save the pipeline to a .cppipe file

4. **Execution**:
   - Pipelines are executed separately (not covered in this module)
   - Aligned images and quality metrics are saved

## Key Classes and Resources

- **PCPIndex**: Manages image metadata and hierarchy
- **CellProfilerContext**: Context manager for CellProfiler resources
- **Data Utilities**:
  - `gen_image_hierarchy`: Generates hierarchical organization of images
  - `get_channels_by_batch_plate`: Extracts channel information for a batch/plate
  - `get_cycles_by_batch_plate`: Extracts cycle information for a batch/plate

## Technical Implementation Notes

1. **Nuclei Channel Alignment**:
   - The default nuclei channel (typically DAPI) is used as the reference for alignment
   - This channel generally provides the most stable features across cycles

2. **Multi-Channel Alignment**:
   - After aligning the nuclei channel, all other channels from the same cycle are aligned using the same transformation
   - This preserves the spatial relationships between channels

3. **Quality Metrics**:
   - Correlation values between aligned images provide a quantitative measure of alignment success
   - These metrics help identify problematic fields or cycles

4. **Path Handling**:
   - Different paths are used for cycle 1 images (usually from IllumApply) vs. other cycles
   - This accommodates workflows where cycle 1 hasn't been through the alignment process yet

## Conclusion

The alignment module provides a robust system for registering sequential images in optical pooled screening experiments. By aligning all cycle images to a common reference, it enables accurate tracking of cellular features across cycles, which is essential for barcode calling and phenotype analysis. The built-in quality control metrics help identify problematic alignments, ensuring data quality in downstream analysis.
