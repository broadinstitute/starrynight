# starrynight: Optical Pooled Screening Workflow Guide

This guide provides documentation for the starrynight image processing system for optical pooled screening. 
The system consists of 10 different modules, and this document currently shows how to use the illumination correction module alone.

## One-Time Setup Steps

These steps are performed once regardless of which module you're using.

### Creating a Test Dataset

First, create a test fixture with a single plate of Cell Painting images:

1. Copy sample files from S3:
   ```bash
   mkdir -p scratch
   aws s3 sync s3://imaging-platform/projects/2024_03_12_starrynight/starrynight_example scratch/starrynight_example
   ```

2. Organize them in the following structure:
   ```
   scratch/starrynight_example/Source1/Batch1/images/
   └── Plate1
       └── 20X_CP_Plate1_20240319_122800_179
           ├── WellA1_PointA1_0000_ChannelPhalloAF750,ZO1-AF488,DAPI_Seq0000.ome.tiff
           ├── WellA1_PointA1_0001_ChannelPhalloAF750,ZO1-AF488,DAPI_Seq0001.ome.tiff
           ├── WellA2_PointA2_0000_ChannelPhalloAF750,ZO1-AF488,DAPI_Seq1025.ome.tiff
           ├── WellA2_PointA2_0001_ChannelPhalloAF750,ZO1-AF488,DAPI_Seq1026.ome.tiff
           ├── WellB1_PointB1_0000_ChannelPhalloAF750,ZO1-AF488,DAPI_Seq3075.ome.tiff
           └── WellB1_PointB1_0001_ChannelPhalloAF750,ZO1-AF488,DAPI_Seq3076.ome.tiff
   ```

### Clone the Repository
```bash
git clone git@github.com:broadinstitute/starrynight.git
```

### Setup the Environment
```bash
cd starrynight
nix develop --extra-experimental-features nix-command --extra-experimental-features flakes
uv sync 
```

### Generate the Inventory

Create a listing of all image files in the dataset:

```bash
starrynight inventory gen \
    -d ./scratch/starrynight_example \
    -o ./scratch/starrynight_example_workspace/inventory
```

**Expected Output:**
```
./scratch/starrynight_example_workspace/inventory
├── inv
│   ├── inventory_0_cpeuwixtgl.parquet
│   ├── inventory_0_klqcqzwrur.parquet
│   └── [Additional shard files...]
└── inventory.parquet
```

> **Note:** The main output is `inventory.parquet`, which is a consolidated file. The other files in the `inv` directory are shards used during processing.

### Generate the Index

Parse the inventory to create a structured index with metadata for each image:

```bash
starrynight index gen \
    -i ./scratch/starrynight_example_workspace/inventory/inventory.parquet \
    -o ./scratch/starrynight_example_workspace/index/
```

**Expected Output:**
```
./scratch/starrynight_example_workspace/index/
└── index.parquet
```

The `index.parquet` file contains structured metadata for each image, e.g.,:

```text
duckdb -line -c 'select * from "./scratch/starrynight_example_workspace/index/index.parquet" limit 1;'

          key = starrynight_example/Source1/Batch1/images/Plate1/20X_CP_Plate1_20240319_122800_179/WellA2_PointA2_0000_ChannelPhalloAF750,ZO1-AF488,DAPI_Seq1025.ome.tiff
       prefix = scratch
   dataset_id = starrynight-example
     batch_id = Batch1
     plate_id = Plate1
     cycle_id = 
magnification = 20
      well_id = A2
      site_id = 1025
 channel_dict = [PhalloAF750, ZO1-AF488, DAPI]
     filename = WellA2_PointA2_0000_ChannelPhalloAF750,ZO1-AF488,DAPI_Seq1025.ome.tiff
    extension = tiff
 is_sbs_image = false
     is_image = true
       is_dir = false
```

Note: 
When running on macOS, you may see error messages about `.DS_Store` files. 
These are hidden files created by macOS Finder. 
The parser cannot handle filenames starting with a dot, but these errors can be safely ignored. 
The indexing process will continue successfully and create a complete index of your actual data files.
If desired, you can remove these files with `find /path/to/data -name ".DS_Store" -delete`, but it's not necessary as they don't affect the final result.

## Module 1: Illumination Correction

This module generates illumination correction files to account for uneven illumination across the field of view in Cell Painting images.

### Step 1: Generate CellProfiler LoadData Files for Illumination Correction

Create CSV files that CellProfiler will use to load and process images:

```bash
starrynight illum calc loaddata \
    -i ./scratch/starrynight_example_workspace/index/index.parquet \
    -o ./scratch/starrynight_example_workspace/cellprofiler/loaddata/cp/illum/illum_calc
```

**Expected Output:**
```
./scratch/starrynight_example_workspace/cellprofiler/loaddata/cp/illum/illum_calc
└── Batch1
    └── illum_calc_Batch1_Plate1.csv
```

### Step 2: Generate CellProfiler Pipelines for Illumination Correction

Create CellProfiler pipeline files (.cppipe) that define the illumination correction workflow:

```bash
starrynight illum calc cppipe \
    -l ./scratch/starrynight_example_workspace/cellprofiler/loaddata/cp/illum/illum_calc/ \
    -o ./scratch/starrynight_example_workspace/cellprofiler/cppipe/cp/illum/illum_calc \
    -w ./scratch/starrynight_example_workspace
```

**Expected Output:**
```
./scratch/starrynight_example_workspace/cellprofiler/cppipe/cp/illum/illum_calc
└── Batch1
    └── illum_calc_Batch1_Plate1.cppipe
```

### Step 3: Execute CellProfiler Pipeline for Illumination Correction

Run the CellProfiler pipelines to generate illumination correction files:

```bash
starrynight cp \
    -p ./scratch/starrynight_example_workspace/cellprofiler/cppipe/cp/illum/illum_calc/ \
    -l ./scratch/starrynight_example_workspace/cellprofiler/loaddata/cp/illum/illum_calc \
    -o ./scratch/starrynight_example_workspace/illum/cp/illum_calc
```

**Expected Output:**
```
./scratch/starrynight_example_workspace/illum/cp/illum_calc
├── Batch1_Plate1_IllumOrigDAPI.npy
├── Batch1_Plate1_IllumOrigPhalloAF750.npy
└── Batch1_Plate1_IllumOrigZO1-AF488.npy
```

### Visualizing Results

To visualize an illumination correction file, you can use this Python snippet:

```python
import numpy as np
import matplotlib.pyplot as plt

# Load the illumination correction file
data = np.load('scratch/starrynight_example_workspace/illum/cp/illum_calc/Batch1_Plate1_IllumOrigDAPI.npy')

# Create a visualization
plt.figure(figsize=(10,8))
plt.imshow(data, cmap='viridis')
plt.colorbar()
plt.title('DAPI Illumination Correction')
plt.show()
```
