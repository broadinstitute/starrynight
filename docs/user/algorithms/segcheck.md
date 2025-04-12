# Segmentation Check (segcheck.py)

!!! Warning
    - This document contains bot-generated text and has not yet been reviewed by developers!

Validates cell segmentation quality in microscopy images by performing cell and nuclei segmentation and generating visualizations that allow researchers to assess quality before proceeding with full analysis.

## Key Components

- **Multi-level Segmentation**: Identifies confluent regions, nuclei, and cells to evaluate different aspects of segmentation quality
- **Rich Visualization**: Creates color-coded overlays showing all detected objects simultaneously for visual assessment
- **Sampling Strategy**: Processes a subset (10%) of available sites to reduce computational load while providing sufficient quality assessment data

### CellProfiler Configuration

Key CellProfiler modules and configurations:

- **IdentifyPrimaryObjects**: Used for both confluent regions (500-5000 pixels) and nuclei (10-80 pixels)
- **IdentifySecondaryObjects**: Uses intensity watershed with three-class Otsu thresholding for cell boundary detection
- **GrayToColor**: Creates RGB visualizations with nuclei in magenta (red+blue) and cell boundaries in green
- **OverlayOutlines**: Adds nuclei outlines (blue), cell outlines (white), and confluent region outlines (orange)

## Implementation Notes

- **RGB Composition**: Uses a color scheme designed for easy visual assessment with good contrast between structures
- **Masked Analysis**: Excludes confluent regions to focus segmentation on areas with well-separated cells
- **Quality Hierarchy**: Identifies segmentation issues at multiple levels (confluent regions, nuclei, cells)
- **SBS vs. Non-SBS Handling**: Adapts to both standard and cycle-based image organizations
