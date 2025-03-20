# Image Processing Pipeline Example

This guide walks through a complete example of processing microscopy images using StarryNight's key modules.

## Prerequisites

Before starting this workflow, you need:

- A generated inventory and index (see [Quick Start Guide](../getting-started/quickstart.md))
- Sufficient disk space for intermediate and output files

## Pipeline Overview

This example demonstrates a typical workflow:

1. Illumination correction to normalize lighting across images
2. Quality control checks before and after segmentation
3. Cell segmentation and feature extraction

Most StarryNight modules follow a consistent three-step pattern:

1. **Generate LoadData files**: Create CSV files that tell CellProfiler which images to process
2. **Generate pipeline files**: Create customized CellProfiler pipelines
3. **Execute pipelines**: Run CellProfiler with the generated files

Before running any commands, set up your workspace directory as an environment variable for convenience:

```bash
export WKDIR='./scratch/starrynight_example/workspace'
```

## Step 1: Illumination Correction

Illumination correction compensates for uneven lighting across the field of view, improving segmentation accuracy and feature extraction.

### Calculate Correction Functions

First, generate correction functions for each channel:

```bash
# Generate LoadData files
starrynight illum calc loaddata \
    -i ${WKDIR}/index/index.parquet \
    -o ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_calc

# Generate CellProfiler pipelines
starrynight illum calc cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_calc/ \
    -o ${WKDIR}/cellprofiler/cppipe/cp/illum/illum_calc \
    -w ${WKDIR}

# Execute pipelines
starrynight cp \
    -p ${WKDIR}/cellprofiler/cppipe/cp/illum/illum_calc/ \
    -l ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_calc \
    -o ${WKDIR}/illum/cp/illum_calc
```

Module-specific parameters:

- `--channels`: comma-separated list of channels to process (e.g., `--channels DAPI,PhalloAF750`)
- `--sample-size`: Number of images to sample per channel for correction calculation

### Apply Corrections

Next, apply the correction functions to your images:

```bash
# Generate LoadData files
starrynight illum apply loaddata \
    -i ${WKDIR}/index/index.parquet \
    -o ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_apply

# Generate CellProfiler pipelines
starrynight illum apply cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_apply \
    -o ${WKDIR}/cellprofiler/cppipe/cp/illum/illum_apply \
    -w ${WKDIR}

# Execute pipelines
starrynight cp \
    -p ${WKDIR}/cellprofiler/cppipe/cp/illum/illum_apply \
    -l ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_apply \
    -o ${WKDIR}/illum/cp/illum_apply
```

Module-specific parameters:

- `--illum`: Path to illumination correction files (default: auto-detected)
- `--sbs`: Flag for sequence-based screening images (default: False)

## Step 2: Quality Control

Quality control modules evaluate image and segmentation quality to ensure optimal results.

### Pre-segmentation Check

Pre-segmentation checking evaluates whether images are suitable for segmentation before investing computational resources:

```bash
# Generate LoadData files
starrynight presegcheck loaddata \
    -i ${WKDIR}/index/index.parquet \
    -o ${WKDIR}/cellprofiler/loaddata/cp/presegcheck \
    -c ${WKDIR}/illum/cp/illum_apply

# Generate CellProfiler pipelines
starrynight presegcheck cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/cp/presegcheck/ \
    -o ${WKDIR}/cellprofiler/cppipe/cp/presegcheck \
    -w ${WKDIR} \
    --nuclei DAPI \
    --cell PhalloAF750

# Execute pipelines
starrynight cp \
    -p ${WKDIR}/cellprofiler/cppipe/cp/presegcheck \
    -l ${WKDIR}/cellprofiler/loaddata/cp/presegcheck \
    -o ${WKDIR}/presegcheck/cp/
```

> **Note**: There is a known inconsistency in the CLI interface - the `-n` and `-c` parameters are required in the `presegcheck cppipe` command but not in the `presegcheck loaddata` command.
> Further, the flag `-c` is the shorthand for two different flats.
> These implementation quirks will be fixed in a future release.

### Post-segmentation Check

Segmentation checking validates the quality of completed segmentation, providing metrics and visualizations:

```bash
# Generate LoadData files
starrynight segcheck loaddata \
    -i ${WKDIR}/index/index.parquet \
    -o ${WKDIR}/cellprofiler/loaddata/cp/segcheck \
    -c ${WKDIR}/illum/cp/illum_apply \
    --nuclei DAPI \
    --cell PhalloAF750


# Generate CellProfiler pipelines
starrynight segcheck cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/cp/segcheck/ \
    -o ${WKDIR}/cellprofiler/cppipe/cp/segcheck \
    -w ${WKDIR} \
    --nuclei DAPI \
    --cell PhalloAF750

# Execute pipelines
starrynight cp \
    -p ${WKDIR}/cellprofiler/cppipe/cp/segcheck \
    -l ${WKDIR}/cellprofiler/loaddata/cp/segcheck \
    -o ${WKDIR}/segcheck/cp/
```

## FIXME How Quality Control Works

The pre-segmentation check identifies confluent regions in images and creates masks to exclude regions unsuitable for segmentation. The post-segmentation check performs nuclei and cell identification using optimized parameters and generates overlay images highlighting segmentation results for visual validation.

## Output Files

Each step produces specific outputs:

- Illumination Correction
    - `.npy` files containing correction functions (e.g., `Batch1_Plate1_IllumOrigDAPI.npy`)
    - 16-bit TIFF files with corrected images
- Quality Control
    - CSV files with quality metrics
    - TIFF images with segmentation overlays (post-segmentation check)

## Common Parameters

Throughout the pipeline, you'll use these common parameters:

- `-i, --index`: Path to the index.parquet file
- `-o, --output`: Output directory for generated files
- `-w, --workspace`: Path to the workspace directory
- `-l, --loaddata`: Path to LoadData CSV files
- `-p, --pipeline`: Path to CellProfiler pipeline directory
- `-m, --path_mask`: Path prefix mask to use when resolving image paths
- `-c, --corr_images`: Path to illumination-corrected images
- `-n, --nuclei`: Channel to use for nuclei segmentation (e.g., "DAPI")
- `-c, --cell`: Channel to use for cell segmentation (e.g., "PhalloAF750")

## FIXME Troubleshooting

### Illumination Correction Issues

- Check that channel names in the index match your expectations
- Verify images exist for all channels
- Ensure sufficient memory for processing
- For CellProfiler errors, check CellProfiler log files

### Quality Control Issues

- Check for focus issues in original images
- Verify illumination correction was properly applied
- Adjust nuclei and cell channels if necessary
- For over-confluent regions, consider adjusting threshold parameters
- Review CellProfiler logs for pipeline errors

## Next Steps

- Proceed with full cell segmentation
- Extract and analyze features
- View results in the Canvas UI
