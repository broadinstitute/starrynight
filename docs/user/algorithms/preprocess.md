# Image Preprocessing (preprocess.py)

Implements a comprehensive preprocessing pipeline for sequencing-based (SBS) microscopy images to prepare them for downstream analysis, performing background subtraction, fluorescence compensation, cell segmentation, and barcode spot detection.

## Key Components

- **Background Subtraction**: Uses mean images across cycles to identify and remove consistent background patterns
- **Multi-stage Spot Detection**: Employs standard deviation images, feature enhancement, and filtering to identify barcode spots even in noisy images
- **Color Compensation**: Corrects for spectral overlap between fluorophores using custom CellProfiler module
- **Barcode Calling**: Identifies barcode sequences from intensity patterns across cycles using custom module

### CellProfiler Configuration

Key CellProfiler modules and configurations:

- **IdentifyPrimaryObjects**: Identifies nuclei using Li's thresholding with size constraints (6-25 pixels)
- **IdentifySecondaryObjects**: Expands from nuclei using Otsu's three-class thresholding with watershed separation
- **EnhanceOrSuppressFeatures**: Enhances spot-like features with a 5-pixel radius
- **Custom Modules**:
    - `CompensateColors`: Performs spectral unmixing with histogram matching
    - `CallBarcodes`: Analyzes intensity patterns to identify barcode sequences

## Implementation Notes

- **Sampling Approach**: Processes a subset of sites (10% by default) to balance thoroughness with processing time
- **Multi-channel Analysis**: Processes all fluorescence channels across all cycles simultaneously
- **Visualization Assets**: Generates overlay images showing cell boundaries and barcode spots for QC
- **Data Organization**: Handles batch/plate/cycle hierarchies for SBS imaging data

## Integration Points

- **Inputs**: Requires aligned images from all cycles (typically from `align.py`)
- **Outputs**:
    - Segmentation results (nuclei, cells)
    - Barcode spot detections with sequence calls
    - Visualization overlays in PNG and TIFF formats
- **Dependencies**: CellProfiler plus custom modules `CallBarcodes` and `CompensateColors`
- **Downstream**: Feeds into detailed analysis pipeline for phenotypic profiling
