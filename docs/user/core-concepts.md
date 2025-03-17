# Core Concepts

This guide explains the fundamental concepts behind the StarryNight platform.

## System Overview

StarryNight is a comprehensive platform for processing, analyzing, and managing optical pooled screening (OPS) image data, with particular focus on Cell Painting and sequencing-based assays.

### Core Components

The platform consists of three main components:

1. **StarryNight Core**: Image processing algorithms and command-line tools
2. **PipeCraft**: Workflow definition and execution framework
3. **Conductor**: Job scheduling, management, and Canvas UI

![System Architecture](assets/architecture.png)

## Data Organization

### Directory Structure

StarryNight uses a structured approach to organize data:

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

### File Naming Conventions

StarryNight extracts metadata from image file paths. The default parser ("vincent") expects paths like:

```
[dataset]/Source[source_id]/Batch[batch_id]/images/[plate_id]/[experiment_id]/Well[well_id]_Point[site_id]_[index]_Channel[channels]_Seq[sequence].ome.tiff
```

Example:
```
starrynight_example/Source1/Batch1/images/Plate1/20X_CP_Plate1_20240319_122800_179/WellA2_PointA2_0000_ChannelPhalloAF750,ZO1-AF488,DAPI_Seq1025.ome.tiff
```

## Workflow Concepts

### Basic Workflow

A typical StarryNight workflow involves:

1. **Inventory Generation**: Creating a catalog of image files
2. **Index Generation**: Extracting metadata from file paths
3. **Module Processing**: Running specific image processing algorithms
4. **Pipeline Execution**: Executing complete workflows

### Module System

StarryNight is built around a modular architecture, where each module:

- Represents a specific image processing task
- Has clearly defined inputs and outputs
- Can be used independently or in a workflow
- Often integrates with CellProfiler for processing

### Processing Approaches

StarryNight supports different processing approaches:

1. **CLI-based**: Direct command-line execution
2. **Pipeline-based**: Using PipeCraft to define workflows
3. **UI-based**: Using the Canvas interface

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

### Projects and Jobs

In the Conductor system:

- **Project**: An organizational unit for related analyses
- **Job**: A specific analysis run within a project
- **Run**: An execution instance of a job
- **Step**: An individual processing step in a job

## Canvas UI Concepts

The Canvas UI provides a graphical interface for:

- **Project Management**: Creating and organizing projects
- **Job Configuration**: Setting up analysis parameters
- **Execution Monitoring**: Tracking progress and viewing logs
- **Result Visualization**: Displaying and downloading results

## Next Steps

- Learn about all [Processing Modules](modules.md)
- Try the [Illumination Correction](illumination-correction.md) workflow
- Explore the [Canvas UI](ui-guide.md)
