# Image Preprocessing (preprocess.py) - Technical Documentation

This document provides a detailed explanation of the image preprocessing algorithm implementation in the StarryNight project.

## Overview

The `preprocess.py` module implements a comprehensive preprocessing pipeline for sequencing-based (SBS) microscopy images. This critical step prepares images for downstream analysis by performing background subtraction, fluorescence compensation, cell segmentation, and barcode spot detection.

The module follows StarryNight's standard three-tier architecture:
1. Load data generation
2. CellProfiler pipeline generation
3. Pipeline execution (handled elsewhere)

## Dependencies

The module relies on several key libraries:
- **CellProfiler**: Extensive image processing functionality including segmentation, measurement, and feature enhancement
- **Polars**: Data manipulation through DataFrames
- **CloudPath**: Path abstraction for local and cloud storage compatibility
- **Custom CellProfiler Plugins**: Specialized modules for barcode calling (`CallBarcodes`) and color compensation (`CompensateColors`)

## Key Components

### 1. Load Data Generation

#### Main Functions

- `write_loaddata`: Writes CSV headers and data rows for CellProfiler's LoadData module
- `gen_preprocess_load_data_by_batch_plate`: Main entry point for load data generation

#### Data Organization

- Data is organized hierarchically by `batch`, `plate`, and `cycle`
- Load data CSVs combine aligned images from both cycle 1 and other cycles
- A sampling approach (10% by default) is used to reduce computation for large datasets

### 2. CellProfiler Pipeline Generation

#### Main Functions

- `generate_preprocess_pipeline`: Creates a complex CellProfiler pipeline for image preprocessing
- `gen_preprocess_cppipe_by_batch_plate`: Writes pipeline files for each batch/plate combination

#### Pipeline Structure

The pipeline creates a sophisticated sequence of modules that:
1. **LoadData**: Loads aligned images from all cycles and channels
2. **ImageMath**: Calculates mean and standard deviation images across cycles
3. **CorrectIlluminationCalculate/Apply**: Performs background subtraction
4. **IdentifyPrimaryObjects**: Identifies nuclei from the reference channel
5. **IdentifySecondaryObjects**: Expands from nuclei to identify cell boundaries
6. **EnhanceOrSuppressFeatures**: Enhances spot-like features for barcode detection
7. **IdentifyPrimaryObjects**: Detects potential barcode spots
8. **FilterObjects**: Filters spots based on quality metrics
9. **CompensateColors**: Performs color compensation to correct spectral overlap
10. **MeasureObjectIntensity**: Measures intensity in each spot across all channels and cycles
11. **CallBarcodes**: Identifies barcode sequences based on intensity patterns
12. **RelateObjects**: Links barcodes to cells
13. **SaveImages**: Saves preprocessed images and visualization overlays
14. **ExportToSpreadsheet**: Exports measurements for downstream analysis

### Technical Details

#### Cell Segmentation Parameters

- Nuclei identification uses Li's thresholding method with size constraints (6-25 pixels)
- Cell segmentation uses propagation from nuclei with Otsu's three-class thresholding
- Both steps include watershed-based separation of touching objects

#### Barcode Detection

- Standard deviation images across cycles highlight spots with temporal variability
- Enhancement of spot-like features with a 5-pixel radius
- Robust background thresholding with size constraints (2-10 pixels)
- Filtering based on object measurements to reduce false positives

#### Color Compensation

- Custom `CompensateColors` module corrects for spectral overlap between fluorophores
- Post-masking histogram matching normalizes intensity distributions
- Optional Laplacian of Gaussian (LoG) filtering enhances spot detection

#### Barcode Calling

- Custom `CallBarcodes` module analyzes intensity patterns across cycles
- References barcode sequences from an external CSV file
- Identifies best matching barcode sequences for each spot
- Maps barcodes to gene symbols for biological interpretation

## Workflow

1. **Data Preparation**:
   - Read the index file containing image metadata
   - Filter for SBS images specifically
   - Sample a subset (10%) of sites for computational efficiency
   - Group images by hierarchy (batch/plate/cycle)

2. **Load Data Generation**:
   - For each batch/plate combination:
     - Identify all cycles and channels
     - Generate a CSV file linking aligned images from all cycles
     - Write to the output directory

3. **Pipeline Generation**:
   - For each generated CSV file:
     - Create a comprehensive CellProfiler pipeline
     - Configure all segmentation, feature extraction, and barcode calling steps
     - Set up visualization and data export
     - Save the pipeline to a .cppipe file

4. **Execution**:
   - Pipelines are executed separately (not covered in this module)
   - Preprocessed images, barcode calls, and measurements are saved

## Key Classes and Resources

- **PCPIndex**: Manages image metadata and hierarchy
- **CellProfilerContext**: Context manager for CellProfiler resources
- **Custom CellProfiler Plugins**:
  - `CallBarcodes`: Identifies barcode sequences from intensity patterns
  - `CompensateColors`: Corrects for spectral overlap between fluorophores

## Technical Implementation Notes

1. **Background Subtraction**:
   - Mean images across cycles identify consistent background patterns
   - Background subtraction (rather than division) is used to preserve relative intensities

2. **Multi-stage Spot Detection**:
   - Standard deviation images highlight variable spots
   - Feature enhancement focuses on spot-like structures
   - Size and intensity filtering reduces false positives
   - This approach effectively identifies barcode spots even in noisy images

3. **Optimized Performance**:
   - The algorithm processes a subset of sites (10% sampling) to balance thoroughness with processing time
   - Complete image sets can be processed in subsequent production runs using the same pipeline

4. **Visualization Assets**:
   - The pipeline generates overlay images showing cell boundaries and barcode spots
   - These are saved in both PNG (for quick viewing) and TIFF (for detailed analysis) formats
   - Visualizations are crucial for quality control and result interpretation

## Conclusion

The preprocessing module provides a comprehensive system for preparing sequencing-based microscopy images for analysis. It performs critical steps including background correction, cell segmentation, barcode spot detection, and sequence calling. The resulting preprocessed images and barcode calls enable downstream phenotypic analysis and spatial transcriptomics applications. The pipeline's sophisticated approach to spot enhancement and barcode calling makes it particularly effective for optical pooled screening experiments.
