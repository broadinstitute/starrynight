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

   ```bash
   starrynight --help
   pipecraft --help
   conductor --help
   ```

## Next Steps

- Continue to the [Quick Start Guide](quickstart.md) to run your first analysis
- Learn about [Core Concepts](../user/core-concepts.md) of the StarryNight platform
