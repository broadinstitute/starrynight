# Developer Guide

This guide provides information for developers who want to contribute to StarryNight.

## System Architecture

StarryNight is a modular platform for high-throughput microscopy image processing with four main components that work together to process, analyze, and manage microscopy image data.

```mermaid
graph TD
    %% Data sources
    RawData[Raw Image Files] --> Index

    %% StarryNight Core Components
    subgraph StarryNightCore["StarryNight Core"]
        Index[Image Indexing] --> Processing
        Processing[Image Processing]
        Processing --> QC[Quality Control]
        IllumCorr[Illumination Correction]
        Alignment[Image Alignment]
        Preprocess[Preprocessing]
        CellPainting[Cell Painting Analysis]
        Processing --> IllumCorr
        Processing --> Alignment
        Processing --> Preprocess
        Processing --> CellPainting
    end

    %% PipeCraft Components
    subgraph PipeCraftEngine["PipeCraft"]
        Pipeline[Pipeline Definition]
        Nodes[Processing Nodes]
        LocalBackend[Local Execution]
        DockerBackend[Docker Execution]
        AwsBackend[AWS Batch Execution]
        Pipeline --> Nodes
        Nodes --> LocalBackend
        Nodes --> DockerBackend
        Nodes --> AwsBackend
    end

    %% Conductor Components
    subgraph ConductorService["Conductor"]
        JobMgmt[Job Management]
        Database[(Database)]
        RestAPI[REST API]
        WSNotify[WebSocket Notifications]
        JobMgmt --> Database
        RestAPI --> JobMgmt
        JobMgmt --> WSNotify
    end

    %% Canvas UI Components
    subgraph CanvasUI["Canvas UI"]
        Projects[Project Management]
        JobConfig[Job Configuration]
        Monitoring[Run Monitoring]
        Results[Results Visualization]
    end

    %% Connections between components
    StarryNightCore --> PipeCraftEngine
    PipeCraftEngine --> ConductorService
    ConductorService --> CanvasUI

    %% Data flow from UI to execution
    Projects --> JobConfig
    JobConfig --> RestAPI
    WSNotify --> Monitoring
    Database --> Results

    %% Execution flow
    LocalBackend & DockerBackend & AwsBackend --> JobMgmt

    %% Styling
    classDef core fill:#d0e0ff,stroke:#0050a0;
    classDef pipe fill:#ffe0d0,stroke:#a05000;
    classDef conductor fill:#d0ffe0,stroke:#00a050;
    classDef ui fill:#ffd0e0,stroke:#a00050;

    class StarryNightCore core;
    class PipeCraftEngine pipe;
    class ConductorService conductor;
    class CanvasUI ui;
```

### Component Overview

**StarryNight Core**: The foundation library that provides specialized algorithms for microscopy image analysis

   - Image indexing and inventory management
   - Illumination correction, alignment, and preprocessing
   - Cell Painting analysis algorithms
   - Quality control and validation

**PipeCraft**: A pipeline compiler for defining and executing computational pipelines

   - Pipeline definition framework
   - Node-based processing graph
   - Multiple execution backends (local, Docker, AWS)
   - Template-based workflow generation

**Conductor**: A service for job management, monitoring, and API access

   - RESTful API for job control
   - Database for configuration and tracking results
   - Job scheduling and monitoring
   - Real-time updates via WebSockets

**Canvas**: A web-based user interface for interacting with the system

   - Project management interface
   - Job configuration and submission
   - Run monitoring and visualization
   - Results exploration

### Key Design Principles

- **Modularity**: Each component has clear boundaries and interfaces
- **Extensibility**: The system can be extended with new algorithms and processing modules
- **Reproducibility**: Workflows are version-controlled and traceable
- **Scalability**: Processing can scale from local development to cloud execution

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

### Prerequisites

- Git
- Python 3.10+
- Node.js 18+ (for Canvas frontend)
- Nix package manager (recommended)
- Docker (for containerized development)
- AWS CLI (for cloud integrations)

### Setup Steps

#### Option 1: Using Nix (Recommended)

```bash
# Clone the repository
git clone https://github.com/broadinstitute/starrynight.git
cd starrynight

# Set up the Nix environment
nix develop --extra-experimental-features nix-command --extra-experimental-features flakes .

# Synchronize Python dependencies
uv sync
```

#### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/broadinstitute/starrynight.git
cd starrynight

# Create and activate a Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages in development mode
pip install -e ".[dev]"
pip install -e starrynight/
pip install -e pipecraft/
pip install -e conductor/

# Set up the Canvas frontend
cd canvas
npm install
```

## Core Components and Design Patterns

### StarryNight Core

The foundation of the platform providing specialized algorithms for microscopy image analysis:

- **CLI Tools**: Command-line interfaces for each algorithm
- **Algorithms**: Image processing algorithms for microscopy data
- **Modules System**: Standardized module structure for algorithm implementation
- **Parsers**: File path parsing and metadata extraction
- **Utilities**: Common functions for file handling, data transformation, etc.

#### Data Flow Architecture

Data flows through the system following a standard pattern:

1. **Raw Data → Inventory**: Create catalog of all image files
2. **Inventory → Index**: Parse inventory to create structured index with metadata
3. **Index → Processing**: Run specific algorithms on indexed data
4. **Processing → Results**: Store and manage processing results

### PipeCraft

PipeCraft is the pipeline compiler, featuring:

- **Pipeline Definition**: Python API for defining computational workflows
- **Node System**: Individual processing steps as configurable nodes
- **Backend Abstraction**: Support for local, Docker, and AWS Batch execution
- **Template System**: Pre-defined templates for common backends

#### Workflow Design Patterns

PipeCraft implements:

- **Strategy Pattern**: Different execution strategies for different environments
- **Builder Pattern**: Constructing complex pipelines from simple building blocks
- **Composite Pattern**: Nested execution graphs for complex workflows

```python
# Pipeline construction example
from pipecraft.pipeline import Parallel, PyFunction, Seq
pipeline = Seq(
        [
            PyFunction("A", ["in path"], ["out path"]),
            Seq(
                [
                    PyFunction("B", ["in path"], ["out path"]),
                    PyFunction("C", ["in path"], ["out path"]),
                    Parallel(
                        [
                            Parallel(
                                [
                                    PyFunction("H", ["in path"], ["out path"]),
                                ]
                            ),
                            PyFunction("F", ["in path"], ["out path"]),
                            PyFunction("G", ["in path"], ["out path"]),
                        ]
                    ),
                ]
            ),
            PyFunction("D", ["in path"], ["out path"]),
        ]
    )
```

### Conductor

Conductor manages the execution environment:

- **REST API**: API for job management and monitoring
- **Database**: Storage for project configurations and job results
- **Job Management**: Scheduling, execution, and monitoring of jobs
- **WebSockets**: Real-time updates on job status

#### Service Architecture

Conductor implements:

- **Repository Pattern**: Data access abstraction for database operations
- **Service Layer Pattern**: Business logic encapsulation

### Canvas UI

The web-based user interface:

- **React Components**: Modular UI components
- **State Management**: Zustand for global state
- **API Integration**: SWR for data fetching
- **Responsive Design**: Mobile-friendly interfaces

#### Frontend Architecture

Canvas implements:

- **Atomic Design**: Component hierarchy from atoms to templates
- **Container-Presenter Pattern**: Separation of data and presentation
- **Hooks Pattern**: Reusable behavior implementations

## Running Tests

### Python Tests

```bash
# Run all tests
pytest

# Run tests for a specific package
pytest starrynight/tests/
pytest pipecraft/tests/
pytest conductor/tests/

# Run a specific test
pytest starrynight/tests/modules/test_gen_index.py::test_function_name
```

### Frontend Tests

```bash
cd canvas
npm run test
```

## Running Components Locally

### StarryNight Core

```bash
# Run StarryNight CLI directly
starrynight --help
```

### Conductor Service

```bash
# Start Conductor API service
cd conductor
fastapi dev ./src/conductor/main.py
```

### Canvas Frontend

```bash
cd canvas
npm run dev
# Access the UI at http://localhost:3000
```

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**: Implement your feature or fix

3. **Run tests**: Ensure functionality works as expected
   ```bash
   pytest
   ruff check .
   ```

4. **Commit changes**: Follow the project's commit conventions
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push changes**: Share your work
   ```bash
   git push -u origin feature/your-feature-name
   ```

6. **Create a pull request**: Submit your changes for review

## Coding Standards

### Python

- **Style**: Follow PEP 8 with a line length of 88 characters
- **Formatting**: Use ruff for code formatting
- **Type Hints**: Use type annotations for all function parameters and returns
- **Docstrings**: Use NumPy style docstrings
- **Imports**: Group imports (standard library, third-party, local)
- **Naming**: Use snake_case for variables/functions, PascalCase for classes

### TypeScript (Canvas)

- **Style**: Follow the project's TypeScript/React conventions
- **Formatting**: Use ESLint and Prettier
- **Types**: Define interfaces/types for all components and functions
- **Naming**: Use camelCase for variables/functions, PascalCase for components/interfaces

## Extending StarryNight

### Adding a New Module

To add a new processing module:

1. Create a new algorithm implementation in `starrynight/algorithms/`
2. Add CLI commands in `starrynight/cli/`
3. Implement module definition files in `starrynight/modules/`
4. Add tests for all components
5. Update documentation

Here's an example of creating a new module:

#### 1. Create the Algorithm

```python
# starrynight/algorithms/new_algorithm.py
import numpy as np
from typing import Dict, List, Optional

def process_image(image: np.ndarray, params: Dict) -> np.ndarray:
    """Process an image with the new algorithm.

    Parameters
    ----------
    image : np.ndarray
        Input image
    params : Dict
        Processing parameters

    Returns
    -------
    np.ndarray
        Processed image
    """
    # Algorithm implementation
    return processed_image
```

#### 2. Create CLI Command

```python
# starrynight/cli/new_algorithm.py
import click
from pathlib import Path
from starrynight.algorithms import new_algorithm

@click.command("new-algorithm")
@click.option("-i", "--input", type=str, required=True, help="Input file path")
@click.option("-o", "--output", type=str, required=True, help="Output directory")
@click.option("--param", type=float, default=1.0, help="Algorithm parameter")
def new_algorithm_command(input: str, output: str, param: float) -> None:
    """Run the new algorithm on input images."""
    # Command implementation
    pass
```

#### 3. Create Module Definition

```python
# starrynight/modules/new_algorithm/
# new_algorithm_module.py
from starrynight.modules.common import StarrynightModule

class NewAlgorithmModule(StarrynightModule):
    """Module for new algorithm processing."""

    @classmethod
    def from_config(cls, config: dict) -> "NewAlgorithmModule":
        return cls(**config)

    def _spec(self) -> dict:
        return {
            "version": "1.0.0",
            "parameters": {
                "input": {"type": "string", "description": "Input path"},
                "output": {"type": "string", "description": "Output path"},
                "param": {"type": "number", "default": 1.0, "description": "Algorithm parameter"}
            }
        }

    def build_pipeline(self) -> "Pipeline":
        # Define pipeline for this module
        pass
```

### Creating a New Pipeline

To create a new pipeline using existing modules:

1. Define a pipeline configuration
2. Create a pipeline definition in PipeCraft
3. Register the pipeline with the system

Example pipeline creation:

```python
# pipecraft/pipelines/my_pipeline.py
from pipecraft.pipeline import Seq
from pipecraft.node import Node
from starrynight.modules.new_algorithm_module import NewAlgorithmModule

def create_my_pipeline(config: dict) -> Pipeline:
    """Create a custom pipeline for image processing.

    Parameters
    ----------
    config : dict
        Pipeline configuration

    Returns
    -------
    Pipeline
        Configured pipeline
    """

    # Build pipeline
    pipeline = Seq([NewAlgorithmModule.from_config(config).pipe])

    return pipeline
```

### Extending Conductor

To add a new API endpoint:

1. Create a new route file in `conductor/deploy/local/routes/`
2. Implement handler functions in `conductor/handlers/`
3. Add models if needed in `conductor/models/`

### Extending Canvas

To add new UI components:

1. Create component files in `canvas/components/`
2. Update state management if needed
3. Add new routes if creating new pages

## Configuration and Error Handling

### Configuration Management

StarryNight uses a structured approach to configuration:

#### Schema Validation

All configuration is validated using `pydantic` schemas:

```python
# Example schema validation
from starrynight.schema import validate_schema

config = {
    "input": "/path/to/input",
    "output": "/path/to/output",
    "parameters": {
        "channel": "DAPI",
        "sample_size": 100
    }
}

# Validate against schema
errors = validate_schema(config, "module_schema.json")
if errors:
    raise ValueError(f"Invalid configuration: {errors}")
```

## Performance Optimization

### Parallel Processing

StarryNight supports parallel processing in several ways:

#### Task Parallelism

Pipeline nodes can be executed in parallel when dependencies allow:

```python
# Parallel pipeline

from pipecraft.pipeline import Parallel, PyFunction, Seq
pipeline = Seq(
        [
            PyFunction("A", ["in path"], ["out path"]),
            Seq(
                [
                    PyFunction("B", ["in path"], ["out path"]),
                    PyFunction("C", ["in path"], ["out path"]),
                    Parallel(
                        [
                            Parallel(
                                [
                                    PyFunction("H", ["in path"], ["out path"]),
                                ]
                            ),
                            PyFunction("F", ["in path"], ["out path"]),
                            PyFunction("G", ["in path"], ["out path"]),
                        ]
                    ),
                ]
            ),
            PyFunction("D", ["in path"], ["out path"]),
        ]
    )
```

#### Distributed Execution

Pipecraft supports execution across multiple compute resources:

- Local execution for development
- AWS Batch for cloud-scale processing
- Custom execution backends for specific environments

## Getting Help

If you need assistance, you can:

- Check the existing documentation
- Browse the source code
- Contact the core team at imaging@broadinstitute.org
- Join community discussions on the issue tracker

## Additional Resources

- GitHub repository: https://github.com/broadinstitute/starrynight
- Issue tracker: https://github.com/broadinstitute/starrynight/issues
- Development roadmap: See project milestones on GitHub
- Related tools: CellProfiler, ImageJ, NumPy, scikit-image
