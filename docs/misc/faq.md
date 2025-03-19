# Frequently Asked Questions

This page addresses common questions and issues when using StarryNight.

## General Questions

### What is StarryNight?

StarryNight is a comprehensive platform for processing, analyzing, and managing optical pooled screening (OPS) image data, with particular focus on Cell Painting and sequencing-based assays.

### What programming languages does StarryNight use?

StarryNight is primarily built with:

- Python for the core algorithms and backend
- TypeScript/React for the Canvas UI
- Nix for environment management

### Is StarryNight open source?

Yes, StarryNight is open source under the MIT license. You can find the source code at [github.com/broadinstitute/starrynight](https://github.com/broadinstitute/starrynight).

## Installation

### Why is Nix recommended for installation?

Nix provides a reproducible environment that ensures all dependencies (including CellProfiler and other tools) are available with the correct versions. This eliminates common environment issues.

### Can I use StarryNight without Nix?

Yes, you can install StarryNight using a standard Python virtual environment, but you'll need to manually install dependencies like CellProfiler.

### How do I upgrade StarryNight?

To upgrade StarryNight to the latest version:

```bash
# Using Nix
git pull
nix develop --extra-experimental-features nix-command --extra-experimental-features flakes

# Using pip
git pull
pip install -e ".[dev]"
pip install -e starrynight/
pip install -e pipecraft/
pip install -e conductor/
```

## Usage

### How do I process my own data?

1. Organize your data with a consistent file structure
2. Generate an inventory and index
3. Run the appropriate processing modules
4. See the [Quick Start Guide](../getting-started/quickstart.md) for details

### What file formats does StarryNight support?

StarryNight supports most common microscopy image formats including:

- TIFF (.tiff, .tif)
- OME-TIFF (.ome.tiff)
- JPEG (.jpg, .jpeg)
- PNG (.png)

### Can StarryNight work with large datasets?

Yes, StarryNight is designed to handle large datasets efficiently:

- Parallel processing for inventory creation
- Parquet files for efficient data storage
- Scalable execution on clusters or cloud

### How do I integrate StarryNight with AWS?

StarryNight supports AWS integration for storage and computation:

1. Configure AWS credentials
2. Use S3 buckets for data storage
3. Optionally use AWS Batch for processing

See the Canvas UI guide for details.

## Troubleshooting

### CellProfiler is not found

If you see errors about CellProfiler not being found:

1. Using Nix: Ensure you're in the Nix environment
   ```bash
   nix develop --extra-experimental-features nix-command --extra-experimental-features flakes
   ```

2. Manual installation: Install CellProfiler
   ```bash
   pip install cellprofiler
   ```

3. Set the path explicitly:
   ```bash
   export STARRYNIGHT_CELLPROFILER_PATH=/path/to/cellprofiler
   ```

### Out of memory errors during processing

If you see out of memory errors:

1. Reduce the memory usage:
   ```bash
   starrynight cp -p /path/to/pipeline -l /path/to/loaddata -o /path/to/output --memory-limit 1024
   ```

2. Process in smaller batches

### Issues with file naming

If you see errors about file parsing:

1. Check your file naming convention
2. Use a custom parser if needed
3. Ensure there are no hidden files (like .DS_Store)

### Canvas UI not connecting

If the Canvas UI can't connect to Conductor:

1. Ensure Conductor is running (`conductor status`)
2. Check that you're using the correct port (default: 8000)
3. Verify network connectivity (especially in Docker)

## Development

### How do I contribute to StarryNight?

See the [Developer Guide](../developer/developer-guide.md) for details on:

- Setting up a development environment
- Understanding the codebase
- Contributing code

### Where do I report bugs?

Report bugs on the [GitHub issue tracker](https://github.com/broadinstitute/starrynight/issues).

### How do I add a new processing module?

See the "Adding a New Module" section in the [Developer Guide](../developer/developer-guide.md).

## Getting Help

### How do I get help with StarryNight?

- Check the documentation
- Post on the GitHub issues
