# Inventory and Index in StarryNight

Inventory and Index are foundational concepts in StarryNight that enable efficient organization and processing of large microscopy datasets. This document explains what they are, how they're created, and how they're used throughout the system.

## The Inventory

### What is the Inventory?

The Inventory is a comprehensive catalog of all files in a dataset. It serves as the first step in organizing your data for processing.

- It records the paths to every file in your dataset
- It captures basic file metadata (file size, modification time, etc.)
- It provides a unified view of potentially distributed data

### Why Create an Inventory?

Creating an inventory serves several purposes:

1. **Discovery**: Find all relevant files across potentially complex directory structures
2. **Performance**: Avoid repetitive filesystem traversals during processing
3. **Persistence**: Create a stable reference to files that won't change during processing
4. **Distribution**: Enable parallel processing by sharding the inventory

### Inventory Format

The inventory is stored as a Parquet file containing file paths and basic metadata. The main file is `inventory.parquet`, with additional shard files stored in the `inv/` subdirectory.

### Creating an Inventory

The inventory is typically created using the CLI:

```bash
starrynight inventory gen -d /path/to/dataset -o /path/to/workspace/inventory
```

Or through the web UI when creating a new project.

## The Index

### What is the Index?

The Index is a structured database of metadata extracted from the files in your inventory. It:

- Parses filenames to extract experimental metadata
- Organizes files by plate, well, site, channel, etc.
- Creates a queryable structure for finding specific images

The index is central to StarryNight's ability to process files in a context-aware manner.

### Key Information in the Index

The index typically contains:

- **Dataset Structure**: Batch, plate, well, and site identifiers
- **Image Metadata**: Channels, magnification, cycle information
- **File Details**: Original filename, format, path
- **Relationships**: How files relate to each other in the experimental design

### Index Format

The index is stored as a Parquet file (`index.parquet`) containing structured records with standardized fields. For example:

```
key = path/to/image.tiff
prefix = /absolute/path
dataset_id = experiment-123
batch_id = Batch1
plate_id = Plate1
well_id = A2
site_id = 1025
channel_dict = [PhalloAF750, ZO1-AF488, DAPI]
```

### Creating an Index

The index is generated from an inventory:

```bash
starrynight index gen -i /path/to/inventory/inventory.parquet -o /path/to/workspace/index
```

## Using Inventory and Index in Workflows

### In the CLI

Most StarryNight CLI commands accept an index file as input:

```bash
starrynight illum calc loaddata -i /path/to/index/index.parquet -o /path/to/output
```

### In the Web UI

In the web interface, inventory and index generation happens automatically when creating a project. The system then uses these to:

- Show project statistics
- Enable file browsing
- Configure processing modules
- Provide filtering and selection options

### In Custom Scripts

You can also use the inventory and index in custom Python scripts:

```python
import pandas as pd

# Load the index
index = pd.read_parquet('path/to/index/index.parquet')

# Filter for specific wells or plates
plate1_images = index[index.plate_id == 'Plate1']
```

## Parsers and Customization

StarryNight includes parsers for common naming conventions, but you can also customize how filenames are parsed:

- The Vincent parser handles standard Cell Painting naming conventions
- Custom parsers can be added for specialized naming schemes
- Parser configuration is usually done at project creation time

## Best Practices

- Keep inventory and index in a dedicated workspace directory
- Regenerate both if your dataset changes significantly
- Use the index to verify your dataset is complete before processing
- Query the index to understand your dataset structure

## Next Steps

- Learn about [Projects](projects.md)
- Explore [Modules and Pipelines](modules-pipelines.md)
- Try the [CLI Workflow examples](../user/cli-workflows/illumination-correction.md)
