# Algorithm Documentation

This directory contains concise technical documentation for algorithms in the StarryNight project, focusing on unique aspects and implementation details not obvious from the code.

## CellProfiler as the Foundation

StarryNight uses **CellProfiler** as its core image processing engine:

1. **StarryNight generates CellProfiler pipelines** rather than implementing image processing directly
2. **Common three-tier architecture**:
      - **Load Data Generation**: Creates CSVs for CellProfiler's LoadData module
      - **Pipeline Generation**: Programmatically constructs CellProfiler pipelines
      - **Pipeline Execution**: Handled elsewhere

## Algorithm Index

- [Illumination Calculation](illum_calc.md): Calculates illumination correction functions
- [Illumination Apply](illum_apply.md): Applies illumination correction to images
- [Alignment](align.md): Registers images across cycles and channels
- [Preprocessing](preprocess.md): Prepares images for analysis
- [Analysis](analysis.md): Performs feature extraction and analysis
- [Pre-segmentation Check](presegcheck.md): Validates images prior to segmentation
- [Segmentation Check](segcheck.md): Validates segmentation results
- [Stitch and Crop](stitchcrop.md): Combines and crops image tiles

## Documentation Focus

Each document emphasizes:

- Unique components and features specific to the algorithm
- Key CellProfiler modules and configurations
- Non-obvious implementation details and special cases
- Integration points with other parts of the system

For understanding the overall system architecture, refer to the [Core Concepts](../core-concepts.md) documentation.
