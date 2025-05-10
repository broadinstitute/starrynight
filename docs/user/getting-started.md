# Getting Started with StarryNight

This guide will help you install StarryNight and run your first illumination correction workflow using the CLI (Command Line Interface) approach.

!!! note "CLI vs Module Layer Approach"
    **Direct CLI Commands** (shown in this guide): This is a simpler, more direct approach good for learning and exploration. It involves manual execution of individual commands with limited containerization and workflow automation.

    **Module-based Approach** (used in production): This provides standardized components with consistent interfaces, containerized execution for reproducibility, advanced workflow composition, automatic parameter inference, and integration with the Canvas UI.

    This guide focuses on the CLI approach. For production use cases, see the [Architecture Overview](../architecture/00_architecture_overview.md) and [Module Layer](../architecture/03_module_layer.md) documentation.

## Installation

StarryNight uses the Nix package manager to provide a consistent and reproducible environment:

1. **Install Nix** (if not already installed):

        sh <(curl -L https://nixos.org/nix/install) --daemon


2. **Clone the Repository**:

        git clone https://github.com/broadinstitute/starrynight.git
        cd starrynight

3. **Set Up the Environment**:

        nix develop --extra-experimental-features nix-command --extra-experimental-features flakes .

4. **Install Dependencies and Project**:

        # First get basic dependencies
        uv sync

        # Then install the project in editable mode with development tools
        uv pip install -e ".[dev]"

5. **Verify Installation**:

        starrynight --help
        pipecraft --help
        conductor --help

## For Developers

If you're developing for StarryNight, the setup process is the same as above. For detailed information on the project architecture and how to extend components, see the [Architecture Overview](../architecture/00_architecture_overview.md).

## Quick Start Workflow

This section walks you through running a basic illumination correction workflow.

### Step 1: Download Sample Data

```sh
# Create a directory for the sample data
mkdir -p scratch

# Download sample data from S3 (if you have AWS CLI and access)
aws s3 sync s3://imaging-platform/projects/2024_03_12_starrynight/starrynight_example_input scratch/starrynight_example_input
```

Before running any commands, set up your data and workspace directories as environment variables:

```sh
export DATADIR='./scratch/starrynight_example_input'
export WKDIR='./scratch/starrynight_example_output/workspace'
```

### Step 2: Create Experiment Configuration

The experiment configuration file defines parameters for your processing workflow:

First, ensure the directories exist:

```sh
# Create necessary directories for the workflow
mkdir -p scratch/starrynight_example_output/workspace/
```

```sh
# Generate a default experiment configuration template
starrynight exp init -e  "Pooled CellPainting [Generic]" -o ${WKDIR}
```

This creates an `experiment_init.json` file in your workspace that you can edit to match your dataset's characteristics:

FIXME: `sbs_cell_channel` and `sbs_mito_channel` should not need to be specified in the `experiment_init.json` file.

```json
{
    "barcode_csv_path": ".",
    "use_legacy": false,
    "cp_img_overlap_pct": 10,
    "cp_img_frame_type": "round",
    "cp_acquisition_order": "snake",
    "sbs_img_overlap_pct": 10,
    "sbs_img_frame_type": "round",
    "sbs_acquisition_order": "snake",
    "cp_nuclei_channel": "DAPI",
    "cp_cell_channel": "PhalloAF750",
    "cp_mito_channel": "ZO1AF488",
    "sbs_nuclei_channel": "DAPI",
    "sbs_cell_channel": "PhalloAF750",
    "sbs_mito_channel": "ZO1AF488"
}
```

Adjust the values to match your experiment setup.

### Step 3: Generate Inventory

Create a catalog of all image files in your dataset:

```sh
# Generate the inventory
starrynight inventory gen \
    -d ${DATADIR} \
    -o ${WKDIR}/inventory
```

This command will create an inventory file:

```
${WKDIR}/inventory/
├── inv/                # Shard directory with temporary files
└── inventory.parquet   # Main inventory file
```

### Step 4: Generate Index

Parse the inventory to create a structured index with metadata:

```sh
starrynight index gen \
    -i ${WKDIR}/inventory/inventory.parquet \
    -o ${WKDIR}/index/
```

The result will be an `index.parquet` file containing structured metadata for each image.

### Step 5: Create Experiment File

Initialize an experiment using your index and configuration:

```sh
starrynight exp new \
    -i ${WKDIR}/index/index.parquet \
    -e "Pooled CellPainting [Generic]" \
    -c ${WKDIR}/experiment_init.json \
    -o ${WKDIR}
```

This creates an `experiment.json` file with dataset-specific parameters derived from your index.

### Step 6: Run Illumination Correction

First, ensure the directories exist:

```sh
mkdir -p ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_calc/
```

!!! note "Pipeline Generation Approaches"
    StarryNight offers two ways to generate CellProfiler pipelines:

    - **Pre-fabricated Pipelines**: Uses established, tested pipeline templates (add `--use_legacy` flag)
    - **Dynamic Generation**: Automatically generates pipelines based on configuration (omit the `--use_legacy` flag)

    This guide uses the pre-fabricated approach for stability.

**Generate LoadData Files:**

```sh
# Generate loaddata files using established pipeline templates
starrynight illum calc loaddata \
    -i ${WKDIR}/index/index.parquet \
    -o ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_calc \
    --exp_config ${WKDIR}/experiment.json \
    --use_legacy
```

**Generate CellProfiler Pipelines:**

```sh
# Generate CellProfiler pipeline files using established templates
starrynight illum calc cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_calc/ \
    -o ${WKDIR}/cellprofiler/cppipe/cp/illum/illum_calc \
    -w ${WKDIR} \
    --use_legacy
```

**Execute CellProfiler Pipelines:**

```sh
# The path must point to a specific .cppipe file, not a directory
starrynight cp \
    -p ${WKDIR}/cellprofiler/cppipe/cp/illum/illum_calc/illum_calc_painting.cppipe \
    -l ${WKDIR}/cellprofiler/loaddata/cp/illum/illum_calc \
    -o ${WKDIR}/illum/cp/illum_calc
```


### Step 7: Verify Results

The illumination correction files will be created in the output directory:

```
${WKDIR}/illum/cp/illum_calc/
├── Plate1_IllumDNA.npy
├── Plate1_IllumPhalloidin.npy
└── Plate1_IllumZO1.npy
```

If you have Python with matplotlib installed, you can visualize the results:

```python
import numpy as np
import matplotlib.pyplot as plt

# Load one of the illumination correction files
import os
wkdir = os.environ.get('WKDIR', './scratch/starrynight_example/workspace')
data = np.load(f'{wkdir}/illum/cp/illum_calc/Plate1_IllumDNA.npy')

# Create a visualization
plt.figure(figsize=(10,8))
plt.imshow(data, cmap='viridis')
plt.colorbar()
plt.title('DNA Illumination Correction')
plt.show()
```

## Advanced CLI Options

StarryNight commands support additional options to customize processing:

### Path Masking

Filter files with path masks using the `-m/--path_mask` option:

```sh
starrynight illum calc loaddata -m "Batch1/Plate1" ...
```

### Parallel Processing

Control the number of parallel jobs with the `-j/--jobs` option:

```sh
# Run with 8 parallel jobs (default is 50)
starrynight cp -j 8 -p /path/to/pipeline.cppipe ...
```

### CellProfiler Plugins

Specify a directory containing CellProfiler plugins:

```sh
starrynight cp -d /path/to/plugins -p /path/to/pipeline.cppipe ...
```

## Next Steps

- Learn about [Core Concepts](core-concepts.md) of the StarryNight platform
- Explore available [Processing Modules](modules.md)
- Try an [end-to-end pipeline example](example-pipeline-cli.md)
- Check the architecture docs to understand the [system structure](../architecture/00_architecture_overview.md)


!!! info "For Document Contributors"
    This section contains editorial guidelines for maintaining this document. These guidelines are intended for contributors and maintainers, not end users.

    ### Purpose and Audience

    - **Introductory Focus** - This document is a user's first hands-on experience with StarryNight
    - **CLI Emphasis** - Prioritize the CLI approach as an accessible entry point
    - **Single Path with Options** - Present one primary workflow while noting alternatives
    - **Assumed Knowledge** - Users understand basic command line but not StarryNight architecture

    ### Structure Principles

    1. **Linear numbered steps** - Maintain a clear, sequential progression (Steps 1-7)
    2. **Notes for alternatives** - Use MkDocs admonitions to present alternatives without disrupting flow
    3. **Quick start spirit** - Keep explanations brief and focused on practical execution
    4. **Progressive detail** - Start with setup, then basic workflow, then advanced options
    5. **Clear prerequisites** - Ensure directory creation and dependencies are explicitly mentioned

    ### Content Style Guidelines

    1. **Command formatting** - Include descriptive comments in code blocks
    2. **Bold subheadings** - Use bold text rather than deeper heading levels for substeps
    3. **Copy-pastable commands** - Ensure commands work as written without modification
    4. **Environment variables** - Use consistent variables (DATADIR, WKDIR)
    5. **Expected outputs** - Show example outputs and file structures where appropriate

    ### Terminology Consistency

    - "CLI approach" vs "Module-based approach" - Different ways to use StarryNight
    - "Pre-fabricated pipelines" vs "Dynamic pipeline generation" - Two pipeline generation methods
    - "Workflow" - The end-to-end image processing sequence
    - "Pipeline" - The CellProfiler processing definition
    - "LoadData files" - CSV files that tell CellProfiler which images to process
