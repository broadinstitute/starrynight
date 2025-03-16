# Developer Getting Started Guide

This guide helps new developers set up their environment and understand how to work with the StarryNight codebase.

## Repository Structure

StarryNight is organized as a monorepo containing three main Python packages:

1. **starrynight/**: Core scientific algorithms and image processing modules
2. **pipecraft/**: Pipeline definition and execution framework
3. **conductor/**: API server and orchestration layer
4. **canvas/**: Web UI (Next.js frontend)

## Prerequisites

- Python 3.10+
- Git
- [Nix](https://nixos.org/download.html) (for reproducible development environment)
- [UV](https://github.com/astral-sh/uv) (modern Python package management)

## Setting Up Your Development Environment

### 1. Clone the Repository

```bash
git clone git@github.com:broadinstitute/starrynight.git
cd starrynight
```

### 2. Set Up the Development Environment

StarryNight uses Nix flakes to create a reproducible development environment:

```bash
# Enable required experimental features
nix develop --extra-experimental-features nix-command --extra-experimental-features flakes
```

This command sets up a shell with all required dependencies including Python, libraries, and tools.

### 3. Install Python Dependencies

```bash
# Once inside the Nix shell, synchronize dependencies
uv sync
```

### 4. Install in Development Mode

To work on the packages and have your changes immediately reflected:

```bash
# Install all packages in development mode
uv pip install -e .
```

## Key Directories and Files

### StarryNight Package

```
starrynight/
├── src/starrynight/
│   ├── algorithms/       # Core image processing algorithms
│   ├── cli/              # CLI command definitions
│   ├── modules/          # Reusable processing modules
│   ├── parsers/          # File path parsing utilities
│   ├── pipelines/        # Pipeline definitions
│   └── experiments/      # Experiment configurations
└── tests/                # Unit and integration tests
```

### Pipecraft Package

```
pipecraft/
├── src/pipecraft/
│   ├── backend/          # Pipeline execution backends
│   ├── pipeline.py       # Pipeline classes
│   └── node.py           # Node interface definition
└── tests/                # Unit tests
```

### Conductor Package

```
conductor/
├── src/conductor/
│   ├── models/           # Database models
│   ├── handlers/         # Business logic
│   ├── deploy/           # API routes and server
│   └── cli/              # CLI for conductor
└── tests/                # Unit and integration tests
```

## Development Workflow

### Running Tests

```bash
# Run all tests
python -m pytest

# Run tests for a specific package
python -m pytest starrynight/tests/

# Run a specific test
python -m pytest starrynight/tests/path/to/test_file.py::TestClass::test_function
```

### Code Quality

```bash
# Run linting
python -m ruff check

# Run type checking
basedpyright
```

### Building Packages

```bash
# Build all packages
python -m build
```

## Core Concepts for Developers

### 1. Scientific Modules

StarryNight's algorithms are wrapped as modules that implement the Pipecraft Node interface, allowing them to be composed into pipelines.

### 2. Pipeline Framework

Pipecraft defines pipelines as directed acyclic graphs (DAGs) of computational nodes, with backends that translate these abstract pipelines into concrete execution plans.

### 3. Database Models

Conductor uses SQLAlchemy models to represent projects, jobs, and runs in its database.

### 4. API Design

The REST API follows a resource-oriented design, with handlers that implement business logic for each resource.

## Contributing

When making changes:

1. Write tests for your new functionality
2. Add docstrings following NumPy style
3. Use type hints consistently
4. Run linting and type checking before committing

## Next Steps

- Review the [system architecture](../architecture.md) which includes data flow information
- See [CLI examples](../user/cli-workflows/illumination-correction.md)
- Explore the [core concepts](../concepts/overview.md)
