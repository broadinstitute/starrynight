# Getting Started with StarryNight

This guide will help you install StarryNight and run your first illumination correction workflow.

## Installation

StarryNight uses the Nix package manager to provide a consistent and reproducible environment:

1. **Install Nix** (if not already installed):

        sh <(curl -L https://nixos.org/nix/install) --daemon


1. **Clone the Repository**:

        git clone https://github.com/broadinstitute/starrynight.git
        cd starrynight

2. **Set Up the Environment**:

        nix develop --extra-experimental-features nix-command --extra-experimental-features flakes .

3. **Synchronize Dependencies**:

        uv sync

4. **Verify Installation**:

        starrynight --help
        pipecraft --help
        conductor --help

## Quick Start Workflow

This section walks you through running a basic illumination correction workflow.

### Step 0: Download Sample Data

```sh
# Create a directory for the sample data
mkdir -p scratch

# Download sample data from S3 (if you have AWS CLI and access)
aws s3 sync s3://imaging-platform/projects/2024_03_12_starrynight/starrynight_example_input scratch/starrynight_example_input
```

Before running any commands, set up your data and workspace directories as environment variables:

```sh
export DATADIR='./scratch/starrynight_example_input'
export WKDIR='./scratch/starrynight_example_output/workspace'
```

### Step 1: Generate Inventory

Create a catalog of all image files in your dataset:

```sh
# Generate the inventory
starrynight inventory gen \
    -d ${DATADIR} \
    -o ${WKDIR}/inventory
```

This command will create an inventory file:

```
${WKDIR}/inventory/
├── inv/                # Shard directory with temporary files
└── inventory.parquet   # Main inventory file
```

### Step 2: Generate Index

Parse the inventory to create a structured index with metadata:

```sh
starrynight index gen \
    -i ${WKDIR}/inventory/inventory.parquet \
    -o ${WKDIR}/index/
```

The result will be an `index.parquet` file containing structured metadata for each image.

### Step 3: Run Illumination Correction

#### 3.1: Generate LoadData Files

```sh
starrynight illum calc loaddata \
    -i ${WKDIR}/index/index.parquet \
    -o ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_calc
```

#### 3.2: Generate CellProfiler Pipelines

```sh
starrynight illum calc cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_calc/ \
    -o ${WKDIR}/cellprofiler/cppipe/cp/illum/illum_calc \
    -w ${WKDIR}
```

#### 3.3: Execute CellProfiler Pipelines

```sh
starrynight cp \
    -p ${WKDIR}/cellprofiler/cppipe/cp/illum/illum_calc/ \
    -l ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_calc \
    -o ${WKDIR}/illum/cp/illum_calc
```

### Step 4: Verify Results

The illumination correction files will be created in the output directory:

```
${WKDIR}/illum/cp/illum_calc/
├── Batch1_Plate1_IllumOrigDAPI.npy
├── Batch1_Plate1_IllumOrigPhalloAF750.npy
└── Batch1_Plate1_IllumOrigZO1-AF488.npy
```

If you have Python with matplotlib installed, you can visualize the results:

```python
import numpy as np
import matplotlib.pyplot as plt

# Load one of the illumination correction files
import os
wkdir = os.environ.get('WKDIR', './scratch/starrynight_example/workspace')
data = np.load(f'{wkdir}/illum/cp/illum_calc/Batch1_Plate1_IllumOrigDAPI.npy')

# Create a visualization
plt.figure(figsize=(10,8))
plt.imshow(data, cmap='viridis')
plt.colorbar()
plt.title('DAPI Illumination Correction')
plt.show()
```

## Next Steps

- Learn about [Core Concepts](core-concepts.md) of the StarryNight platform
- Explore available [Processing Modules](modules.md)
- Try an [end-to-end pipeline example](example-pipeline-cli.md)
