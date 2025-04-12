# Processing Modules

!!! Warning
    - This document contains bot-generated text and has not yet been reviewed by developers!


This guide provides an overview of the processing modules available in StarryNight.

## Module Overview

StarryNight organizes functionality into distinct processing modules:

| Module                      | Purpose                      | Key Features                                         |
| --------------------------- | ---------------------------- | ---------------------------------------------------- |
| **Inventory**               | Catalog image files          | Fast file scanning, parallel processing              |
| **Index**                   | Extract metadata             | Path parsing, structure generation                   |
| **Illumination Correction** | Normalize illumination       | Per-channel correction, CellProfiler integration     |
| **Alignment**               | Register images              | Multi-channel alignment, cycle-to-cycle registration |
| **Preprocessing**           | Prepare images for analysis  | Background subtraction, artifact removal             |
| **Cell Painting Analysis**  | Cell segmentation & features | CellProfiler integration, feature extraction         |
| **Sequencing Analysis**     | Process sequencing data      | Barcode calling, cycle alignment                     |

## Module Workflow

Most StarryNight modules follow a similar three-step workflow:

1. **Generate LoadData files**: Create CSV files telling CellProfiler which images to process
2. **Generate pipeline files**: Create customized CellProfiler pipelines
3. **Execute pipelines**: Run CellProfiler with the generated files

## Inventory Module

The inventory module catalogs all image files in a dataset:

```sh
starrynight inventory gen -d INPUT_DIRECTORY -o OUTPUT_DIRECTORY
```

Key features:

- Fast parallel file scanning
- Parquet file format for efficient access
- Supports large datasets (millions of files)

## Index Module

The index module extracts structured metadata from file paths:

```sh
starrynight index gen -i INVENTORY_FILE -o OUTPUT_DIRECTORY
```

Key features:

- Extracts well, plate, channel information
- Uses a parser for consistent metadata extraction
- Creates a structured index for downstream processing

## Illumination Correction Module

The illumination correction module compensates for uneven illumination across the field of view:

```sh
# Generate LoadData files
starrynight illum calc loaddata -i INDEX_FILE -o OUTPUT_DIRECTORY

# Generate pipelines
starrynight illum calc cppipe -l LOADDATA_DIRECTORY -o PIPELINE_DIRECTORY -w WORKSPACE

# Execute pipelines
starrynight cp -p PIPELINE_DIRECTORY -l LOADDATA_DIRECTORY -o OUTPUT_DIRECTORY
```

## Alignment Module

The alignment module handles registration of images across different channels and cycles:

```sh
# Generate LoadData files
starrynight align loaddata -i INDEX_FILE -o OUTPUT_DIRECTORY

# Generate pipelines
starrynight align cppipe -l LOADDATA_DIRECTORY -o PIPELINE_DIRECTORY -w WORKSPACE

# Execute pipelines
starrynight cp -p PIPELINE_DIRECTORY -l LOADDATA_DIRECTORY -o OUTPUT_DIRECTORY
```

Key features:

- Multi-channel alignment
- Cycle-to-cycle registration
- Configurable reference channel

## Preprocessing Module

The preprocessing module prepares images for downstream analysis:

```sh
# Generate LoadData files
starrynight preprocess loaddata -i INDEX_FILE -o OUTPUT_DIRECTORY

# Generate pipelines
starrynight preprocess cppipe -l LOADDATA_DIRECTORY -o PIPELINE_DIRECTORY -w WORKSPACE

# Execute pipelines
starrynight cp -p PIPELINE_DIRECTORY -l LOADDATA_DIRECTORY -o OUTPUT_DIRECTORY
```

Key features:

- Background subtraction
- Image normalization
- Artifact removal
- Quality control

## Cell Painting Analysis Module

The cell painting module handles cell segmentation and feature extraction:

```sh
# Multiple steps for cell segmentation and feature extraction
# See CLI reference for detailed options
```

Key features:

- Cell segmentation
- Feature extraction
- Integration with CellProfiler

## Sequencing Analysis Module

The sequencing module processes sequencing-based image data:

```sh
# Multiple steps for cycle alignment and barcode calling
# See CLI reference for detailed options
```

Key features:

- Cycle alignment
- Barcode calling
- Sequence decoding

## Module Dependencies

Modules typically have dependencies on earlier modules:

```
Inventory → Index → Illumination Correction → Alignment → Preprocessing → Analysis
```

## Module Outputs

Each module produces specific outputs:

- **Inventory**: `inventory.parquet` file
- **Index**: `index.parquet` file
- **Illumination Correction**: `.npy` illumination function files
- **Alignment**: Aligned image files
- **Preprocessing**: Processed image files
- **Analysis**: Measurement and feature files

## Next Steps

- Read the detailed user guides for each of the modules
