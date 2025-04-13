# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# CellProfiler Pipeline Asset Guidelines

## Commands
- Generate pipeline graphs: `python /path/to/cp_graph.py input.json output.dot --rank-nodes --remove-unused-data`
- Render graphs: `dot -Gdpi=50 -Tpng input.dot -o output.png` or `dot -Tsvg input.dot -o output.svg`
- Lint Python: `ruff scripts/*.py`

## Code Style
### Python
- Follow PEP 8 style with snake_case variables/functions
- Imports order: stdlib → third-party → local (grouped with blank lines)
- Type annotations for function parameters and returns
- 4-space indentation, 80 character line limit
- Comprehensive docstrings with parameter descriptions
- Use consistent error handling with descriptive messages

### Pipeline Files
- Document pipeline modifications in commit messages
- Maintain consistent module naming across related pipelines
- Include version and modification info in pipeline metadata
- Reference source of original pipelines in documentation

## PCPIP Pipeline Architecture

### Pipeline Structure
- PCPIP processes microscopy images through two parallel tracks then combines them:
  - Cell Painting Track (Pipelines 1-4): Using DNA, Phalloidin, ZO1 channels for morphology
  - Barcoding Track (Pipelines 5-8): Using DAPI, A, C, G, T channels for genetic barcodes
  - Combined Analysis (Pipeline 9): Integrates both for phenotype-genotype relationships

### Key Pipeline Functions
1. **Pipeline 1 (CP_Illum)**: Calculates illumination correction for Cell Painting channels
   - Downsamples images → Calculates correction functions → Upsamples to original size
   - Outputs .npy files with illumination patterns for each channel

2. **Pipeline 2 (CP_Apply_Illum)**: Applies illumination correction and segments cells
   - Corrects using division method → Identifies nuclei and cells → Creates masks
   - Outputs corrected images and segmentation parameters

3. **Pipeline 3 (CP_SegmentationCheck)**: Verifies segmentation quality
   - Applies segmentation using thresholds from Pipeline 2
   - Creates overlay images for quality control visualization

4. **Pipeline 5 (BC_Illum)**: Calculates illumination correction for barcoding channels
   - Similar to Pipeline 1 but works with cycle-specific barcode channels
   - Processes DAPI, A, T, G, C illumination patterns for multiple cycles

5. **Pipeline 6 (BC_Apply_Illum)**: Applies correction to barcoding images
   - Applies cycle-specific illumination correction
   - Aligns DAPI across cycles, shifting A, C, G, T by same amount

6. **Pipeline 7 (BC_Preprocess)**: Processes barcoding images for barcode calling
   - Performs color compensation to correct spectral bleed-through
   - Identifies potential barcode foci in each channel
   - Analyzes foci intensities and calls barcodes

7. **Pipeline 9 (Analysis)**: Integrates Cell Painting and barcoding data
   - Aligns Cell Painting images to barcoding images
   - Segments nuclei, cells, cytoplasm in Cell Painting images
   - Measures morphological features and calls barcodes
   - Relates cellular features to genetic barcodes

### Image Naming Conventions
- **Original Images**: Prefix "Orig" (OrigDNA, OrigPhalloidin, OrigA, etc.)
- **Illumination Functions**: Prefix "Illum" (IllumDNA, IllumA, etc.)
- **Corrected Images**: Prefix "Corr" or no prefix (CorrDNA or DNA)
- **Barcoding Cycles**: Numbered prefixes (Cycle01_DAPI, Cycle02_A, etc.)
- **Output Files**: Include metadata (Plate_{Plate}_Well_{Well}_Site_{Site}_*.tiff)

### Configuration System
- LoadData module reads CSV files with experiment-specific metadata
- Metadata columns control image grouping (Plate, Well, Site, Cycle)
- Channel Dictionary maps microscope channels to biological stains
- Pipeline selection based on experiment type (standard vs. SABER)
