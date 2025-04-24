# Core Concepts

This guide explains the fundamental concepts behind the StarryNight platform.

## System Overview

StarryNight is a comprehensive platform for processing, analyzing, and managing optical pooled screening (OPS) image data, with particular focus on Cell Painting and sequencing-based assays.

For a detailed description of the platform's components and architecture, see the [Architecture Overview](../architecture/00_architecture_overview.md).

## Data Organization and Parsing

StarryNight provides flexibility in data organization through its inventory and index system, which extracts metadata from file paths using configurable path parsers.

### Inventory and Index Concepts

The foundation of data organization in StarryNight consists of two key concepts:

**Inventory**: A catalog of all files in a dataset

   - Contains basic file information: path, name, extension
   - Created by scanning a data directory recursively
   - Stored as a Parquet file for efficient querying

**Index**: Structured metadata extracted from file paths

   - Contains rich metadata: dataset, batch, plate, well, site, channel info
   - Created by parsing file paths using a grammar-based parser
   - Enables sophisticated filtering and selection of images
   - Stored as a structured Parquet file

### Directory Structure

StarryNight uses a standardized workspace structure for processing:

```
workspace/
├── inventory/                  # File inventory
│   └── inventory.parquet       # Master inventory file
├── index/                      # Structured metadata
│   └── index.parquet           # Index file with extracted metadata
├── cellprofiler/               # CellProfiler-related files
│   ├── loaddata/               # CSV files for loading images
│   └── cppipe/                 # Pipeline files
├── illum/                      # Illumination correction files
├── aligned/                    # Aligned images
└── results/                    # Analysis results
```

This workspace structure is used for processing results, but the *source data* can follow various organization patterns, as long as the path parser can interpret them.

### Path Parsing System

StarryNight uses a grammar-based path parsing system that:

1. Takes file paths from the inventory
2. Applies grammar rules to extract structured metadata
3. Creates index records with rich, queryable information

The default parser ("vincent") expects paths like:

```
[dataset]/Source[source_id]/Batch[batch_id]/images/[plate_id]/[experiment_id]/Well[well_id]_Point[site_id]_[index]_Channel[channels]_Seq[sequence].ome.tiff
```

Example:
```
starrynight_example/Source1/Batch1/images/Plate1/20X_CP_Plate1_20240319_122800_179/WellA2_PointA2_0000_ChannelPhalloAF750,ZO1-AF488,DAPI_Seq1025.ome.tiff
```

### Flexible Data Organization

The path parsing approach provides significant flexibility:

- **Dataset Structure**: Your raw data can follow different organization patterns
- **File Naming**: Different file naming conventions can be supported
- **Customization**: Custom parsers can be created for specific needs

The parsing system extracts key metadata including:

- Dataset, batch, and plate identifiers
- Well and site information
- Channel details
- Sequence/cycle information for sequence-based screens
- Other experiment-specific metadata

See [Parser Configuration](parser-configuration.md) for details on customizing the parser for your own data organization.

## Workflow Concepts

### Basic Workflow

A typical StarryNight workflow involves:

1. **Inventory Generation**: Creating a catalog of all image files (one-time step)
2. **Index Generation**: Extracting metadata from file paths (one-time step)
3. **Module Processing**: For each processing module (e.g., illumination correction):
      - **Generate LoadData**: Creating CellProfiler LoadData CSV files
      - **Generate Pipeline**: Creating CellProfiler pipeline (.cppipe) files
      - **Execute Pipeline**: Running CellProfiler with the generated files

### Module System

StarryNight is built around a modular architecture where each module represents a specific processing task (illumination correction, alignment, etc.). Modules follow a consistent three-step pattern:

1. **Load Data Generation**: Creating input specifications for processing
2. **Pipeline Generation**: Creating processing pipeline definitions
3. **Pipeline Execution**: Running the defined pipeline on the data

Modules can be used independently via CLI or composed into complete workflows through PipeCraft.

### Processing Approaches

StarryNight supports different processing approaches:

1. **CLI-based**: Direct command-line execution of individual modules
2. **Pipeline-based**: Using PipeCraft to define and automate complete workflows
3. **UI-based**: Using the Canvas interface for intuitive configuration and execution

## Key Abstractions

### Inventory and Index

These are the foundation of all StarryNight workflows:

- **Inventory**: A catalog of all files in a dataset
- **Index**: Structured metadata extracted from file paths

### Processing Modules

Each module handles a specific image processing task:

- **Illumination Correction**: Normalizes uneven illumination
- **Alignment**: Registers images across channels/cycles
- **Preprocessing**: Applies filters and quality control
- **Cell Painting Analysis**: Cell segmentation and features
- **Sequencing Analysis**: Processes sequencing-based images

## Next Steps

- Learn about all [Processing Modules](../user/modules.md)
