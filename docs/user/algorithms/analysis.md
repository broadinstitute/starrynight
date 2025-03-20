# Analysis (analysis.py) - Technical Documentation

This document provides a detailed explanation of the analysis algorithm implementation in the StarryNight project.

## Overview

The `analysis.py` module implements a comprehensive analysis pipeline for microscopy images in the StarryNight platform. It integrates multiple image processing steps including quality control, segmentation, feature extraction, and barcode calling to enable detailed phenotypic analysis of optical pooled screening experiments.

The module follows StarryNight's standard three-tier architecture:
1. Load data generation (creating CSVs for CellProfiler's LoadData module)
2. CellProfiler pipeline generation (programmatically constructing a .cppipe file)
3. Pipeline execution (handled elsewhere)

## Dependencies

The module relies on a wide range of libraries:
- **CellProfiler**: Over 30 different image processing modules including segmentation, measurement, feature extraction, and morphological operations
- **Polars**: Data manipulation through DataFrames
- **CloudPath**: Path abstraction for local and cloud storage compatibility
- **Custom CellProfiler Plugins**: Specialized modules for barcode calling (`CallBarcodes`) and color compensation (`CompensateColors`)

## Key Components

### 1. Load Data Generation

#### Main Functions

- `write_loaddata`: Writes CSV headers and data rows for CellProfiler's LoadData module
- `gen_analysis_load_data_by_batch_plate`: Main entry point for load data generation

#### Data Organization

- Data is organized hierarchically by `batch`, `plate`, and `cycle`
- The CSV integrates data from multiple sources:
  - Cell Painting (CP) corrected images
  - Sequential-based screening (SBS) corrected images
  - SBS compensated images from preprocessing
- All channels and cycles from both image types are included in a single CSV file

### 2. CellProfiler Pipeline Generation

#### Main Functions

- `generate_analysis_pipeline`: Creates an extensive CellProfiler pipeline for comprehensive image analysis
- `gen_analysis_cppipe_by_batch_plate`: Writes pipeline files for each batch/plate combination

#### Pipeline Structure

The pipeline creates an extensive sequence of modules that can be grouped into several major analysis steps:

1. **Quality Control**:
   - Measures image intensity to detect empty images
   - Flags and skips problematic images
   - Performs alignment verification using correlation metrics

2. **Image Preprocessing**:
   - Aligns images across channels and cycles
   - Detects non-padded areas and creates masks
   - Creates distance maps from image edges

3. **Primary Object Detection**:
   - Identifies confluent regions
   - Detects nuclei using DAPI/Hoechst channel
   - Identifies barcode spots/foci

4. **Secondary Object Detection**:
   - Expands from nuclei to detect cell boundaries
   - Creates cytoplasmic regions (tertiary objects)
   - Generates various masks for feature extraction

5. **Feature Extraction**:
   - Measures object intensity across channels
   - Calculates object shape metrics
   - Assesses texture and granularity
   - Performs colocalization analysis
   - Quantifies neighborhood relationships

6. **Barcode Analysis**:
   - Calls barcodes from intensity patterns
   - Relates barcodes to cells
   - Calculates barcode scores and quality metrics

7. **Visualization**:
   - Creates RGB overlays for quality assessment
   - Generates outlines of detected objects
   - Saves visualizations of segmentation results

8. **Data Export**:
   - Exports all measurements to spreadsheets
   - Organizes outputs by batch and plate

### Technical Details

#### Object Detection Parameters

- **Nuclei Detection**:
  - Size range: 10-80 pixels
  - Shape-based declumping
  - Otsu thresholding with foreground assignment

- **Cell Detection**:
  - Propagation-based segmentation from nuclei
  - Uses cell channel (typically Phalloidin/Actin)
  - Three-class Otsu thresholding

- **Foci/Spot Detection**:
  - Size range: 2-10 pixels
  - Intensity-based watershed
  - Robust background thresholding with median filtering

#### Feature Measurement

- **Intensity Features**: Mean, median, standard deviation, min/max for all channels
- **Shape Features**: Area, perimeter, form factor, eccentricity, etc.
- **Texture Features**: Haralick features, angular second moment, etc.
- **Distribution Features**: Radial distribution of intensity from nucleus center
- **Granularity Features**: Spectrum of structure sizes within cells
- **Neighborhood Features**: Number of neighbors, percent touching, correlation between neighbors

#### Barcode Calling

- Measures intensities of all channels across all cycles
- Compares intensity patterns to expected barcode sequences
- Assigns barcode IDs and gene symbols to detected spots
- Calculates confidence scores for each barcode call

## Workflow

1. **Data Preparation**:
   - Read the index file containing image metadata
   - Filter for both CP and SBS images
   - Organize image paths for both modalities

2. **Load Data Generation**:
   - For each batch/plate combination:
     - Identify all channels and cycles
     - Generate a CSV file linking all required images
     - Write to the output directory

3. **Pipeline Generation**:
   - For each generated CSV file:
     - Create a comprehensive CellProfiler pipeline
     - Configure all modules with appropriate parameters
     - Set up complex image processing workflows
     - Save the pipeline to a .cppipe file

4. **Pipeline Execution**:
   - Pipelines are executed separately (not covered in this module)
   - Feature data and visualizations are saved to output directories

## Key Classes and Resources

- **PCPIndex**: Manages image metadata and hierarchy
- **CellProfilerContext**: Context manager for CellProfiler resources
- **Custom CellProfiler Plugins**:
  - `CallBarcodes`: Identifies barcode sequences from intensity patterns
  - `CompensateColors`: Corrects for spectral overlap between fluorophores
- **CellProfiler Modules**:
  - Extensive use of over 30 different CellProfiler modules
  - Configured with parameters optimized for microscopy data

## Technical Implementation Notes

1. **Integration of Multiple Data Types**:
   - The pipeline integrates standard Cell Painting and cycle-based (SBS) images
   - Different image sources are aligned and processed together
   - This enables cross-modality analysis and feature extraction

2. **Multi-Scale Analysis**:
   - Features are extracted at multiple scales: subcellular (spots), cellular (nuclei, cells), and multicellular (confluent regions)
   - Object relationships are captured through parent-child relationships
   - Neighborhood analysis captures tissue-level organization

3. **Quality Control Integration**:
   - Multiple quality control steps are embedded throughout the pipeline
   - Images and objects failing quality criteria are flagged
   - Measurements are conditional on passing quality thresholds

4. **Computational Efficiency**:
   - Specific steps use downsampling to improve performance
   - Memory-intensive operations are optimized
   - The pipeline is designed to handle large-scale screening datasets

## Conclusion

The analysis module provides a comprehensive system for extracting rich phenotypic data from microscopy images. By leveraging CellProfiler's extensive module library, it enables multi-parametric analysis including cell morphology, subcellular structure, and barcode-based genetic perturbation readouts. This module represents the culmination of the StarryNight processing workflow, generating the feature data that forms the basis for downstream biological insights.
