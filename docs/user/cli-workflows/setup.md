# Setting Up for StarryNight CLI Workflows

This guide covers the essential setup steps required before running any StarryNight module. These steps include environment setup, dataset preparation, and generating the inventory and index.

## Prerequisites

- Python 3.10 or higher
- StarryNight packages installed
- Access to a microscopy image dataset

## Environment Setup

### Using Nix (Recommended)

The most reliable way to set up your environment is using Nix, which ensures all dependencies are correctly installed:

```bash
# Clone the repository if you haven't already
git clone git@github.com:broadinstitute/starrynight.git
cd starrynight

# Enter the development environment
nix develop --extra-experimental-features nix-command --extra-experimental-features flakes

# Synchronize dependencies
uv sync
```

### Alternative: Direct Installation

If you cannot use Nix, you can install StarryNight directly:

```bash
pip install git+https://github.com/broadinstitute/starrynight.git
```

## Dataset Preparation

StarryNight works best with datasets organized according to a consistent structure. A typical organization might look like:

```
dataset/
└── Source1/
    └── Batch1/
        └── images/
            └── Plate1/
                └── 20X_CP_Plate1_20240319_122800_179/
                    ├── WellA1_PointA1_0000_Channel*.tiff
                    ├── WellA1_PointA1_0001_Channel*.tiff
                    └── ...
```

## Creating a Workspace

Before processing, create a workspace directory to store outputs:

```bash
mkdir -p my_workspace
```

## Generating the Inventory

The first step in any StarryNight workflow is to generate an inventory of all files in your dataset:

```bash
starrynight inventory gen \
    -d /path/to/dataset \
    -o my_workspace/inventory
```

This command recursively scans the dataset directory and creates:
- `my_workspace/inventory/inventory.parquet`: The main inventory file
- `my_workspace/inventory/inv/`: Directory containing inventory shards

## Generating the Index

Next, parse the inventory to create a structured index:

```bash
starrynight index gen \
    -i my_workspace/inventory/inventory.parquet \
    -o my_workspace/index
```

This creates `my_workspace/index/index.parquet`, which contains structured metadata for each file.

## Verifying Your Index

To verify your index has been created correctly, you can examine it using pandas:

```python
import pandas as pd

# Load the index
index = pd.read_parquet('my_workspace/index/index.parquet')

# Display sample records
print(index.head())

# Count images by plate
print(index.groupby('plate_id').size())
```

## Common Issues

### .DS_Store Files on macOS

When running on macOS, you may see error messages about `.DS_Store` files. These are hidden files created by macOS Finder and can be safely ignored. The parser cannot handle filenames starting with a dot, but this won't affect processing of your actual data files.

To remove these files if desired:
```bash
find /path/to/dataset -name ".DS_Store" -delete
```

### Missing Files

If your dataset is incomplete or has an unexpected structure, the index may not contain all the files you expect. Verify your dataset structure matches what the parser expects.

## Next Steps

Once you have completed these setup steps, you can proceed to running specific modules:

- [Illumination Correction Workflow](illumination-correction.md)
- [Alignment Workflow](alignment.md)
- [Preprocessing Workflow](preprocessing.md)

Each module guide assumes you have already completed these setup steps.
