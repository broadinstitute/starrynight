# Installation Guide

This guide provides detailed instructions for installing the StarryNight platform and its dependencies.

## System Requirements

- **Operating System**: Linux (recommended) or macOS
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB+ recommended
- **Storage**: 10GB for installation, additional space for data
- **Python**: 3.10 or later
- **Node.js**: 18.0 or later (for Canvas UI)

## Installation Options

StarryNight can be installed using several methods:

### Option 1: Using Nix (Recommended)

The Nix package manager provides a consistent and reproducible environment:

1. **Install Nix** (if not already installed):
   ```bash
   sh <(curl -L https://nixos.org/nix/install) --daemon
   ```

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/broadinstitute/starrynight.git
   cd starrynight
   ```

3. **Set Up the Environment**:
   ```bash
   nix develop --extra-experimental-features nix-command --extra-experimental-features flakes
   ```

4. **Synchronize Dependencies**:
   ```bash
   uv sync
   ```

### Option 2: Using Python Virtual Environment

For a more traditional Python installation:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/broadinstitute/starrynight.git
   cd starrynight
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the Packages**:
   ```bash
   pip install -e ".[dev]"
   pip install -e starrynight/
   pip install -e pipecraft/
   pip install -e conductor/
   ```

4. **Set Up Canvas UI** (optional):
   ```bash
   cd canvas
   npm install
   ```

## Verifying Installation

Test your installation:

1. **Check CLI Tools**:
   ```bash
   starrynight --version
   pipecraft --version
   conductor --version
   ```

2. **Run a Simple Command**:
   ```bash
   starrynight --help
   ```

## Sample Data

For testing purposes, you can download the example dataset:

```bash
# Create a directory for the sample data
mkdir -p scratch

# Download sample data from S3 (if you have AWS CLI and access)
aws s3 sync s3://imaging-platform/projects/2024_03_12_starrynight/starrynight_example scratch/starrynight_example
```

## Next Steps

- Continue to the [Quick Start Guide](quickstart.md) to run your first analysis
- Learn about [Core Concepts](core-concepts.md) of the StarryNight platform
