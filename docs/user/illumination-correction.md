# Illumination Correction

This guide explains how to use the illumination correction module in StarryNight.

## Overview

The illumination correction process in StarryNight:

1. Identifies and collects representative images
2. Calculates illumination correction functions for each channel
3. Applies these corrections to normalize illumination across all images

## Prerequisites

Before using the illumination correction module, you need:

- A generated inventory and index (see [Quick Start Guide](quickstart.md))
- Sufficient disk space for intermediate and output files

## Workflow Steps

The illumination correction workflow consists of three main steps:

### 1. Generate CellProfiler LoadData Files

This step creates CSV files that tell CellProfiler which images to use for calculating illumination functions:

```bash
starrynight illum calc loaddata \
    -i /path/to/index/index.parquet \
    -o /path/to/output/cellprofiler/loaddata/cp/illum/illum_calc
```

Parameters:

- `-i, --index`: Path to the index.parquet file
- `-o, --output`: Output directory for the LoadData CSV files
- `--channels`: Optional comma-separated list of channels to process
- `--sample-size`: Number of images to sample per channel

### 2. Generate CellProfiler Pipelines

This step creates CellProfiler pipeline files (.cppipe) customized for your dataset:

```bash
starrynight illum calc cppipe \
    -l /path/to/output/cellprofiler/loaddata/cp/illum/illum_calc/ \
    -o /path/to/output/cellprofiler/cppipe/cp/illum/illum_calc \
    -w /path/to/workspace
```

Parameters:

- `-l, --loaddata`: Path to the LoadData CSV files directory
- `-o, --output`: Output directory for the CellProfiler pipelines
- `-w, --workspace`: Path to the workspace directory

### 3. Execute CellProfiler Pipelines

This step runs the generated CellProfiler pipelines to calculate illumination correction functions:

```bash
starrynight cp \
    -p /path/to/output/cellprofiler/cppipe/cp/illum/illum_calc/ \
    -l /path/to/output/cellprofiler/loaddata/cp/illum/illum_calc \
    -o /path/to/output/illum/cp/illum_calc
```

Parameters:

- `-p, --pipeline`: Path to the CellProfiler pipeline directory
- `-l, --loaddata`: Path to the LoadData CSV files directory
- `-o, --output`: Output directory for the illumination correction files

## Output Files

The illumination correction process produces:

- `.npy` files containing illumination correction functions for each channel
- Example: `Batch1_Plate1_IllumOrigDAPI.npy`

## Applying Illumination Correction

After generating illumination correction functions, you can apply them to your images using a similar workflow:

```bash
# Generate LoadData files for applying correction
starrynight illum apply loaddata -i INDEX_FILE -o OUTPUT_DIRECTORY -c CORRECTION_DIRECTORY

# Generate CellProfiler pipelines
starrynight illum apply cppipe -l LOADDATA_DIRECTORY -o PIPELINE_DIRECTORY -w WORKSPACE

# Execute pipelines
starrynight cp -p PIPELINE_DIRECTORY -l LOADDATA_DIRECTORY -o OUTPUT_DIRECTORY
```

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
