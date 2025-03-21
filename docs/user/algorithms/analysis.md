# Analysis (analysis.py)

Implements a comprehensive analysis pipeline for microscopy images that integrates quality control, segmentation, feature extraction, and barcode calling to enable detailed phenotypic analysis of optical pooled screening experiments.

## Key Components

- **Multi-modality Integration**: Combines Cell Painting (CP) and sequential-based screening (SBS) images in a unified analysis pipeline
- **Multi-scale Feature Extraction**: Analyzes at subcellular (spots), cellular (nuclei, cells), and multicellular (neighborhoods, confluent regions) scales
- **Comprehensive Cell Profiling**: Extracts over 500 features covering intensity, morphology, texture, and spatial relationships

### CellProfiler Configuration

Key CellProfiler modules and configurations:

- **IdentifyPrimaryObjects**: Detects nuclei (10-80 pixels) and barcode spots (2-10 pixels)
- **IdentifySecondaryObjects**: Uses propagation with Otsu three-class thresholding for cell detection
- **MeasureObjectIntensity/Texture/Granularity**: Captures diverse cellular phenotypic features
- **MeasureObjectNeighbors**: Quantifies spatial relationships between cells
- **Custom Modules**: Uses `CallBarcodes` and `CompensateColors` for calling barcodes

## Implementation Notes

- **Quality Control Integration**: Embeds multiple quality checkpoints throughout the pipeline including alignment verification
- **Data Organization**: Processes data by batch/plate with channels and cycles from both CP and SBS modalities
- **Computational Optimization**: Employs downsampling and memory management for large datasets
