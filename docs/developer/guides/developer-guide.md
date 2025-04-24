# Developer Guide

!!! warning

    **This is a first, very minimal draft of the document.**

This guide provides information for developers who want to contribute to StarryNight.

StarryNight is a modular platform for high-throughput microscopy image processing with four main components. For an overview of each component and its purpose, please refer to the [overview](../index.md#platform-overview).

## Repository Structure

The StarryNight repository is organized as a monorepo with four main packages:

```
starrynight/
├── canvas/              # Frontend UI (Next.js/React)
├── conductor/           # Job orchestration service
├── pipecraft/           # Pipeline definition framework
├── starrynight/         # Core image processing algorithms
├── docs/                # Documentation
├── nix/                 # Nix configuration
└── workspace/           # Development workspace
```

## Development Environment Setup

### Setup Steps

```sh
# Clone the repository
git clone https://github.com/broadinstitute/starrynight.git
cd starrynight

# Set up the Nix environment
nix develop --extra-experimental-features nix-command --extra-experimental-features flakes .

# Synchronize Python dependencies
uv sync
```

## Core Components and Design Patterns

### StarryNight Core

The foundation of the platform providing specialized algorithms for microscopy image analysis:

- **CLI Tools**: Command-line interfaces for each algorithm
- **Algorithms**: Image processing algorithms for microscopy data
- **Modules System**: Standardized module structure for algorithm implementation
- **Parsers**: File path parsing and metadata extraction
- **Utilities**: Common functions for file handling, data transformation, etc.

### PipeCraft

PipeCraft is the pipeline compiler, featuring:

- **Pipeline Definition**: Python API for defining computational workflows
- **Node System**: Individual processing steps as configurable nodes
- **Backend Abstraction**: Support for local, Docker, and AWS Batch execution
- **Template System**: Pre-defined templates for common backends

### Conductor

Conductor manages the execution environment:

- **REST API**: API for job management and monitoring
- **Database**: Storage for project configurations and job results
- **Job Management**: Scheduling, execution, and monitoring of jobs
- **WebSockets**: Real-time updates on job status

### Canvas UI

The web-based user interface:

- **React Components**: Modular UI components
- **State Management**: Zustand for global state
- **API Integration**: SWR for data fetching
- **Responsive Design**: Mobile-friendly interfaces
