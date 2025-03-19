# Illumination Correction

This guide explains how to use the illumination correction module in StarryNight.

## Prerequisites

Before using the illumination correction module, you need:

- A generated inventory and index (see [Quick Start Guide](../getting-started/quickstart.md))
- Sufficient disk space for intermediate and output files

## Overview

The illumination correction process in StarryNight:

1. Identifies and collects representative images
2. Calculates illumination correction functions for each channel
3. Applies these corrections to normalize illumination across all images

It comprises two modules:

1. **Illumination Function Calculation** (`illum calc`) - Generates correction functions
2. **Illumination Function Application** (`illum apply`) - Applies corrections to images

Each module follows a similar three-step workflow.

## Module 1: Calculating Illumination Functions

### 1.1. Generate CellProfiler LoadData Files

This step creates CSV files that tell CellProfiler which images to use for calculating illumination functions:

```bash
starrynight illum calc loaddata \
    -i ./scratch/starrynight_example/workspace/index/index.parquet \
    -o ./scratch/starrynight_example/workspace/cellprofiler/loaddata/cp/illum/illum_calc
```

Parameters:

- `-i, --index`: Path to the index.parquet file
- `-o, --output`: Output directory for the LoadData CSV files
- `--channels`: Optional comma-separated list of channels to process
- `--sample-size`: Number of images to sample per channel

### 1.2. Generate CellProfiler Pipelines

This step creates CellProfiler pipeline files (.cppipe) customized for your dataset:

```bash
starrynight illum calc cppipe \
    -l ./scratch/starrynight_example/workspace/cellprofiler/loaddata/cp/illum/illum_calc/ \
    -o ./scratch/starrynight_example/workspace/cellprofiler/cppipe/cp/illum/illum_calc \
    -w ./scratch/starrynight_example/workspace
```

Parameters:

- `-l, --loaddata`: Path to the LoadData CSV files directory
- `-o, --output`: Output directory for the CellProfiler pipelines
- `-w, --workspace`: Path to the workspace directory

### 1.3. Execute CellProfiler Pipelines

This step runs the generated CellProfiler pipelines to calculate illumination correction functions:

```bash
starrynight cp \
    -p ./scratch/starrynight_example/workspace/cellprofiler/cppipe/cp/illum/illum_calc/ \
    -l ./scratch/starrynight_example/workspace/cellprofiler/loaddata/cp/illum/illum_calc \
    -o ./scratch/starrynight_example/workspace/illum/cp/illum_calc
```

Parameters:

- `-p, --pipeline`: Path to the CellProfiler pipeline directory
- `-l, --loaddata`: Path to the LoadData CSV files directory
- `-o, --output`: Output directory for the illumination correction files

### Output Files

The calculation process produces:

- `.npy` files containing illumination correction functions for each channel
- Example: `Batch1_Plate1_IllumOrigDAPI.npy`

## Module 2: Applying Illumination Correction

After generating illumination correction functions, you apply them to your images using a similar workflow:

### 2.1. Generate CellProfiler LoadData Files

This step creates CSV files that tell CellProfiler which images to apply corrections to:

```bash
starrynight illum apply loaddata \
    -i ./scratch/starrynight_example/workspace/index/index.parquet \
    -o ./scratch/starrynight_example/workspace/cellprofiler/loaddata/cp/illum/illum_apply
```

Parameters:

- `-i, --index`: Path to the index.parquet file
- `-o, --out`: Output directory for the LoadData CSV files
- `--illum`: Path to the illumination correction files directory (default: auto-detected as "index/../illum/cp/illum_calc")
- `-m, --path_mask`: Path prefix mask to use when resolving image paths
- `--sbs`: Flag for treating as sequence-based screening images (default: False)

### 2.2. Generate CellProfiler Pipelines

This step creates CellProfiler pipeline files (.cppipe) for applying corrections:

```bash
starrynight illum apply cppipe \
    -l ./scratch/starrynight_example/workspace/cellprofiler/loaddata/cp/illum/illum_apply \
    -o ./scratch/starrynight_example/workspace/cellprofiler/cppipe/cp/illum/illum_apply \
    -w ./scratch/starrynight_example/workspace
```

Parameters:

- `-l, --loaddata`: Path to the LoadData CSV files directory
- `-o, --out`: Output directory for the CellProfiler pipelines
- `-w, --workspace`: Path to the workspace directory
- `--sbs`: Flag for treating as sequence-based screening images (default: False)

### 2.3. Execute CellProfiler Pipelines

This step runs the pipelines to apply corrections to all images:

```bash
starrynight cp \
    -p ./scratch/starrynight_example/workspace/cellprofiler/cppipe/cp/illum/illum_apply \
    -l ./scratch/starrynight_example/workspace/cellprofiler/loaddata/cp/illum/illum_apply \
    -o ./scratch/starrynight_example/workspace/illum/cp/illum_apply
```

Parameters:

- `-p, --cppipe_path`: Path to the CellProfiler pipeline directory
- `-l, --load_data_path`: Path to the LoadData CSV files directory
- `-o, --path`: Output directory for the corrected images

### Output Files

The application process produces:

- 16-bit TIFF files with illumination-corrected images
- Regular image naming: `{batch}_{plate}_Well_{well}_Site_{site}_{CorrChannel}`
- SBS image naming: `{batch}_{plate}_{cycle}_Well_{well}_Site_{site}_{CorrChannel}`

## Troubleshooting

Common issues:

**Missing channels in output files**

   - Check that channel names in the index match your expectations
   - Verify that images exist for all channels

 **CellProfiler errors**

   - Check CellProfiler log files
   - Ensure you have enough memory for processing

**Poor quality illumination correction**

   - Increase the sample size for more representative correction
   - Check for outlier images

## Next Steps

- Continue to the alignment module if needed
- Proceed to preprocessing
- View results in the Canvas UI
