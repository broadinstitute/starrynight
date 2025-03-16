# Illumination Correction CLI Workflow

This guide demonstrates how to use StarryNight's CLI to perform illumination correction on Cell Painting images. Illumination correction compensates for uneven illumination across the field of view, which is essential for accurate image analysis.

## Prerequisites

Before following this guide, ensure you've completed the [setup steps](setup.md) which include:
- Setting up your environment
- Creating a test dataset
- Generating inventory and index files

This guide assumes you have an index file at `./workspace/index/index.parquet`.

## Sample Test Data

If you need sample data to follow along, you can use:

```bash
# Create test data directory
mkdir -p scratch

# Download example files
aws s3 sync s3://imaging-platform/projects/2024_03_12_starrynight/starrynight_example scratch/starrynight_example

# Optional: Download reference output files to compare your results
aws s3 sync s3://imaging-platform/projects/2024_03_12_starrynight/starrynight_example_workspace scratch/starrynight_example_workspace_reference
```

> Note: The sample data uses compressed TIFF files (compressed with `convert` using JPEG compression at 80% quality) to keep data sizes manageable.

## Illumination Correction Workflow

Illumination correction in StarryNight is performed in three steps:

1. Generate CellProfiler LoadData files
2. Generate CellProfiler pipeline files
3. Execute the CellProfiler pipelines

### Step 1: Generate CellProfiler LoadData Files

First, create CSV files that CellProfiler will use to load and process images:

```bash
starrynight illum calc loaddata \
    -i ./workspace/index/index.parquet \
    -o ./workspace/cellprofiler/loaddata/cp/illum/illum_calc
```

**Parameters:**
- `-i`: Path to the index.parquet file
- `-o`: Output directory for the LoadData CSV files

**Expected Output:**
```
./workspace/cellprofiler/loaddata/cp/illum/illum_calc
└── Batch1
    └── illum_calc_Batch1_Plate1.csv
```

The generated CSV files contain paths to the images that will be used for illumination correction, organized by batch and plate.

### Step 2: Generate CellProfiler Pipelines

Next, create CellProfiler pipeline files (.cppipe) that define the illumination correction workflow:

```bash
starrynight illum calc cppipe \
    -l ./workspace/cellprofiler/loaddata/cp/illum/illum_calc/ \
    -o ./workspace/cellprofiler/cppipe/cp/illum/illum_calc \
    -w ./workspace
```

**Parameters:**
- `-l`: Directory containing the LoadData CSV files
- `-o`: Output directory for the pipeline files
- `-w`: Workspace directory path

**Expected Output:**
```
./workspace/cellprofiler/cppipe/cp/illum/illum_calc
└── Batch1
    └── illum_calc_Batch1_Plate1.cppipe
```

These pipeline files contain CellProfiler modules configured to generate illumination correction files for each channel.

### Step 3: Execute CellProfiler Pipeline

Finally, run the CellProfiler pipelines to generate illumination correction files:

```bash
starrynight cp \
    -p ./workspace/cellprofiler/cppipe/cp/illum/illum_calc/ \
    -l ./workspace/cellprofiler/loaddata/cp/illum/illum_calc \
    -o ./workspace/illum/cp/illum_calc
```

**Parameters:**
- `-p`: Directory containing the pipeline files
- `-l`: Directory containing the LoadData CSV files
- `-o`: Output directory for illumination correction files

**Expected Output:**
```
./workspace/illum/cp/illum_calc
├── Batch1_Plate1_IllumOrigDAPI.npy
├── Batch1_Plate1_IllumOrigPhalloAF750.npy
└── Batch1_Plate1_IllumOrigZO1-AF488.npy
```

These `.npy` files contain the illumination correction functions for each channel, which can be applied to correct images in subsequent processing steps.

## Visualizing Results

To visualize an illumination correction file, you can use this Python snippet:

```python
import numpy as np
import matplotlib.pyplot as plt

# Load the illumination correction file
data = np.load('./workspace/illum/cp/illum_calc/Batch1_Plate1_IllumOrigDAPI.npy')

# Create a visualization
plt.figure(figsize=(10,8))
plt.imshow(data, cmap='viridis')
plt.colorbar()
plt.title('DAPI Illumination Correction')
plt.show()
```

## Next Steps

After generating illumination correction files, you can:

1. Apply illumination correction to your images
2. Proceed with alignment or segmentation
3. Use the correction files in a complete pipeline

See the [Applying Illumination Correction](apply-illumination.md) guide for the next steps.
