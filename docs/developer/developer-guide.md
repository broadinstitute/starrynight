# Developer Guide

This guide provides information for developers who want to contribute to StarryNight.

## Repository Structure

The StarryNight repository is organized as a monorepo with three main packages:

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
nix develop --extra-experimental-features nix-command --extra-experimental-features flakes

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

## Core Components

### StarryNight Core

The foundation of the platform providing specialized algorithms for microscopy image analysis:

- **CLI Tools**: Command-line interfaces for each algorithm
- **Algorithms Module**: Image processing algorithms for microscopy data
- **Modules System**: Standardized module structure for algorithm implementation
- **Parsers**: File path parsing and metadata extraction
- **Utilities**: Common functions for file handling, data transformation, etc.

### PipeCraft

PipeCraft is the workflow engine, featuring:

- **Pipeline Definition**: Python API for defining computational workflows
- **Node System**: Individual processing steps as configurable nodes
- **Backend Abstraction**: Support for local, Docker, and AWS Batch execution
- **Template System**: Pre-defined templates for common workflows

### Conductor & Canvas UI

Conductor manages the execution environment:

- **REST API**: API for job management and monitoring
- **Database**: Storage for project configurations and job results
- **Job Management**: Scheduling, execution, and monitoring of jobs
- **Canvas UI**: Web interface for managing the system

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
python -m starrynight.cli.main --help
```

### Conductor Service

```bash
# Start Conductor API service
python -m conductor.cli.main start
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

## Adding a New Module

To add a new processing module:

1. Create a new algorithm implementation in `starrynight/algorithms/`
2. Add CLI commands in `starrynight/cli/`
3. Implement module definition files in `starrynight/modules/`
4. Add tests for all components
5. Update documentation

## Getting Help

If you need assistance, you can:

- Check the existing documentation
- Browse the source code
- Contact the core team at imaging@broadinstitute.org

## Additional Resources

- GitHub repository: https://github.com/broadinstitute/starrynight
- Issue tracker: https://github.com/broadinstitute/starrynight/issues
