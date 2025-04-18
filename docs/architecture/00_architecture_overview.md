# Starry Night Architecture Overview

## Introduction

Starry Night is a scientific image processing framework designed for processing high-throughput imaging data. It provides a flexible, composable pipeline system that handles complex image processing workflows while maintaining separation of concerns between algorithms, execution, and configuration.

This document provides a high-level overview of the Starry Night architecture, explaining how the different components interact to form a complete pipeline system.

## Core Architectural Layers

Starry Night follows a layered architecture with increasing levels of abstraction:

1. **Algorithm Layer** - Core image processing functionality, completely independent of other layers
2. **CLI Layer** - Command-line interface wrappers
3. **Module Layer** - Standardized abstractions with specs and compute graphs
4. **Pipeline Layer** - Compositions of modules into executable workflows
5. **Execution Layer** - Backend systems that run the pipelines

Each layer builds upon the previous, adding capabilities while maintaining clear separation of concerns.

## Key Components

### Algorithm Sets

The foundation of Starry Night is the algorithm sets - collections of related functions that implement specific image processing steps. Each algorithm set typically includes:

- Functions to generate data loading configurations
- Functions to create CellProfiler pipelines
- Functions to execute pipelines on the data

**Critical Point:** Algorithm sets are pure Python functions with no external dependencies on other Starry Night components, making them easily testable and completely independent. As emphasized in the architecture discussions: "the first thing, which is the algorithm model, completely separate the core part. It's not dependent, dependent on anything else."

### CLI Wrappers

CLI wrappers expose algorithms as command-line tools using the Click library. They handle:

- Command structure and organization
- Parameter validation and type conversion
- Path handling using cloudpathlib's AnyPath (supporting both local and cloud storage)
- Consistent interface patterns

The CLI layer makes algorithms directly accessible to users without requiring Python programming.

### Modules

Modules are a key abstraction that standardize how pipeline components are defined and composed. A module:

- Encapsulates a spec that defines inputs and outputs (using Bilayers schema)
- Contains a compute graph that defines what operations will be performed
- Provides from_config methods for automatic configuration
- Does not perform actual computation (delegated to execution backends)

**Critical Point:** Modules focus on just two essential things - specs and compute graphs. As highlighted in the architecture discussions: "first the spec and that there is the compute graph. [A module] doesn't perform any compute it just gives you the compute graph." This separation is central to the system's power.

Each algorithm set typically corresponds to a module set containing specific module implementations for load data, pipeline generation, and execution.

### Pipelines

Pipelines compose multiple modules into executable workflows. The pipeline layer:

- Uses Pipecraft to define compute graphs with nodes and connections
- Configures containers for execution
- Manages parallel and sequential execution paths
- Handles input/output relationships between modules

Pipelines represent the complete computation to be performed but are backend-agnostic.

### Execution

The execution layer takes pipelines and runs them on specific backends:

- Currently implemented with Snakemake
- Translates Pipecraft pipelines into Snakemake rules
- Manages container execution (Docker/Singularity)
- Handles parallelism, logging, and monitoring

**Critical Point:** The execution is separated from pipeline definition, allowing the same pipeline to potentially run on different backends (local, cloud, etc.). This backend-agnostic approach is a major architectural achievement: "we can take this computer graph and then convert it to snake wave file... [or] write a back end that can execute it on AWS."

### Experiment Configuration

Experiment configuration classes handle parameter inference and standardization:

- Infer parameters from data where possible
- Combine user-provided parameters with defaults
- Create consistent configurations for modules
- Support extension for different experimental types

## Data Flow

A typical data flow through the Starry Night system:

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

Starry Night can be used in multiple contexts:

1. **Direct CLI usage** - Running algorithms directly via command line
2. **Notebook integration** - Creating and running pipelines in Jupyter notebooks
3. **UI integration** - Canvas and Conductor components provide web UI

Each context has different state management requirements, with the CLI being stateless and the UI maintaining session state.

### Container Usage

Starry Night uses containers for consistent execution:

- Each module defines its container requirements
- Containers include necessary dependencies (CellProfiler, Python libraries, etc.)
- Execution is delegated to container runtimes (Docker, Singularity)
- Container-based execution ensures reproducibility

## Extension Points

Starry Night is designed for extensibility:

1. **New algorithms** - Add functions to implement new image processing techniques
2. **New CLI commands** - Expose new algorithms through command-line interfaces
3. **New modules** - Create modules with specs and compute graphs for new functionality
4. **New experiment types** - Define new experiment classes for different workflows
5. **New backends** - Implement new execution backends beyond Snakemake

## Visual Representation

```
┌─────────────────────────────────────┐
│ User Interface (Canvas/Notebook/CLI) │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│ Experiment Configuration             │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│ Module System                        │
│  ┌─────────────┐   ┌──────────────┐  │
│  │ Bilayer Spec │◄──┤ Configuration│  │
│  └─────┬───────┘   └──────────────┘  │
│        │                             │
│  ┌─────▼───────┐                     │
│  │ Compute     │                     │
│  │ Graph       │                     │
│  └─────┬───────┘                     │
└─────────┬───────────────────────────┘
          │
┌─────────▼───────────────────────────┐
│ Pipeline Composition (Pipecraft)     │
└─────────┬───────────────────────────┘
          │
┌─────────▼───────────────────────────┐
│ Execution Backend (Snakemake)        │
└─────────┬───────────────────────────┘
          │
┌─────────▼───────────────────────────┐
│ Container Execution                  │
│ ┌─────────────────────────────────┐ │
│ │ Algorithms (via CLI)            │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Key Concepts Reference

- **Algorithm Set**: Group of functions that implement a specific pipeline step
- **Module**: Standardized wrapper with spec and compute graph
- **Bilayers**: Schema system for defining module inputs/outputs
- **Pipecraft**: Library for creating composable pipeline graphs
- **Compute Graph**: Definition of operations and their relationships
- **Container**: Isolated execution environment with dependencies
- **Snakemake**: Workflow engine that executes the compiled pipeline

## The Central Architectural Achievement

The most important architectural achievement of Starry Night is the clear separation between what should be done (algorithms), how it should be configured (specs), how it should be structured (compute graphs), and how it should be executed (backends). As emphasized in the architecture discussions:

> "This is not just some weird attraction or something that we want. Just we built it because we wanted to build it. It's there because it's a very key piece. It's a central piece of like the entire system."

This separation enables the automatic generation of complex execution plans (like 500+ line Snakemake files) while maintaining the simplicity and clarity of the higher-level abstractions.

## Conclusion

The Starry Night architecture provides a flexible system for scientific image processing that separates concerns between algorithms, specifications, and execution. This separation allows for reuse, composition, and extension while maintaining reproducibility through containerized execution.

The following documents provide detailed explanations of each component, their implementation, and how they work together in the complete system.
