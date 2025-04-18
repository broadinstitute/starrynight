# StarryNight Architecture Overview

## Introduction

StarryNight is a scientific image processing framework designed for processing high-throughput imaging data. It provides a flexible, composable pipeline system that handles complex image processing workflows while maintaining separation of concerns between algorithms, execution, and configuration.

This document provides a high-level overview of the StarryNight architecture, explaining how the different components interact to form a complete pipeline system.

## Project Structure

The StarryNight framework is organized as a monorepo with four main packages:

1. **StarryNight** - Core package containing:
    - Algorithm Layer: Pure Python functions for image processing
    - CLI Layer: Command-line interfaces for algorithms
    - Module System: Standardized module abstractions

2. **PipeCraft** - Pipeline definition framework that powers:
    - Pipeline Layer: Composition of modules into workflows
    - Part of the Execution Layer: Backend abstractions

3. **Conductor** - Job orchestration service handling:
    - Execution management and monitoring
    - Configuration storage
    - REST API for job control

4. **Canvas** - Frontend UI providing:
    - Web interface for pipeline configuration
    - Visualization of results
    - Integration with Conductor

!!!warning "Documentation Scope"
     This architecture documentation primarily focuses on the StarryNight core and PipeCraft packages. The Conductor (job orchestration) and Canvas (user interface) packages are mentioned for completeness but not covered in detail in the current documentation.

!!!note "Focus"
     This documentation primarily focuses on the architectural layers rather than the package boundaries, as layers can span multiple packages.

## Core Architectural Layers

StarryNight follows a layered architecture with increasing levels of abstraction:

1. **Algorithm Layer** - Core image processing functionality, completely independent of other layers
2. **CLI Layer** - Command-line interface wrappers
3. **Module Layer** - Standardized abstractions with specs and compute graphs
4. **Pipeline Layer** - Compositions of modules into executable workflows
5. **Execution Layer** - Backend systems that run the pipelines

Each layer builds upon the previous, adding capabilities while maintaining clear separation of concerns.

## Key Components

### Algorithm Sets

The foundation of StarryNight is the algorithm sets -- collections of related functions that implement specific image processing steps (1). While many examples use CellProfiler-focused algorithm sets (with data loading, pipeline generation, and execution functions), the architecture supports various other types like indexing, inventory management, quality control, and data visualization.
{ .annotate }

1. Algorithm sets are pure Python functions with no external dependencies on other StarryNight components, making them easily testable and completely independent.

### CLI Wrappers

CLI wrappers expose algorithms as command-line tools. This layer handles parameter parsing, path management, and command organization, making algorithms directly accessible to users without requiring Python programming.

### Modules

Modules are a key abstraction that standardize how pipeline components are defined and composed (1).
{ .annotate }

1. Modules have a dual focus - specs and compute graphs. They describe what should be done (through specifications) and how it should be structured (through compute graphs), but don't actually perform the computation.

A module:

- Encapsulates a spec that defines inputs and outputs (using [Bilayers](https://github.com/bilayer-containers/bilayers) schema)
- Contains a compute graph that defines what operations will be performed
- Provides `from_config` methods for automatic configuration from experiment settings
- Does not perform actual computation (delegated to execution backends)

Each algorithm set typically corresponds to a module set containing specific module implementations for load data generation, pipeline generation, and execution.

### Pipelines

Pipelines compose multiple modules into executable workflows. The pipeline layer:

- Uses Pipecraft to define compute graphs with nodes and connections
- Configures containers for execution
- Manages parallel and sequential execution paths
- Handles input/output relationships between modules

Pipelines represent the complete computation to be performed but are backend-agnostic.

### Execution

The execution layer takes pipelines and runs them on specific backends(1):
{ .annotate }

1. The execution is separated from pipeline definition, allowing the same pipeline to potentially run on different backends (local, cloud, etc.).

- Currently implemented with Snakemake
- Translates Pipecraft pipelines into Snakemake rules
- Manages container execution (Docker/Singularity)
- Handles parallelism, logging, and monitoring

### Experiment Configuration

Experiment configuration classes handle parameter inference and standardization:

- Infer parameters from data where possible
- Combine user-provided parameters with defaults
- Create consistent configurations for modules
- Support extension for different experimental types

## Data Flow

A typical data flow through the StarryNight system:

1. User configures an experiment with minimal required parameters
2. Experiment configuration infers additional parameters
3. Modules are instantiated with the configuration
4. Modules generate their compute graphs (Pipecraft pipelines)
5. Pipelines are composed for complete workflow
6. Backend translates the pipeline to executable form (e.g., Snakefile)
7. Backend executes the workflow in containers
8. Results are stored in configured locations

## System Integration

### Execution Contexts

StarryNight can be used in multiple contexts:

1. **Direct CLI usage** - Running algorithms directly via the CLI layer in the StarryNight core package
2. **Notebook integration** - Creating and running pipelines in Jupyter notebooks using StarryNight and PipeCraft
3. **UI integration** - Using the Canvas (frontend package) and Conductor (orchestration package) which provide a web-based interface that ultimately utilizes the same core functionality

Each context has different state management requirements, with the CLI being stateless and the UI components (Canvas and Conductor) maintaining session state.

### Container Usage

StarryNight uses containers for consistent execution:

- Each module defines its container requirements
- Containers include necessary dependencies (CellProfiler, Python libraries, etc.)
- Execution is delegated to container runtimes (Docker, Singularity)
- Container-based execution ensures reproducibility

## Extension Points

StarryNight is designed for extensibility:

1. **New algorithms** - Add functions to implement new image processing techniques
2. **New CLI commands** - Expose new algorithms through command-line interfaces
3. **New modules** - Create modules with specs and compute graphs for new functionality
4. **New experiment types** - Define new experiment classes for different workflows
5. **New backends** - Implement new execution backends beyond Snakemake

## Key Concepts Reference

- **Algorithm Set**: Group of functions that implement a specific pipeline step
- **Module**: Standardized wrapper with spec and compute graph
- **Bilayers**: Schema system for defining module inputs/outputs
- **Pipecraft**: Library for creating composable pipeline graphs
- **Compute Graph**: Definition of operations and their relationships
- **Container**: Isolated execution environment with dependencies
- **Snakemake**: Workflow engine that executes the compiled pipeline

## The Central Architectural Achievement

The most important architectural achievement of StarryNight is the clear separation between what should be done (algorithms), how it should be configured (specs), how it should be structured (compute graphs), and how it should be executed (backends).

This separation enables the automatic generation of complex execution plans (like 500+ line Snakemake files) while maintaining the simplicity and clarity of the higher-level abstractions.

## Conclusion

The StarryNight architecture provides a flexible system for high-throughput microscopy image processing that separates concerns between algorithms, specifications, and execution. This separation allows for reuse, composition, and extension while maintaining reproducibility through containerized execution.

The following documents provide detailed explanations of each component, their implementation, and how they work together in the complete system.
