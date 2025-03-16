# StarryNight Overview

StarryNight is a comprehensive image processing system designed specifically for optical pooled screening (OPS) and cell painting workflows. This document explains the core concepts and components of the system.

## What is StarryNight?

StarryNight is a software suite that enables scientists to process, analyze, and manage large-scale microscopy image datasets, with a focus on cell painting and optical pooled screening applications. It provides:

- Algorithms for image processing (illumination correction, alignment, preprocessing)
- Integration with CellProfiler for advanced cell analysis
- Workflow orchestration and pipeline execution
- Web-based user interface for experiment configuration and monitoring

## Key Problems StarryNight Solves

1. **Large-Scale Image Processing**: Handles thousands of high-resolution microscopy images efficiently
2. **Workflow Standardization**: Establishes consistent processing pipelines for reproducible research
3. **Computational Resource Management**: Orchestrates execution across computing resources
4. **Result Organization**: Manages and organizes complex experimental outputs

## System Components

StarryNight is organized into three main packages:

### 1. StarryNight Core

The scientific algorithm layer providing:
- Image processing algorithms (alignment, illumination correction, etc.)
- CellProfiler integration
- Command-line interface for direct usage
- Data parsing and indexing utilities

### 2. Pipecraft

The pipeline abstraction framework offering:
- Representation of computational workflows as directed acyclic graphs
- Execution backends for different environments (local, cloud)
- Sequential and parallel execution strategies

### 3. Conductor

The orchestration and user interface layer delivering:
- Project and job management
- Execution tracking and monitoring
- REST API for programmatic access
- Integration with the Canvas web UI

## Workflow Overview

A typical StarryNight workflow involves:

1. **Project Creation**: Defining a dataset and processing parameters
2. **Inventory Generation**: Creating a comprehensive listing of all image files
3. **Index Creation**: Parsing file information into structured metadata
4. **Module Configuration**: Setting up specific processing steps
5. **Pipeline Execution**: Running the configured workflow
6. **Result Analysis**: Examining and utilizing the processed outputs

## Using StarryNight

Users can interact with StarryNight in two ways:

1. **Command-Line Interface**: Direct access to algorithms for scripting and power users
2. **Web User Interface**: Canvas UI for visual configuration and monitoring

Each approach has advantages depending on your specific needs and workflow preferences.

## Next Steps

- Learn about [Projects and Datasets](projects.md)
- Understand [Inventory and Index](inventory-index.md)
- Explore [Modules and Pipelines](modules-pipelines.md)
- Try the [CLI Workflows](../user/cli-workflows/illumination-correction.md)
- Get started with the [Web UI](../user/web-ui/getting-started.md)
