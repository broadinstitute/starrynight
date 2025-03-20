# Quick Start Guide

This guide will walk you through running a basic illumination correction workflow with StarryNight.

## Prerequisites

Before starting, ensure you have installed StarryNight (see the [Installation Guide](installation.md))


## Step 0: Download sample data

Download this example dataset:

```bash
# Create a directory for the sample data
mkdir -p scratch

# Download sample data from S3 (if you have AWS CLI and access)
aws s3 sync s3://imaging-platform/projects/2024_03_12_starrynight/starrynight_example scratch/starrynight_example
```

<details markdown="1">

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

```bash
find . -type f -name "*.ome.tiff" | parallel 'magick {} -compress jpeg -quality 80 {= s/\.ome\.tiff$/.compressed.tiff/ =}'
find . -type f -name "*.ome.tiff" -exec rm {} +
```

</details>

Before running any commands, set up your data and workspace directories as environment variables for convenience:

```bash
export DATADIR='./scratch/starrynight_example_input'
export WKDIR='./scratch/starrynight_example_output/workspace'
```

## Step 1: Generate Inventory

First, create a catalog of all image files in your dataset:

```bash
# Generate the inventory
starrynight inventory gen \
    -d ${DATADIR} \
    -o ${WKDIR}/inventory
```

This command will scan all files in the input directory and create an inventory file:

```
${WKDIR}/inventory/
├── inv/                # Shard directory with temporary files
└── inventory.parquet   # Main inventory file
```

## Step 2: Generate Index

Next, parse the inventory to create a structured index with metadata:

```bash
starrynight index gen \
    -i ${WKDIR}/inventory/inventory.parquet \
    -o ${WKDIR}/index/
```

The result will be an `index.parquet` file containing structured metadata for each image.

> **Note**:


## Step 3: Run Illumination Correction

### 3.1: Generate LoadData Files

Create CSV files for CellProfiler to load images:

```bash
starrynight illum calc loaddata \
    -i ${WKDIR}/index/index.parquet \
    -o ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_calc
```

### 3.2: Generate CellProfiler Pipelines

Create CellProfiler pipeline files:

```bash
starrynight illum calc cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_calc/ \
    -o ${WKDIR}/cellprofiler/cppipe/cp/illum/illum_calc \
    -w ${WKDIR}
```

### 3.3: Execute CellProfiler Pipelines

Run the pipelines to generate illumination correction files:

```bash
starrynight cp \
    -p ${WKDIR}/cellprofiler/cppipe/cp/illum/illum_calc/ \
    -l ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_calc \
    -o ${WKDIR}/illum/cp/illum_calc
```

## Step 4: Verify Results

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

- Learn about other [Processing Modules](../user/modules.md)
- Understand [Core Concepts](../user/core-concepts.md) of StarryNight
