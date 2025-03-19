# Segmentation Checking

This guide explains how to use the segmentation checking modules in StarryNight.

## Prerequisites

Before using the segmentation checking modules, you need:

- A generated inventory and index (see [Quick Start Guide](../getting-started/quickstart.md))
- Illumination-corrected images (see [Illumination Correction](illumination-correction.md))
- Sufficient disk space for intermediate and output files

## Overview

The segmentation checking process in StarryNight:

1. **Pre-segmentation Checking (PreSegCheck)**: Evaluates image quality before segmentation
2. **Segmentation Checking (SegCheck)**: Validates segmentation quality after cell identification

Both modules analyze images to ensure optimal segmentation quality, helping researchers identify and address issues early in the pipeline.

## Module 1: Pre-segmentation Checking

Pre-segmentation checking evaluates whether images are suitable for segmentation before investing computational resources in the full process.

### 1.1. Generate CellProfiler LoadData Files

This step creates CSV files that tell CellProfiler which images to check:

```bash
starrynight presegcheck loaddata \
    -i ./scratch/starrynight_example/workspace/index/index.parquet \
    -o ./scratch/starrynight_example/workspace/cellprofiler/loaddata/cp/presegcheck \
    -c ./scratch/starrynight_example/workspace/illum/cp/illum_apply
```

Parameters:

- `-i, --index`: Path to the index.parquet file
- `-o, --out`: Output directory for the LoadData CSV files
- `-c, --corr_images`: Path to illumination-corrected images
- `-m, --path_mask`: Path prefix mask to use when resolving image paths

### 1.2. Generate CellProfiler Pipelines

This step creates CellProfiler pipeline files (.cppipe) customized for your dataset:

```bash
starrynight presegcheck cppipe \
    -l ./scratch/starrynight_example/workspace/cellprofiler/loaddata/cp/presegcheck/ \
    -o ./scratch/starrynight_example/workspace/cellprofiler/cppipe/cp/presegcheck \
    -w ./scratch/starrynight_example/workspace \
    -n DAPI \
    -c PhalloAF750
```

Parameters:

- `-l, --loaddata`: Path to the LoadData CSV files directory
- `-o, --out`: Output directory for the CellProfiler pipelines
- `-w, --workspace`: Path to the workspace directory
- `-n, --nuclei`: Channel to use for nuclei segmentation (e.g., "DAPI")
- `-c, --cell`: Channel to use for cell segmentation (e.g., "PhalloAF750")

### 1.3. Execute CellProfiler Pipelines

This step runs the generated CellProfiler pipelines to analyze image quality:

```bash
starrynight cp \
    -p ./scratch/starrynight_example/workspace/cellprofiler/cppipe/cp/presegcheck \
    -l ./scratch/starrynight_example/workspace/cellprofiler/loaddata/cp/presegcheck \
    -o ./scratch/starrynight_example/workspace/presegcheck/cp/
```

Parameters:

- `-p, --pipeline`: Path to the CellProfiler pipeline directory
- `-l, --loaddata`: Path to the LoadData CSV files directory
- `-o, --output`: Output directory for the pre-segmentation check results

### Output Files

The pre-segmentation check produces:
- CSV files with image quality metrics

## Module 2: Segmentation Checking

Segmentation checking evaluates the quality of completed segmentation, providing validation and metrics.

### 2.1. Generate CellProfiler LoadData Files

This step creates CSV files that tell CellProfiler which images to validate:

```bash
starrynight segcheck loaddata \
    -i ./scratch/starrynight_example/workspace/index/index.parquet \
    -o ./scratch/starrynight_example/workspace/cellprofiler/loaddata/cp/segcheck \
    -c ./scratch/starrynight_example/workspace/illum/cp/illum_apply \
```

Parameters:

- `-i, --index`: Path to the index.parquet file
- `-o, --out`: Output directory for the LoadData CSV files
- `-c, --corr_images`: Path to illumination-corrected images
- `-m, --path_mask`: Path prefix mask to use when resolving image paths

### 2.2. Generate CellProfiler Pipelines

This step creates CellProfiler pipeline files (.cppipe) for segmentation validation:

```bash
starrynight segcheck cppipe \
    -l ./scratch/starrynight_example/workspace/cellprofiler/loaddata/cp/segcheck/ \
    -o ./scratch/starrynight_example/workspace/cellprofiler/cppipe/cp/segcheck \
    -w ./scratch/starrynight_example/workspace \
    -n DAPI \
    -c PhalloAF750
```

Parameters:

- `-l, --loaddata`: Path to the LoadData CSV files directory
- `-o, --out`: Output directory for the CellProfiler pipelines
- `-w, --workspace`: Path to the workspace directory
- `-n, --nuclei`: Channel to use for nuclei segmentation
- `-c, --cell`: Channel to use for cell segmentation

### 2.3. Execute CellProfiler Pipelines

This step runs the pipelines to perform segmentation quality checking:

```bash
starrynight cp \
    -p ./scratch/starrynight_example/workspace/cellprofiler/cppipe/cp/segcheck \
    -l ./scratch/starrynight_example/workspace/cellprofiler/loaddata/cp/segcheck \
    -o ./scratch/starrynight_example/workspace/segcheck/cp/
```

Parameters:

- `-p, --pipeline`: Path to the CellProfiler pipeline directory
- `-l, --loaddata`: Path to the LoadData CSV files directory
- `-o, --output`: Output directory for the segmentation check results

### Output Files

The segmentation check produces:

- CSV files with segmentation quality metrics
- TIFF images with overlaid segmentation outlines for visual validation
- Metrics for cell and nuclei identification (count, size, distribution)

## FIXME: How Segmentation Checking Works

### Pre-segmentation Algorithm

The pre-segmentation check:

1. Identifies confluent regions in images
2. Creates masks to exclude regions unsuitable for segmentation
3. Performs initial nuclei and cell identification
4. Computes quality metrics to predict segmentation success

### Segmentation Check Algorithm

The segmentation check:

1. Performs nuclei and cell identification using optimized parameters
2. Analyzes object counts, sizes, and distributions
3. Generates overlay images highlighting segmentation results
4. Exports measurements for quality assessment

## Troubleshooting

Common issues:

**Poor quality metrics in pre-segmentation**

- Check for focus issues in original images
- Verify illumination correction was properly applied
- Adjust nuclei and cell channels if necessary

**Segmentation errors in visualization**

- Adjust threshold parameters in the CellProfiler pipeline
- Verify the correct nuclei and cell channels are specified
- Check for over-confluent regions that may need exclusion

## Next Steps

- Adjust CellProfiler pipelines for your specific needs
- Filter images based on segmentation check results
- Proceed with full segmentation and analysis on validated images
