# Pre-Segmentation Check (presegcheck.py)

Assesses image quality and segmentation feasibility prior to full image analysis by identifying confluent regions, nuclei, and cells to evaluate whether images are suitable for downstream processing.

## Key Components

- **Confluent Region Detection**: Identifies large confluent areas in the nuclei channel where individual cells cannot be resolved
- **Masked Analysis**: Creates masked versions of all channels that exclude confluent regions
- **Sampling Strategy**: Processes a subset (10%) of available sites to reduce computational load while providing sufficient quality data

### CellProfiler Configuration

Key CellProfiler modules and configurations:

- **IdentifyPrimaryObjects (ConfluentRegions)**: Uses Otsu thresholding with 0.5 correction factor for larger objects (500-5000 pixels)
- **MaskImage**: Creates inverted masks to focus on non-confluent areas
- **IdentifyPrimaryObjects (Nuclei)**: Uses Otsu thresholding with shape-based declumping for smaller objects (10-80 pixels)
- **IdentifySecondaryObjects (Cells)**: Uses intensity watershed with three-class Otsu thresholding

## Implementation Notes

- **Different Channel Roles**: Uses nuclei channel for both confluent region and nuclei detection, while a separate cell channel is used for cell boundary detection
- **Hierarchy-Aware Processing**: Handles different organizational structures based on image type (standard vs. SBS)
- **Quality Metrics**: Extracts object counts and measurements as indicators of image quality and segmentation difficulty
