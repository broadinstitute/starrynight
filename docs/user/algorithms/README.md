# Algorithm Documentation

This directory contains technical documentation for each algorithm in the StarryNight project. Each file provides detailed information about a specific algorithm's implementation, including its architecture, components, workflow, and technical details.

## CellProfiler as the Foundation

The StarryNight platform uses **CellProfiler** as its core image processing engine. This fundamental design choice defines how algorithms are implemented:

1. **StarryNight does not implement image processing algorithms directly**. Instead, it generates CellProfiler pipelines that perform the actual image processing.

2. **Each algorithm follows a three-tier architecture**:
   - **Load Data Generation**: Creates CSV files that tell CellProfiler which images to process
   - **Pipeline Generation**: Programmatically constructs CellProfiler pipelines (.cppipe files) with specific modules
   - **Pipeline Execution**: Runs CellProfiler with the generated pipeline and input data (handled separately)

3. **Key Benefits of the CellProfiler-based approach**:
   - Leverages CellProfiler's extensive, validated image processing capabilities
   - Provides reproducible workflows through explicit pipeline files
   - Allows flexible scaling from local execution to distributed computing

## Algorithm Index

The following algorithms are documented:

- [Illumination Calculation](illum_calc.md): Calculates illumination correction functions for microscopy images
- [Illumination Apply](illum_apply.md): Applies illumination correction to microscopy images
- [Alignment](align.md): Registers images across cycles and channels
- [Preprocessing](preprocess.md): Prepares images for analysis with standardization and quality checks
- [Analysis](analysis.md): Performs feature extraction and analysis on processed images
- [Pre-segmentation Check](presegcheck.md): Validates images prior to segmentation
- [Segmentation Check](segcheck.md): Validates segmentation results
- [CellProfiler Plugins](cp_plugins.md): Additional CellProfiler functionality
- [Index Generation](index.md): Creates structured metadata from file paths
- [Inventory](inventory.md): Catalogs files in a dataset

## Using This Documentation

Each algorithm document is structured to help developers understand both the conceptual approach and implementation details:

- **Overview**: Explains the algorithm's purpose and its place in the workflow
- **Dependencies**: Lists key libraries, with emphasis on CellProfiler modules used
- **Key Components**: Details the load data generation and pipeline generation functions
- **Workflow**: Describes the end-to-end process from input to output
- **Technical Implementation**: Highlights important considerations and design decisions

For understanding the overall system architecture, refer to the [Core Concepts](../core-concepts.md) documentation.
