# Quick Start Guide

This guide will walk you through running a basic illumination correction workflow with StarryNight.

## Prerequisites

Before starting, ensure you have:

- Installed StarryNight (see the [Installation Guide](installation.md))
- Sample data (see the [Installation Guide](installation.md))

## Step 1: Generate Inventory

First, create a catalog of all image files in your dataset:

```bash
# Generate the inventory
starrynight inventory gen \
    -d ./scratch/starrynight_example \
    -o ./scratch/workspace/inventory
```

This command will scan all files in the input directory and create an inventory file:

```
./scratch/workspace/inventory/
├── inv/                # Shard directory with temporary files
└── inventory.parquet   # Main inventory file
```

## Step 2: Generate Index

Next, parse the inventory to create a structured index with metadata:

```bash
starrynight index gen \
    -i ./scratch/workspace/inventory/inventory.parquet \
    -o ./scratch/workspace/index/
```

The result will be an `index.parquet` file containing structured metadata for each image.

## Step 3: Run Illumination Correction

### 3.1: Generate LoadData Files

Create CSV files for CellProfiler to load images:

```bash
starrynight illum calc loaddata \
    -i ./scratch/workspace/index/index.parquet \
    -o ./scratch/workspace/cellprofiler/loaddata/cp/illum/illum_calc
```

### 3.2: Generate CellProfiler Pipelines

Create CellProfiler pipeline files:

```bash
starrynight illum calc cppipe \
    -l ./scratch/workspace/cellprofiler/loaddata/cp/illum/illum_calc/ \
    -o ./scratch/workspace/cellprofiler/cppipe/cp/illum/illum_calc \
    -w ./scratch/workspace
```

### 3.3: Execute CellProfiler Pipelines

Run the pipelines to generate illumination correction files:

```bash
starrynight cp \
    -p ./scratch/workspace/cellprofiler/cppipe/cp/illum/illum_calc/ \
    -l ./scratch/workspace/cellprofiler/loaddata/cp/illum/illum_calc \
    -o ./scratch/workspace/illum/cp/illum_calc
```

## Step 4: Verify Results

The illumination correction files will be created in the output directory:

```
./scratch/workspace/illum/cp/illum_calc/
├── Batch1_Plate1_IllumOrigDAPI.npy
├── Batch1_Plate1_IllumOrigPhalloAF750.npy
└── Batch1_Plate1_IllumOrigZO1-AF488.npy
```

If you have Python with matplotlib installed, you can visualize the results:

```python
import numpy as np
import matplotlib.pyplot as plt

# Load one of the illumination correction files
data = np.load('./scratch/workspace/illum/cp/illum_calc/Batch1_Plate1_IllumOrigDAPI.npy')

# Create a visualization
plt.figure(figsize=(10,8))
plt.imshow(data, cmap='viridis')
plt.colorbar()
plt.title('DAPI Illumination Correction')
plt.show()
```

## Next Steps

- Learn about other [Processing Modules](user/modules.md)
- Understand [Core Concepts](user/core-concepts.md) of StarryNight
