# Algorithm Documentation

!!! Warning "Documentation Status"
    - This document contains comprehensive but **outdated** algorithm documentation
    - The documentation style and structure here should be used as a template for Python docstrings
    - Future algorithm documentation should be maintained in code docstrings rather than separate Markdown files
    - This document is retained as a reference for the documentation style and structure

This document contains concise technical documentation for algorithms in the StarryNight project, focusing on unique aspects and implementation details not obvious from the code.

## CellProfiler as the Foundation

StarryNight uses **CellProfiler** as its core image processing engine:

1. **StarryNight generates CellProfiler pipelines** rather than implementing image processing directly
2. **Common three-tier architecture**:
      - **Load Data Generation**: Creates CSVs for CellProfiler's LoadData module
      - **Pipeline Generation**: Programmatically constructs CellProfiler pipelines
      - **Pipeline Execution**: Handled elsewhere

## Documentation Guidelines

### Core Documentation Principles

1. **Be concise**: Developers can read code. Focus on explaining "why" not "how".
2. **Emphasize unique aspects**: Document what makes each algorithm special, not what's common.
3. **Focus on architecture decisions**: Explain key design choices and their rationale.
4. **Include non-obvious information**: Document things that aren't immediately clear from the code.

### Documentation Best Practices

1. **Be specific about differences**
      - Highlight what makes this algorithm unique
      - Don't repeat architectural patterns common to all algorithms
2. **Include only non-obvious examples**
      - Show examples only for complex or unusual configurations
      - Skip examples for standard patterns
3. **Focus on design decisions and trade-offs**
      - Explain why certain approaches were chosen
      - Document alternative approaches that were considered
4. **Document edge cases and limitations**
      - Note known limitations or constraints
      - Document special case handling
5. **Use consistent technical terminology**
      - Maintain consistent naming across all algorithm documentation
      - Use terms from the StarryNight codebase (e.g., "SBS" for sequential-based screening)
6. **Explain integration points**
      - Document how the algorithm connects with other components
      - Note any dependencies or required inputs

### Common StarryNight Patterns

When documenting algorithms, be aware of these common patterns that appear throughout the codebase:

- **SBS vs. Non-SBS Image Handling**: Most algorithms need to handle both standard images (batch/plate) and sequential-based screening images (batch/plate/cycle)
- **Sampling Strategies**: Many algorithms process a subset of available sites (often 10%) to balance thoroughness with computational efficiency
- **Hierarchical Data Processing**: Data organization typically follows batch → plate → [cycle] → channel hierarchies
- **Quality Control Integration**: Algorithms often implement quality checks and visualization capabilities
- **Memory/Performance Optimizations**: Common techniques include downsampling, masked analysis, and parallel processing

## Table of Contents

- [Illumination Calculation](#illumination-calculation-illum_calcpy)
- [Illumination Apply](#illumination-apply-illum_applypy)
- [Pre-segmentation Check](#pre-segmentation-check-presegcheckpy)
- [Segmentation Check](#segmentation-check-segcheckpy)
- [Alignment](#image-alignment-alignpy)
- [Stitch and Crop](#stitch-and-crop-stitchcroppy)
- [Preprocessing](#image-preprocessing-preprocesspy)
- [Analysis](#analysis-analysispy)

## Documentation Focus

Each section emphasizes:

- Unique components and features specific to the algorithm
- Key CellProfiler modules and configurations
- Non-obvious implementation details and special cases
- Integration points with other parts of the system

For understanding the overall system architecture, refer to the [Architecture Overview](../../architecture/00_architecture_overview.md) documentation.

---

## Illumination Calculation (illum_calc.py)

Calculates illumination correction functions for microscopy images to normalize uneven illumination patterns, a critical preprocessing step that improves downstream analysis quality.

### Key Components

- **Image Downsampling/Upsampling**: Uses 4x downsampling during processing and 4x upsampling for final outputs to improve performance while maintaining quality

#### CellProfiler Configuration

Key CellProfiler modules and configurations:

- **CorrectIlluminationCalculate**: Uses median filtering (block size 60, filter size 20) to model background illumination patterns
- **Resize**: Implements bilinear interpolation for both downsampling (0.25x) and upsampling (4x)
- **SaveImages**: Stores illumination functions as NumPy (.npy) files

### Implementation Notes

- **SBS vs. Non-SBS Images**: Handles both standard images (batch/plate) and sequential images (batch/plate/cycle)
- **Performance Optimization**: Downsampling reduces processing time while maintaining correction quality
- **Smooth Gradients**: Bilinear interpolation preserves smooth illumination gradients during resizing operations

---

## Illumination Apply (illum_apply.py)

Applies previously calculated illumination correction functions to microscopy images, normalizing uneven illumination patterns to improve downstream analysis accuracy.

### Key Components

- **Division-Based Correction**: Uses division method (DOS_DIVIDE) to normalize illumination, appropriate for fluorescence microscopy where illumination has multiplicative effects
- **Hierarchical Processing**: Handles both standard (batch/plate) and sequential (batch/plate/cycle) image organizations
- **Automatic Function Matching**: Automatically maps illumination functions to corresponding images based on metadata

#### CellProfiler Configuration

Key CellProfiler modules:

- **CorrectIlluminationApply**: Implements division-based correction to normalize images
- **SaveImages**: Preserves corrected images as 16-bit TIFFs to maintain precision

### Implementation Notes

- **SBS vs. Non-SBS Images**: Handles both standard and cycle-based sequential imaging protocols
- **Modular Design**: Separates illumination function calculation from application, enabling reuse of correction functions

---

## Pre-Segmentation Check (presegcheck.py)

Assesses image quality and segmentation feasibility prior to full image analysis by identifying confluent regions, nuclei, and cells to evaluate whether images are suitable for downstream processing.

### Key Components

- **Confluent Region Detection**: Identifies large confluent areas in the nuclei channel where individual cells cannot be resolved
- **Masked Analysis**: Creates masked versions of all channels that exclude confluent regions
- **Sampling Strategy**: Processes a subset (10%) of available sites to reduce computational load while providing sufficient quality data

#### CellProfiler Configuration

Key CellProfiler modules and configurations:

- **IdentifyPrimaryObjects (ConfluentRegions)**: Uses Otsu thresholding with 0.5 correction factor for larger objects (500-5000 pixels)
- **MaskImage**: Creates inverted masks to focus on non-confluent areas
- **IdentifyPrimaryObjects (Nuclei)**: Uses Otsu thresholding with shape-based declumping for smaller objects (10-80 pixels)
- **IdentifySecondaryObjects (Cells)**: Uses intensity watershed with three-class Otsu thresholding

### Implementation Notes

- **Different Channel Roles**: Uses nuclei channel for both confluent region and nuclei detection, while a separate cell channel is used for cell boundary detection
- **Hierarchy-Aware Processing**: Handles different organizational structures based on image type (standard vs. SBS)
- **Quality Metrics**: Extracts object counts and measurements as indicators of image quality and segmentation difficulty

---

## Segmentation Check (segcheck.py)

Validates cell segmentation quality in microscopy images by performing cell and nuclei segmentation and generating visualizations that allow researchers to assess quality before proceeding with full analysis.

### Key Components

- **Multi-level Segmentation**: Identifies confluent regions, nuclei, and cells to evaluate different aspects of segmentation quality
- **Rich Visualization**: Creates color-coded overlays showing all detected objects simultaneously for visual assessment
- **Sampling Strategy**: Processes a subset (10%) of available sites to reduce computational load while providing sufficient quality assessment data

#### CellProfiler Configuration

Key CellProfiler modules and configurations:

- **IdentifyPrimaryObjects**: Used for both confluent regions (500-5000 pixels) and nuclei (10-80 pixels)
- **IdentifySecondaryObjects**: Uses intensity watershed with three-class Otsu thresholding for cell boundary detection
- **GrayToColor**: Creates RGB visualizations with nuclei in magenta (red+blue) and cell boundaries in green
- **OverlayOutlines**: Adds nuclei outlines (blue), cell outlines (white), and confluent region outlines (orange)

### Implementation Notes

- **RGB Composition**: Uses a color scheme designed for easy visual assessment with good contrast between structures
- **Masked Analysis**: Excludes confluent regions to focus segmentation on areas with well-separated cells
- **Quality Hierarchy**: Identifies segmentation issues at multiple levels (confluent regions, nuclei, cells)
- **SBS vs. Non-SBS Handling**: Adapts to both standard and cycle-based image organizations

---

## Image Alignment (align.py)

Registers images across different cycles in sequencing-based imaging (SBS) experiments, enabling accurate tracking of cells across multiple imaging cycles for applications like optical pooled screening.

### Key Components

- **Cross-Correlation Alignment**: Uses phase correlation to align images, maintaining relative positions of cellular structures
- **Nuclei Channel Reference**: Uses the DAPI/nuclei channel as the primary reference for alignment due to its stable features
- **Quality Control Metrics**: Computes and exports correlation values to identify problematic alignments

#### CellProfiler Configuration

Key CellProfiler modules and configurations:

- **Align**: Implements cross-correlation alignment (M_CROSS_CORRELATION) while maintaining original image size
- **MeasureColocalization**: Measures alignment quality between reference and aligned images
- **FlagImage**: Identifies images that failed to align properly (correlation < 0.9)

### Implementation Notes

- **Multi-Channel Strategy**: After aligning the nuclei channel, all other channels use the same transformation matrix to preserve spatial relationships
- **Reference Cycle**: Typically uses cycle 1 as the reference, aligning all subsequent cycles to it
- **Parallel Processing**: Organizes alignment by batch/plate to enable efficient parallel processing

---

## Stitch and Crop (stitchcrop.py)

Stitches together multiple microscopy image tiles into a single composite image, enabling reconstruction of complete wells from multiple fields of view (FOVs).

### Key Components

- **ImageJ/Fiji Integration**: Uses Fiji's Grid/Collection Stitching plugin rather than CellProfiler for image stitching
- **Predefined Grid Layouts**: Includes optimized configurations for common tile layouts (52, 88, 256, 293, 316, 320, 394, 1332, 1364, 1396 tiles)
- **TileConfiguration Generation**: Automatically creates spatial relationship specifications for the stitching process

#### ImageJ Configuration

Key ImageJ parameters:

- **Stitching Parameters**: 10% tile overlap, linear blending for seamless transitions
- **Quality Control**: Uses regression threshold (0.30) and displacement thresholds (2.50/3.50) for accurate alignment
- **Memory Optimization**: Keeps output virtual to minimize RAM usage while processing large composite images

### Implementation Notes

- **PyImageJ Bridge**: Directly calls ImageJ plugins through Python API rather than using external scripts
- **Coordinate Calculation**: Calculates approximate tile positions which are then refined during the stitching process
- **Parameter Optimization**: Balances memory usage against computation time for large image sets
- **Layout Strategy**: Adapts stitching configuration based on the number of tiles per well

---

## Image Preprocessing (preprocess.py)

Implements a comprehensive preprocessing pipeline for sequencing-based (SBS) microscopy images to prepare them for downstream analysis, performing background subtraction, fluorescence compensation, cell segmentation, and barcode spot detection.

### Key Components

- **Background Subtraction**: Uses mean images across cycles to identify and remove consistent background patterns
- **Multi-stage Spot Detection**: Employs standard deviation images, feature enhancement, and filtering to identify barcode spots even in noisy images
- **Color Compensation**: Corrects for spectral overlap between fluorophores using custom CellProfiler module
- **Barcode Calling**: Identifies barcode sequences from intensity patterns across cycles using custom module

#### CellProfiler Configuration

Key CellProfiler modules and configurations:

- **IdentifyPrimaryObjects**: Identifies nuclei using Li's thresholding with size constraints (6-25 pixels)
- **IdentifySecondaryObjects**: Expands from nuclei using Otsu's three-class thresholding with watershed separation
- **EnhanceOrSuppressFeatures**: Enhances spot-like features with a 5-pixel radius
- **Custom Modules**:
    - `CompensateColors`: Performs spectral unmixing with histogram matching
    - `CallBarcodes`: Analyzes intensity patterns to identify barcode sequences

### Implementation Notes

- **Sampling Approach**: Processes a subset of sites (10% by default) to balance thoroughness with processing time
- **Multi-channel Analysis**: Processes all fluorescence channels across all cycles simultaneously
- **Visualization Assets**: Generates overlay images showing cell boundaries and barcode spots for QC
- **Data Organization**: Handles batch/plate/cycle hierarchies for SBS imaging data

---

## Analysis (analysis.py)

Implements a comprehensive analysis pipeline for microscopy images that integrates quality control, segmentation, feature extraction, and barcode calling to enable detailed phenotypic analysis of optical pooled screening experiments.

### Key Components

- **Multi-modality Integration**: Combines Cell Painting (CP) and sequential-based screening (SBS) images in a unified analysis pipeline
- **Multi-scale Feature Extraction**: Analyzes at subcellular (spots), cellular (nuclei, cells), and multicellular (neighborhoods, confluent regions) scales
- **Comprehensive Cell Profiling**: Extracts over 500 features covering intensity, morphology, texture, and spatial relationships

#### CellProfiler Configuration

Key CellProfiler modules and configurations:

- **IdentifyPrimaryObjects**: Detects nuclei (10-80 pixels) and barcode spots (2-10 pixels)
- **IdentifySecondaryObjects**: Uses propagation with Otsu three-class thresholding for cell detection
- **MeasureObjectIntensity/Texture/Granularity**: Captures diverse cellular phenotypic features
- **MeasureObjectNeighbors**: Quantifies spatial relationships between cells
- **Custom Modules**: Uses `CallBarcodes` and `CompensateColors` for calling barcodes

### Implementation Notes

- **Quality Control Integration**: Embeds multiple quality checkpoints throughout the pipeline including alignment verification
- **Data Organization**: Processes data by batch/plate with channels and cycles from both CP and SBS modalities
- **Computational Optimization**: Employs downsampling and memory management for large datasets
