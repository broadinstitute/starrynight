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

## Sample Data

For testing purposes, you can download the example dataset:

```bash
# Create a directory for the sample data
mkdir -p scratch

# Download sample data from S3 (if you have AWS CLI and access)
aws s3 sync s3://imaging-platform/projects/2024_03_12_starrynight/starrynight_example scratch/starrynight_example
```

<details>
A sampling of a dataset was first downloaded like this:

```bash
export S3_PATH="s3://BUCKET/projects/PROJECT/BATCH"

# Copy SBS images
parallel mkdir -p scratch/starrynight_example/Source1/Batch1/images/Plate1/20X_c{1}_SBS-{1}/ ::: 1 2 3 4 5 6 7 8 9 10

parallel --match '.*' --match '(.*) (.*) (.*)' aws s3 cp "${S3_PATH}/images/Plate1/20X_c{1}_SBS-{1}/Well{2.1}_Point{2.1}_{2.2}_ChannelC,A,T,G,DAPI_Seq{2.3}.ome.tiff" "scratch/starrynight_example/Source1/Batch1/images/Plate1/20X_c{1}_SBS-{1}/" ::: 1 2 3 4 5 6 7 8 9 10 ::: "A1 0000 0000" "A1 0001 0001" "A2 0000 1025" "A2 0001 1026" "B1 0000 3075" "B1 0001 3076"

# Copy Cell Painting images
mkdir -p scratch/starrynight_example/Source1/Batch1/images/20X_CP_Plate1_20240319_122800_179

parallel --match '(.*) (.*) (.*)' aws s3 cp "${S3_PATH}/images/Plate1/20X_CP_Plate1_20240319_122800_179/Well{1.1}_Point{1.1}_{1.2}_ChannelPhalloAF750,ZO1-AF488,DAPI_Seq{1.3}.ome.tiff" "scratch/starrynight_example/Source1/Batch1/images/Plate1/20X_CP_Plate1_20240319_122800_179/" ::: "A1 0000 0000" "A1 0001 0001" "A2 0000 1025" "A2 0001 1026" "B1 0000 3075" "B1 0001 3076"

```

To keep data sizes manageable for this tutorial, the original files were compressed with this command, resulting in a 50x lossy compression:

```bash!
find . -type f -name "*.ome.tiff" | parallel 'magick {} -compress jpeg -quality 80 {= s/\.ome\.tiff$/.compressed.tiff/ =}'
find . -type f -name "*.ome.tiff" -exec rm {} +
```

</details>

## Next Steps

- Continue to the [Quick Start Guide](quickstart.md) to run your first analysis
- Learn about [Core Concepts](../user/core-concepts.md) of the StarryNight platform
