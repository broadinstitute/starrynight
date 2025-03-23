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
export WKDIR='./scratch/starrynight_example_output/workspace'
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

```bash
# Generate LoadData files
starrynight illum calc loaddata \
    -i ${WKDIR}/index/index.parquet \
    -o ${WKDIR}/cellprofiler/loaddata/sbs/illum/illum_calc \
    --sbs

# Generate CellProfiler pipelines
starrynight illum calc cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/sbs/illum/illum_calc/ \
    -o ${WKDIR}/cellprofiler/cppipe/sbs/illum/illum_calc \
    -w ${WKDIR} \
    --sbs

# Execute pipelines
starrynight cp \
    -p ${WKDIR}/cellprofiler/cppipe/sbs/illum/illum_calc/ \
    -l ${WKDIR}/cellprofiler/loaddata/sbs/illum/illum_calc \
    -o ${WKDIR}/illum/sbs/illum_calc \
    --sbs
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

```bash
# Generate LoadData files
starrynight illum apply loaddata \
    -i ${WKDIR}/index/index.parquet \
    -o ${WKDIR}/cellprofiler/loaddata/sbs/illum/illum_apply \
    --sbs

# Generate CellProfiler pipelines
starrynight illum apply cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/sbs/illum/illum_apply \
    -o ${WKDIR}/cellprofiler/cppipe/sbs/illum/illum_apply \
    -w ${WKDIR} \
    --sbs

# Execute pipelines
starrynight cp \
    -p ${WKDIR}/cellprofiler/cppipe/sbs/illum/illum_apply \
    -l ${WKDIR}/cellprofiler/loaddata/sbs/illum/illum_apply \
    -o ${WKDIR}/illum/sbs/illum_apply \
    --sbs
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

## Step 3. Image Alignment

Image alignment is a critical step SBS images, ensuring that images from different cycles are spatially aligned.

This step registers all images from different cycles using the nuclei channel as a reference. The alignment process generates transformed images with consistent spatial coordinates across all cycles, which is crucial for accurately matching cells across multiple imaging rounds.

```bash
# Generate LoadData files for alignment
starrynight align loaddata \
    -i ${WKDIR}/index/index.parquet \
    -o ${WKDIR}/cellprofiler/loaddata/sbs/align \
    -c ${WKDIR}/illum/sbs/illum_apply/ \
    --nuclei DAPI

# Generate CellProfiler pipelines for alignment
starrynight align cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/sbs/align \
    -o ${WKDIR}/cellprofiler/cppipe/sbs/align \
    -w ${WKDIR}/align/sbs \
    --nuclei DAPI

# Execute alignment pipelines
starrynight cp \
    -p ${WKDIR}/cellprofiler/cppipe/sbs/align \
    -l ${WKDIR}/cellprofiler/loaddata/sbs/align \
    -o ${WKDIR}/align/sbs \
    --sbs \
    --jobs 1
```

## Step 4. Preprocessing and Barcode Calling

Preprocessing prepares your images for final analysis by performing barcode calling on SBS images.

This step performs the following operations:

1. Cell segmentation based on nuclear and cytoplasmic markers
2. Feature enhancement to identify barcode spots
3. Color compensation across channels
4. Barcode calling to match detected signals to known barcode sequences
5. Association of barcodes with segmented cells

```bash
# Set input directory with barcode information
export INPUT_WKDIR='./scratch/starrynight_example_input/Source1/workspace'

# Generate LoadData files for preprocessing
starrynight preprocess loaddata \
    -i ${WKDIR}/index/index.parquet \
    -o ${WKDIR}/cellprofiler/loaddata/sbs/preprocess/ \
    -c ${WKDIR}/illum/sbs/illum_apply/ \
    -a ${WKDIR}/align/sbs/ \
    -n DAPI

# Generate CellProfiler pipelines for preprocessing
starrynight preprocess cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/sbs/preprocess/ \
    -o ${WKDIR}/cellprofiler/cppipe/sbs/preprocess/ \
    -w ${WKDIR}/preprocess/sbs/ \
    -b ${INPUT_WKDIR}/metadata/Barcodes.csv \
    -n DAPI

# Execute preprocessing pipelines
starrynight cp \
    -p ${WKDIR}/cellprofiler/cppipe/sbs/preprocess \
    -l ${WKDIR}/cellprofiler/loaddata/sbs/preprocess \
    -o ${WKDIR}/preprocess/sbs/ \
    --sbs
```

Module-specific parameters:

- `-a, --align_images`: Path to aligned images from the previous step
- `-b, --barcode`: Path to the barcode CSV file that defines barcode sequences

## Step 5. Final Analysis

The final analysis step processes the preprocessed images to extract cellular measurements and generate the dataset for downstream analysis.

This step generates the final dataset with:

1. Comprehensive cell morphology measurements
2. Intensity measurements for all channels across all cells
3. Barcode identity associations with cells
4. Quality control metrics for all analyzed objects

```bash
# Generate LoadData files for analysis
starrynight analysis loaddata \
    -i ${WKDIR}/index/index.parquet \
    -o ${WKDIR}/cellprofiler/loaddata/sbs/analysis/ \
    -c ${WKDIR}/illum/sbs/illum_apply/ \
    -p ${WKDIR}/preprocess/sbs/

# Generate CellProfiler pipelines for analysis
starrynight analysis cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/sbs/analysis/ \
    -o ${WKDIR}/cellprofiler/cppipe/sbs/analysis/ \
    -w ${WKDIR}/analysis/sbs/ \
    -b ${INPUT_WKDIR}/metadata/Barcodes.csv \
    --nuclei DAPI \
    --cell PhalloAF750 \
    --mito ZO1-AF488

# Execute analysis pipelines
starrynight cp \
    -p ${WKDIR}/cellprofiler/cppipe/sbs/analysis \
    -l ${WKDIR}/cellprofiler/loaddata/sbs/analysis \
    -o ${WKDIR}/analysis/sbs/ \
    --sbs
```

Module-specific parameters:

- `-a, --align_images`: Path to aligned images from the previous step
- `-b, --barcode`: Path to the barcode CSV file that defines barcode sequences

## How Quality Control Works

The pre-segmentation check identifies confluent regions in images and creates masks to exclude regions unsuitable for segmentation. The post-segmentation check performs nuclei and cell identification using optimized parameters and generates overlay images highlighting segmentation results for visual validation.

## FIXME Output Files

- Illumination Correction
    - `.npy` files containing correction functions (e.g., `Batch1_Plate1_IllumOrigDAPI.npy`)
    - 16-bit TIFF files with corrected images
- Quality Control
    - CSV files with quality metrics
    - TIFF images with segmentation overlays (post-segmentation check)
- Image Alignment                                                                                                                                                                         │ │
    - Aligned TIFF images with consistent spatial coordinates across cycles                                                                                                               │ │
    - Transformation matrices for each image registration                                                                                                                                 │ │
- Preprocessing                                                                                                                                                                           │ │
    - Compensated image files for each channel and cycle                                                                                                                                  │ │
    - CSV files with barcode call information                                                                                                                                             │ │
    - Overlay images showing cell segmentation and barcode spots                                                                                                                          │ │
- Analysis                                                                                                                                                                                │ │
    - CSV files with comprehensive cell measurements (shape, intensity, texture)                                                                                                          │ │
    - Visualization images with cell outlines and identified features                                                                                                                     │ │
    - Barcode-cell association data for downstream analysis

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

### Alignment Issues

- Verify that the nuclei channel (DAPI) has sufficient signal and contrast
- Check that images from different cycles have similar quality
- For poor alignment, consider increasing the number of registration points
- For memory errors, reduce the batch size by editing the loaddata files

### Barcode Calling Issues

- Verify that the barcode CSV file has the correct format with sgRNA and gene_symbol columns
- Ensure that barcode sequences match the expected pattern from your experiment
- For low confidence barcode calls, adjust intensity thresholds in preprocessing
- Check for spectral bleedthrough that might affect barcode signal quality

## Next Steps

- Perform statistical analysis on the extracted features
- Visualize results using your preferred analysis tools
- Export processed data for integration with other analysis platforms

## Conclusion

You have now completed a full StarryNight pipeline, from ingesting raw image data to producing structured analysis results. This example demonstrates the core workflow for processing and analyzing high-content screening data:

1. Create an inventory of your raw image files
2. Generate an index with extracted metadata
3. Perform illumination correction to normalize image intensity
4. Run quality control to ensure reliable segmentation
5. Align images across cycles (for sequence-based screening)
6. Preprocess images and perform barcode calling
7. Run final analysis to extract comprehensive measurements
